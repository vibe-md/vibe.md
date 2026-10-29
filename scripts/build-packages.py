#!/usr/bin/env python3
"""Build reproducible ZIP downloads and a catalog from vibe.md skill packages.

    python3 scripts/build-packages.py --all --output-dir dist/downloads
    python3 scripts/build-packages.py --group gitly --output-dir dist/downloads
    python3 scripts/build-packages.py --verify dist/downloads

A package is any directory under skills/ that holds skills; a standalone skill is a package of one. Packages are
discovered from the source tree, so a new package needs no change here. The
catalog (catalog.json) lists every package, its skills, and its archives with
checksums, all for one source revision.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from categories import infer_categories

ROOT = Path(__file__).resolve().parent.parent
AGENTS = {
    "claude-code": ("Claude Code", ".claude/skills"),
    "codex": ("Codex", ".agents/skills"),
    "cursor": ("Cursor", ".cursor/skills"),
    "gemini": ("Gemini CLI", ".gemini/skills"),
    "copilot": ("GitHub Copilot", ".github/skills"),
}


def build_packages(skills_dir, group, output_dir, ref):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", group) or len(group) > 64:
        raise ValueError("group names must be lowercase kebab-case, up to 64 characters")
    group_dir = skills_dir / group
    if not group_dir.is_dir():
        raise ValueError("package not found: " + group)
    # A standalone skill (skills/<name>/SKILL.md) is published as a package of one skill.
    standalone = (group_dir / "SKILL.md").is_file()
    if standalone:
        sources = [group_dir / "SKILL.md"] + sorted((skills_dir / "_shared").glob("*/SKILL.md"))
    else:
        sources = sorted(group_dir.glob("*/SKILL.md")) + sorted((skills_dir / "_shared").glob("*/SKILL.md"))
        if not any(path.parent.parent == group_dir for path in sources):
            raise ValueError("group contains no skills: " + group)
    payload = {}
    modes = {}
    names = set()
    for entry in sources:
        skill = entry.parent
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill.name) or len(skill.name) > 64:
            raise ValueError("invalid skill name: " + skill.name)
        if skill.name in names:
            raise ValueError("duplicate skill name: " + skill.name)
        names.add(skill.name)
        if skill.is_symlink() or skill.parent.is_symlink():
            raise ValueError("symbolic links are not allowed: " + str(skill))
        for path in sorted(skill.rglob("*")):
            if path.is_symlink():
                raise ValueError("symbolic links are not allowed: " + str(path))
            if path.is_file():
                name = "skills/" + skill.name + "/" + path.relative_to(skill).as_posix()
                data = path.read_bytes()
                if path == entry and skill.parent == group_dir:
                    data = subprocess.run(
                        ["bash", "-c", 'source "$1"; rewrite_group_links "$2" "$3"',
                         "vibe-md-rewrite", str(ROOT / "scripts/install.sh"), str(path), group],
                        check=True, stdout=subprocess.PIPE,
                    ).stdout
                payload[name] = data
                modes[name] = 0o755 if path.stat().st_mode & 0o111 else 0o644

    resources = [] if standalone else [path for path in sorted(group_dir.iterdir()) if not path.name.startswith(".")
                                       and (path.suffix == ".md" or path.name == "LICENSE")]
    if resources and group in names:
        raise ValueError("group resources conflict with a skill of the same name: " + group)
    for path in resources:
        if path.is_symlink() or not path.is_file():
            raise ValueError("group resources must be regular files, without symbolic links: " + str(path))
        payload["skills/" + group + "/" + path.name] = path.read_bytes()

    output_dir.mkdir(parents=True, exist_ok=True)
    root = group + "-install"
    inventory = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payload.items())}
    manifest = {
        "group": group,
        "source_repository": "vibe-md/vibe.md",
        "source_ref": ref,
        "skills": sorted(names),
        "agents": {},
    }
    resources_clause = "including the group resources directory `{destination}/" + group + "/` when present" if not standalone \
        else "(this package has no group resources directory)"
    for agent, (label, destination) in AGENTS.items():
        clause = resources_clause.replace("{destination}", destination)
        guide = f"""# Install {group} from vibe.md for {label}

This package targets {label}. Stop if the currently open agent does not match.
Install only in the user's currently open project, never in this extracted folder.
The user's request to install this package authorizes copying missing files.

1. Read MANIFEST.json beside this file. Verify that the complete package contains
   exactly its listed skills and files, with matching SHA-256 hashes and no
   symbolic links. Required skills: {', '.join(sorted(names))}.
2. Inspect ALL destination directories at `{destination}/<directory>/` first,
   {clause}.
   Classify each complete directory as missing, byte-for-byte identical, or
   conflicting, including any extra destination files. If any directory conflicts,
   stop before writing anything and ask the user how to handle it. Preserve all
   unrelated skills and project files. Never overwrite a conflicting directory.
3. When every destination is missing or identical, create missing directories and
   copy the complete contents of each directory under `skills/` into its destination.
   Do not ask for another confirmation and do not rewrite identical directories.
   This includes the shared vibe router and the group's shared documents and license.
4. Verify every installed file against MANIFEST.json. Do not run bundled scripts,
   change Git history, authenticate, or edit AGENTS.md, CLAUDE.md, or preferences.
5. Report the installed skills. Remove only temporary extraction files you created;
   preserve the downloaded ZIP and any user-created extracted folder.
6. Tell the user to reload {label}, then ask for their desired workflow in ordinary
   language. Individual skills can also be
   invoked directly; the vibe router helps choose among installed workflows.

Follow each skill's documented prerequisites. Installing skills does not install
their tools, execute their workflows, or change existing project preferences.
"""
        package_manifest = {
            "group": group, "agent": agent, "destination": destination,
            "source_repository": manifest["source_repository"], "source_ref": ref,
            "skills": sorted(names), "files": inventory,
        }
        files = dict(payload)
        files["INSTALL.md"] = guide.encode()
        files["MANIFEST.json"] = (json.dumps(package_manifest, indent=2, sort_keys=True) + "\n").encode()
        filename = group + "-" + agent + ".zip"
        target = output_dir / filename
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(root + "/" + name, (2026, 1, 1, 0, 0, 0))
                info.external_attr = (stat.S_IFREG | modes.get(name, 0o644)) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
        manifest["agents"][agent] = {
            "name": label, "skills_dir": destination, "archive": filename,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }
    (output_dir / (group + "-manifest.json")).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def read_frontmatter(path):
    """Return (mapping, body) for a Markdown file with optional YAML frontmatter."""
    try:
        import yaml
    except ImportError:
        raise ValueError("PyYAML is required: python3 -m pip install -r requirements-dev.txt")
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    try:
        data = yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError as error:
        problem = getattr(error, "problem", None) or str(error).splitlines()[0]
        raise ValueError("invalid YAML frontmatter in {}: {}".format(path, problem))
    return (data if isinstance(data, dict) else {}), text[end + 4:]


def first_paragraph(markdown):
    """The first paragraph of prose, skipping headings, lists, and code."""
    lines, in_code = [], False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or stripped.startswith(("#", "-", "*", ">", "|", "<", "[!")):
            if lines:
                break
            continue
        if not stripped:
            if lines:
                break
            continue
        lines.append(stripped)
    return " ".join(lines)


def discover_packages(skills_dir):
    """Package ids: every group of skills under skills/, and every standalone skill (a package of one)."""
    packages = []
    for entry in sorted(skills_dir.iterdir()):
        if entry.name.startswith(".") or entry.name == "_shared" or not entry.is_dir():
            continue
        if (entry / "SKILL.md").is_file() or any((child / "SKILL.md").is_file() for child in entry.iterdir() if child.is_dir()):
            packages.append(entry.name)
    return packages


def standalone_metadata(data):
    """The optional package fields of a standalone skill, from 'metadata' in its frontmatter.
    The validator checks them; maintainers are one comma-separated string there."""
    raw = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    maintainers = raw.get("maintainers")
    return {
        "title": raw.get("title"),
        "category": raw.get("category"),
        "categories": raw.get("categories"),
        "maintainers": maintainers.replace(",", " ").split() if isinstance(maintainers, str) else [],
    }


def describe_package(skills_dir, group, artifacts):
    """One catalog entry. Everything is derived from the source tree except optional metadata:
    a group's README frontmatter, or a standalone skill's 'metadata'."""
    group_dir = skills_dir / group
    standalone = (group_dir / "SKILL.md").is_file()
    if standalone:
        data, _ = read_frontmatter(group_dir / "SKILL.md")
        description = " ".join(str(data.get("description", "")).split())
        meta, body, readme = standalone_metadata(data), description, None
        skills = [{"name": group, "description": description}]
    else:
        readme = group_dir / "README.md"
        meta, body = read_frontmatter(readme) if readme.is_file() else ({}, "")
        skills = []
        for entry in sorted(group_dir.glob("*/SKILL.md")):
            data, _ = read_frontmatter(entry)
            skills.append({"name": entry.parent.name, "description": " ".join(str(data.get("description", "")).split())})
    shared = sorted(entry.parent.name for entry in (skills_dir / "_shared").glob("*/SKILL.md"))
    package = {
        "id": group,
        "title": meta.get("title") or group.replace("-", " ").title(),
        "summary": meta.get("summary") or (body if standalone else first_paragraph(body)),
        "maintainers": list(meta.get("maintainers") or []),
        "skills": skills,
        "shared_skills": shared,
        "kind": "standalone" if standalone else "group",
        "documentation": "skills/{}/SKILL.md".format(group) if standalone else ("skills/{}/README.md".format(group) if readme.is_file() else None),
        "artifacts": artifacts,
    }
    if meta.get("category"):
        package["category"] = meta["category"]
    explicit = meta.get("categories")
    if explicit:
        package["categories"] = [value.strip() for value in explicit.split(",")]
    elif meta.get("category"):
        package["categories"] = [meta["category"]]
    else:
        package["categories"] = infer_categories(package["summary"])
    return package


def build_catalog(skills_dir, groups, output_dir, ref):
    """Build every package and a catalog.json describing them, all or nothing.

    Output is assembled in a temporary directory beside output_dir and moved
    into place only after every package built, so a failure never leaves a
    partial or inconsistent set of files behind.
    """
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".catalog-", dir=str(output_dir.parent)))
    try:
        packages = []
        for group in groups:
            manifest = build_packages(skills_dir, group, staging, ref)
            artifacts = {
                agent: {"file": info["archive"], "sha256": info["sha256"]}
                for agent, info in sorted(manifest["agents"].items())
            }
            packages.append(describe_package(skills_dir, group, artifacts))
        catalog = {
            "schema_version": 1,
            "source_repository": "vibe-md/vibe.md",
            "source_ref": ref,
            "agents": {agent: {"name": label, "skills_dir": destination} for agent, (label, destination) in AGENTS.items()},
            "packages": packages,
        }
        (staging / "catalog.json").write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        errors = verify_catalog(staging, skills_dir)
        if errors:
            raise ValueError("catalog is inconsistent:\n  " + "\n  ".join(errors))
        output_dir.mkdir(parents=True, exist_ok=True)
        for item in sorted(staging.iterdir()):
            os.replace(str(item), str(output_dir / item.name))
        return catalog
    finally:
        shutil.rmtree(str(staging), ignore_errors=True)


def verify_catalog(directory, skills_dir=None):
    """Check that catalog.json, the manifests, and the archives describe the same files."""
    directory = Path(directory)
    errors = []
    try:
        catalog = json.loads((directory / "catalog.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return ["catalog.json could not be read: {}".format(error)]
    if catalog.get("schema_version") != 1:
        errors.append("unsupported catalog schema_version: {!r}".format(catalog.get("schema_version")))
    for package in catalog.get("packages", []):
        group = package["id"]
        try:
            manifest = json.loads((directory / (group + "-manifest.json")).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            errors.append("{}: manifest could not be read: {}".format(group, error))
            continue
        if manifest.get("source_ref") != catalog.get("source_ref"):
            errors.append("{}: manifest and catalog disagree about the source revision".format(group))
        listed = sorted(skill["name"] for skill in package["skills"])
        if sorted(listed + list(package["shared_skills"])) != sorted(manifest["skills"]):
            errors.append("{}: catalog skills do not match the manifest".format(group))
        if sorted(package["artifacts"]) != sorted(manifest["agents"]):
            errors.append("{}: catalog and manifest list different agents".format(group))
        for agent, artifact in package["artifacts"].items():
            archive = directory / artifact["file"]
            if not archive.is_file():
                errors.append("{}: missing archive {}".format(group, artifact["file"]))
            elif hashlib.sha256(archive.read_bytes()).hexdigest() != artifact["sha256"]:
                errors.append("{}: checksum mismatch for {}".format(group, artifact["file"]))
            if manifest["agents"].get(agent, {}).get("sha256") != artifact["sha256"]:
                errors.append("{}: manifest and catalog disagree about {}".format(group, artifact["file"]))
        if skills_dir is not None:
            if (Path(skills_dir) / group / "SKILL.md").is_file():
                source = [group]
            else:
                source = sorted(path.parent.name for path in (Path(skills_dir) / group).glob("*/SKILL.md"))
            if source != listed:
                errors.append("{}: catalog skills {} differ from the source {}".format(group, listed, source))
    expected = {"catalog.json"}
    for package in catalog.get("packages", []):
        expected.add(package["id"] + "-manifest.json")
        expected.update(artifact["file"] for artifact in package["artifacts"].values())
    for entry in sorted(directory.iterdir()):
        if entry.name not in expected:
            errors.append("unlisted file in the output directory: {}".format(entry.name))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", action="append", help="package to build; repeat to build several")
    parser.add_argument("--all", action="store_true", help="build every package found under skills/")
    parser.add_argument("--skills-dir", type=Path, default=ROOT / "skills")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist/downloads")
    parser.add_argument("--ref", help="Published source commit used by terminal installation")
    parser.add_argument("--verify", type=Path, metavar="DIR",
                        help="check an existing output directory against its catalog and the source, then exit")
    args = parser.parse_args()
    if args.verify:
        errors = verify_catalog(args.verify, args.skills_dir)
        for error in errors:
            print("error: " + error)
        print("Catalog verified." if not errors else "Catalog verification failed.")
        raise SystemExit(1 if errors else 0)
    if bool(args.group) == args.all:
        parser.error("choose --group <name> (repeatable) or --all")
    ref = args.ref
    if not ref:
        ref = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    try:
        groups = discover_packages(args.skills_dir) if args.all else args.group
        if not groups:
            parser.error("no packages found in " + str(args.skills_dir))
        catalog = build_catalog(args.skills_dir, groups, args.output_dir, ref)
    except ValueError as error:
        parser.error(str(error))
    count = sum(len(package["skills"]) for package in catalog["packages"])
    print("Built {} package(s) with {} skills for {} agents in {}".format(
        len(catalog["packages"]), count, len(AGENTS), args.output_dir))


if __name__ == "__main__":
    main()
