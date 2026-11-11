#!/usr/bin/env python3
"""Validate every skill in the vibe.md collection.

Usage:
    python3 scripts/validate-skills.py [--skills-dir PATH]

Skills can live directly under skills/ or one level down in a group.
Skills are discovered automatically; nothing here knows about any particular
skill. An empty collection is valid.

Exit codes: 0 = all skills valid, 1 = validation errors, 2 = usage or setup error.
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised manually
    sys.stderr.write(
        "error: PyYAML is required to validate skills.\n"
        "       Install it with: python3 -m pip install -r requirements-dev.txt\n"
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILLS_DIR = REPO_ROOT / "skills"

# Limits from the Agent Skills specification: https://agentskills.io/specification
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX_LENGTH = 64
DESCRIPTION_MIN_LENGTH = 20  # vibe.md policy: descriptions must say something useful
DESCRIPTION_MAX_LENGTH = 1024
COMPATIBILITY_MAX_LENGTH = 500
RECOMMENDED_MAX_LINES = 500

# Files allowed directly inside skills/ that are not skills themselves.
COLLECTION_FILES = {"README.md"}

# Markdown links and images: [text](target) or ![alt](target "title")
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFERENCE_PATTERN = re.compile(r"^[ \t]*\[[^\]]+\]:[ \t]*<?([^\s>]+)>?")
FENCE_PATTERN = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
URL_SCHEME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


class Report:
    """Collects errors and warnings for one validation run."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, message):
        self.errors.append((path, message))

    def warning(self, path, message):
        self.warnings.append((path, message))


def display_path(path):
    """Show paths relative to the current directory when possible."""
    try:
        relative = os.path.relpath(str(path))
    except ValueError:  # different drive on Windows
        return str(path)
    return str(path) if relative.startswith("..") else relative


def split_frontmatter(text):
    """Return (frontmatter_text, body) or raise ValueError with a helpful message."""
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(
            "SKILL.md must start with YAML frontmatter. The very first line must be '---'."
        )
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    raise ValueError("YAML frontmatter is not closed. Add a line containing only '---' after it.")


def iter_markdown_links(body):
    """Yield (line_number, target) for links outside code blocks and inline code."""
    fence = None
    for number, line in enumerate(body.splitlines(), start=1):
        marker = FENCE_PATTERN.match(line)
        if marker:
            token, suffix = marker.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence is not None:
            continue
        # Replace code spans with spaces so removal cannot join unrelated text.
        def hide_code(match):
            return " " * len(match.group(0))
        line = re.sub(r"(`+)(?!`)(.*?)(?<!`)\1(?!`)", hide_code, line)
        reference = REFERENCE_PATTERN.match(line)
        if reference:
            yield number, reference.group(1)
        for match in LINK_PATTERN.finditer(line):
            yield number, match.group(1)


def check_links(skill_dir, skill_md, body, body_offset, report, group_dir=None):
    """Allow local resources and top-level documents shared by a skill group."""
    skill_root = skill_dir.resolve()
    for line_number, target in iter_markdown_links(body):
        if target.startswith("#") or URL_SCHEME_PATTERN.match(target) or target.startswith("//"):
            continue  # anchors and external URLs are not checked
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        location = "{}:{}".format(display_path(skill_md), line_number + body_offset)
        if path_part.startswith("/") or path_part.startswith("\\"):
            report.error(
                location,
                "link '{}' uses an absolute path. Use a path relative to the skill "
                "directory, for example 'references/guide.md'.".format(target),
            )
            continue
        resolved = (skill_dir / path_part).resolve()
        try:
            resolved.relative_to(skill_root)
        except ValueError:
            shared_document = (
                group_dir is not None
                and re.fullmatch(r"\.\./[^./\\][^/\\]*", path_part)
                and resolved.parent == group_dir.resolve()
                and (resolved.suffix == ".md" or resolved.name == "LICENSE")
            )
            if shared_document:
                if not resolved.is_file():
                    report.error(location, "link '{}' points to a file that does not exist.".format(target))
                continue
            report.error(
                location,
                "link '{}' points outside the skill directory. Skills are installed on "
                "their own, so keep every referenced file inside '{}/'.".format(
                    target, skill_dir.name
                ),
            )
            continue
        if not resolved.exists():
            report.error(
                location,
                "link '{}' points to a file that does not exist. Add the file or fix "
                "the link.".format(target),
            )


def check_symlinks(skill_dir, report):
    """Symlinks are rejected: they can point outside the skill or break when copied."""
    for root, dirs, files in os.walk(str(skill_dir)):
        for entry in dirs + files:
            path = Path(root) / entry
            if path.is_symlink():
                report.error(
                    display_path(path),
                    "symbolic links are not allowed in skills. Replace the link with a "
                    "regular file.",
                )


def check_frontmatter(skill_dir, skill_md, data, report):
    """Validate frontmatter fields. Returns the skill name if it is usable."""
    where = display_path(skill_md)
    if not isinstance(data, dict):
        report.error(where, "YAML frontmatter must be a mapping of 'key: value' pairs.")
        return None

    name = data.get("name")
    if name is None:
        report.error(where, "missing required field 'name'. Add 'name: {}'.".format(skill_dir.name))
        name = None
    elif not isinstance(name, str) or not name.strip():
        report.error(where, "'name' must be a non-empty string.")
        name = None
    else:
        if len(name) > NAME_MAX_LENGTH:
            report.error(
                where,
                "'name' is {} characters long; the maximum is {}.".format(len(name), NAME_MAX_LENGTH),
            )
        if not NAME_PATTERN.match(name):
            report.error(
                where,
                "'name: {}' is not lowercase kebab-case. Use only a-z, 0-9 and single "
                "hyphens, with no leading or trailing hyphen (for example 'git-workflow').".format(
                    name
                ),
            )
        if name != skill_dir.name:
            report.error(
                where,
                "'name: {}' does not match the directory name '{}'. Rename one so they "
                "are identical.".format(name, skill_dir.name),
            )

    description = data.get("description")
    if description is None:
        report.error(
            where,
            "missing required field 'description'. Describe what the skill does and "
            "when an agent should use it.",
        )
    elif not isinstance(description, str) or not description.strip():
        report.error(where, "'description' must be a non-empty string.")
    else:
        length = len(description.strip())
        if length < DESCRIPTION_MIN_LENGTH:
            report.error(
                where,
                "'description' is too short ({} characters). Explain what the skill does "
                "and when to use it in at least {} characters.".format(length, DESCRIPTION_MIN_LENGTH),
            )
        elif length > DESCRIPTION_MAX_LENGTH:
            report.error(
                where,
                "'description' is {} characters long; the maximum is {}.".format(
                    length, DESCRIPTION_MAX_LENGTH
                ),
            )

    # Optional fields from the Agent Skills specification: check types only.
    if "license" in data and not isinstance(data["license"], str):
        report.error(where, "'license' must be a string, for example 'MIT'.")
    if "compatibility" in data:
        value = data["compatibility"]
        if not isinstance(value, str) or not value.strip():
            report.error(where, "'compatibility' must be a non-empty string.")
        elif len(value) > COMPATIBILITY_MAX_LENGTH:
            report.error(
                where,
                "'compatibility' is {} characters long; the maximum is {}.".format(
                    len(value), COMPATIBILITY_MAX_LENGTH
                ),
            )
    if "metadata" in data and not isinstance(data["metadata"], dict):
        report.error(where, "'metadata' must be a mapping of keys to values.")
    if "allowed-tools" in data and not isinstance(data["allowed-tools"], str):
        report.error(where, "'allowed-tools' must be a space-separated string.")

    return name if isinstance(name, str) else None


# Content safety limits. These catch honest mistakes and obvious problems. They do
# not replace a maintainer reading what a skill tells an agent to do.
FILE_SIZE_WARN = 256 * 1024
FILE_SIZE_MAX = 1024 * 1024
BINARY_ALLOWED_DIRS = {"assets"}
SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"), "a private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key id"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "a GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"), "a GitHub token"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"), "a Slack token"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b"), "an API key"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "a Google API key"),
]
SUSPICIOUS_PATTERNS = [
    (re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b"), "pipes a download into a shell"),
    (re.compile(r"\bbase64\s+(?:-d|--decode)\b[^\n]*\|\s*(?:ba)?sh\b"), "decodes content into a shell"),
    (re.compile(r"\beval\s+\"?\$\("), "evaluates generated shell code"),
    (re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(?:/|~|\$HOME)(?:\s|$)"), "recursively removes a system or home directory"),
]
PACKAGE_METADATA_KEYS = {"title", "summary", "category", "categories", "maintainers"}
from categories import CATEGORIES
# Keep package text short enough to fit a catalog card; the website enforces looser limits as a backstop.
PACKAGE_TEXT_LIMITS = {"title": 80, "summary": 400, "category": 40}
MAX_MAINTAINERS = 10
CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
MAINTAINER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def check_secrets(content, where, report):
    for pattern, label in SECRET_PATTERNS:
        if pattern.search(content):
            report.error(where, "looks like it contains {}. Remove it and rotate the credential.".format(label))
            return


def check_document(path, report):
    """Size, encoding, and secret checks for a distributed document outside any skill
    (a package README, LICENSE, or other Markdown). These files are packaged into every download."""
    if path.is_symlink() or not path.is_file():
        return
    where = display_path(path)
    size = path.stat().st_size
    if size > FILE_SIZE_MAX:
        report.error(where, "file is {} KiB; the limit is {} KiB. Link to large files instead.".format(
            size // 1024, FILE_SIZE_MAX // 1024))
        return
    if size > FILE_SIZE_WARN:
        report.warning(where, "file is {} KiB. Consider splitting or linking to it.".format(size // 1024))
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report.error(where, "documents must be UTF-8 encoded text.")
        return
    check_secrets(content, where, report)


def check_content_safety(skill_dir, report):
    """File size, file type, executable, secret, and suspicious-content checks for one skill."""
    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        where = display_path(path)
        relative = path.relative_to(skill_dir)
        size = path.stat().st_size
        if size > FILE_SIZE_MAX:
            report.error(where, "file is {} KiB; the limit is {} KiB. Link to large files instead.".format(
                size // 1024, FILE_SIZE_MAX // 1024))
            continue
        if size > FILE_SIZE_WARN:
            report.warning(where, "file is {} KiB. Large files are loaded into the agent's context.".format(size // 1024))
        with open(str(path), "rb") as handle:
            head = handle.read(8192)
        is_text = b"\0" not in head
        top = relative.parts[0] if len(relative.parts) > 1 else ""
        if not is_text and top not in BINARY_ALLOWED_DIRS:
            report.error(where, "binary files are only allowed under assets/.")
            continue
        if path.stat().st_mode & 0o111 and top != "scripts":
            report.warning(where, "file is executable outside scripts/. Remove the executable bit unless it is a script.")
        if top == "scripts":
            report.warning(where, "bundled script: maintainers must review what it does before merging.")
        if not is_text:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            report.error(where, "text files must be UTF-8 encoded.")
            continue
        check_secrets(content, where, report)
        for pattern, label in SUSPICIOUS_PATTERNS:
            if pattern.search(content):
                report.warning(where, "{}. Maintainers must confirm this is intended and documented.".format(label))


def check_package_metadata(group_dir, report):
    """Validate the optional frontmatter of skills/<package>/README.md."""
    readme = group_dir / "README.md"
    if not readme.is_file() or readme.is_symlink():
        report.error(display_path(group_dir), "a skill group needs a README.md whose frontmatter sets 'categories'.")
        return
    where = display_path(readme)
    try:
        text = readme.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report.error(where, "README.md must be UTF-8 encoded text.")
        return
    if not text.startswith("---"):
        report.error(where, "README.md needs frontmatter that sets 'categories'.")
        return
    try:
        frontmatter, _ = split_frontmatter(text)
        data = yaml.safe_load(frontmatter)
    except (ValueError, yaml.YAMLError) as exc:
        report.error(where, "package frontmatter is invalid: {}".format(str(exc).splitlines()[0]))
        return
    if not isinstance(data, dict):
        report.error(where, "package frontmatter must be a mapping of 'key: value' pairs.")
        return
    for key in sorted(set(data) - PACKAGE_METADATA_KEYS):
        report.error(where, "unknown package field '{}'. Allowed: {}.".format(key, ", ".join(sorted(PACKAGE_METADATA_KEYS))))
    check_package_text(where, data, PACKAGE_TEXT_LIMITS, report)
    check_categories(where, data, report)
    check_maintainers(where, data.get("maintainers", []), "'maintainers'", "a list of GitHub usernames", report)


def check_package_text(where, data, keys, report, prefix=""):
    """Length and plain-text rules for the package text fields that are present."""
    for key in keys:
        if key not in data:
            continue
        value, limit, name = data[key], PACKAGE_TEXT_LIMITS[key], "'{}{}'".format(prefix, key)
        if not isinstance(value, str) or not value.strip():
            report.error(where, "{} must be a non-empty string.".format(name))
        elif len(value) > limit:
            report.error(where, "{} is {} characters; the maximum is {}.".format(name, len(value), limit))
        elif CONTROL_CHARACTERS.search(value) or "\n" in value:
            report.error(where, "{} must be a single line of plain text.".format(name))


def check_maintainers(where, maintainers, name, shape, report):
    if not isinstance(maintainers, list) or not all(
        isinstance(item, str) and MAINTAINER_PATTERN.fullmatch(item) for item in maintainers
    ):
        report.error(where, "{} must be {}, without '@'.".format(name, shape))
    elif len(maintainers) > MAX_MAINTAINERS:
        report.error(where, "{} lists {} people; the maximum is {}.".format(name, len(maintainers), MAX_MAINTAINERS))


def check_categories(where, data, report):
    """Every package must choose its categories, so the website can list it where people look."""
    if "categories" not in data:
        report.error(where, "'categories' is required. Choose one to three from: {}.".format(", ".join(CATEGORIES)))
        return
    value = data["categories"]
    if value is None or (isinstance(value, str) and not value.strip()):
        report.error(where, "'categories' is empty. Choose one to three from: {}.".format(", ".join(CATEGORIES)))
        return
    if not isinstance(value, str):
        report.error(where, "'categories' must be a comma-separated string.")
        return
    items = [item.strip() for item in value.split(",")]
    if not 1 <= len(items) <= 3 or len(set(items)) != len(items) or any(item not in CATEGORIES for item in items):
        report.error(where, "'categories' must contain one to three distinct categories from: {}.".format(", ".join(CATEGORIES)))


def check_standalone_metadata(skill_md, data, report):
    """A standalone skill is a package of one. It describes itself under 'metadata' in its
    own frontmatter, using the same fields as a package README ('categories' is required):

        metadata:
          category: Security
          maintainers: octocat, hubot

    Agent Skills metadata values are strings, so the maintainers are one comma-separated string.
    The title and summary come from the name and description unless 'title' is set."""
    metadata = data.get("metadata") if isinstance(data, dict) else None
    where = display_path(skill_md)
    if not isinstance(metadata, dict):
        report.error(where, "add a 'metadata' block with 'categories' (and your GitHub username under 'maintainers').")
        return
    check_package_text(where, metadata, ("title", "category"), report, prefix="metadata.")
    check_categories(where, metadata, report)
    category = metadata.get("category")
    if isinstance(category, str) and category.strip() and category not in CATEGORIES:
        report.error(where, "'metadata.category' is '{}'. Use one of: {}.".format(category, ", ".join(CATEGORIES)))
    if "maintainers" in metadata:
        value = metadata["maintainers"]
        if isinstance(value, str):
            check_maintainers(where, value.replace(",", " ").split(), "'metadata.maintainers'",
                              "GitHub usernames separated by commas", report)
        else:
            report.error(where, "'metadata.maintainers' must be one string of GitHub usernames separated by "
                                "commas, for example 'octocat, hubot'.")


def validate_skill(skill_dir, report, group_dir=None, standalone=False):
    """Validate one skill directory. Returns its declared name, if any."""
    skill_md = skill_dir / "SKILL.md"
    # Compare names exactly: case-insensitive filesystems (macOS, Windows) would
    # accept 'skill.md' here, but Linux and the agents would not.
    names = os.listdir(str(skill_dir))
    if "SKILL.md" not in names or not skill_md.is_file():
        others = [n for n in names if n.lower() == "skill.md" and n != "SKILL.md"]
        hint = " Found '{}'; the file name must be exactly 'SKILL.md'.".format(others[0]) if others else ""
        report.error(display_path(skill_dir), "missing SKILL.md." + hint)
        return None

    check_symlinks(skill_dir, report)
    check_content_safety(skill_dir, report)

    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        report.error(display_path(skill_md), "SKILL.md must be UTF-8 encoded text.")
        return None

    try:
        frontmatter, body = split_frontmatter(text)
    except ValueError as exc:
        report.error(display_path(skill_md), str(exc))
        return None

    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        where = display_path(skill_md)
        mark = getattr(exc, "problem_mark", None)
        if mark is not None:
            where = "{}:{}".format(where, mark.line + 2)  # +1 for 1-based, +1 for opening '---'
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        report.error(
            where,
            "YAML frontmatter is invalid: {}. Tip: wrap values that contain ':' or start "
            "with '[', '{{' or '*' in quotes.".format(problem),
        )
        return None

    name = check_frontmatter(skill_dir, skill_md, data, report)
    if standalone:
        check_standalone_metadata(skill_md, data, report)

    if not body.strip():
        report.error(
            display_path(skill_md),
            "SKILL.md has no instructions after the frontmatter. Add the Markdown body.",
        )

    body_offset = len(frontmatter.splitlines()) + 2  # opening and closing '---' lines
    check_links(skill_dir, skill_md, body, body_offset, report, group_dir)

    line_count = len(text.splitlines())
    if line_count > RECOMMENDED_MAX_LINES:
        report.warning(
            display_path(skill_md),
            "SKILL.md has {} lines. Consider moving detail into references/ to keep it "
            "under {} lines.".format(line_count, RECOMMENDED_MAX_LINES),
        )
    return name


def validate_collection(skills_dir):
    """Validate every skill under skills_dir. Returns (report, skill_count)."""
    report = Report()
    entries = sorted(skills_dir.iterdir(), key=lambda p: p.name)
    skill_dirs = []
    standalone = set()
    groups = {}
    resource_groups = set()
    for entry in entries:
        if entry.name.startswith("."):
            continue
        if entry.is_symlink():
            report.error(display_path(entry), "symbolic links are not allowed in the skills directory.")
        elif entry.is_dir():
            is_group = not (entry / "SKILL.md").is_file() and (
                entry.name == "_shared" or any(
                    child.is_dir() and (child / "SKILL.md").is_file()
                    for child in entry.iterdir()
                )
            )
            if not is_group:
                skill_dirs.append(entry)
                standalone.add(entry)
                continue
            if entry.name != "_shared" and (
                not NAME_PATTERN.fullmatch(entry.name) or len(entry.name) > NAME_MAX_LENGTH
            ):
                report.error(display_path(entry), "group names must use lowercase kebab-case, up to 64 characters.")
            check_symlinks(entry, report)
            children = []
            for child in sorted(entry.iterdir(), key=lambda p: p.name):
                if child.name.startswith(".") or child.is_symlink():
                    continue
                if child.is_dir():
                    children.append(child)
                elif child.suffix != ".md" and child.name != "LICENSE":
                    report.error(display_path(child), "unexpected file in a skill group; use Markdown documentation or LICENSE.")
                else:
                    check_document(child, report)
            if not children:
                report.error(display_path(entry), "a skill group must contain at least one skill directory.")
            skill_dirs.extend(children)
            if entry.name != "_shared":
                check_package_metadata(entry, report)
                groups.update({child: entry for child in children})
                if any(child.is_file() and not child.name.startswith(".") for child in entry.iterdir()):
                    resource_groups.add(entry.name)
        elif entry.name in COLLECTION_FILES:
            check_document(entry, report)
        else:
            report.error(
                display_path(entry),
                "unexpected file. Each skill must be a directory, for example "
                "'skills/<skill-name>/SKILL.md'.",
            )

    seen = {}
    for skill_dir in skill_dirs:
        name = validate_skill(skill_dir, report, groups.get(skill_dir), skill_dir in standalone)
        if name is None:
            continue
        group = groups.get(skill_dir)
        if group is not None and not name.startswith(group.name + "-"):
            report.warning(
                display_path(skill_dir / "SKILL.md"),
                "skill names in the '{0}' package should start with '{0}-'. Installation flattens "
                "every package into one directory, so the prefix keeps names unique.".format(group.name),
            )
        if name in resource_groups:
            report.error(display_path(skill_dir), "skill name '{}' conflicts with a group resources directory.".format(name))
        if name in seen:
            report.error(
                display_path(skill_dir / "SKILL.md"),
                "duplicate skill name '{}', already used by '{}'. Skill names must be "
                "unique.".format(name, display_path(seen[name])),
            )
        else:
            seen[name] = skill_dir
    return report, len(skill_dirs)


def annotate(kind, path, message):
    """Emit a GitHub Actions annotation so problems show up on the PR diff."""
    file_part, _, line_part = path.partition(":")
    location = "file={}".format(file_part)
    if line_part.isdigit():
        location += ",line={}".format(line_part)
    print("::{} {}::{}".format(kind, location, message))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the skills in a vibe.md collection.")
    parser.add_argument(
        "--skills-dir",
        default=str(DEFAULT_SKILLS_DIR),
        help="directory containing skills and skill groups (default: skills/)",
    )
    args = parser.parse_args(argv)

    skills_dir = Path(args.skills_dir)
    if not skills_dir.is_dir():
        sys.stderr.write("error: skills directory not found: {}\n".format(skills_dir))
        return 2

    report, count = validate_collection(skills_dir)
    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"

    for path, message in report.warnings:
        print("warning: {}: {}".format(path, message))
        if in_ci:
            annotate("warning", path, message)
    for path, message in report.errors:
        print("error: {}: {}".format(path, message))
        if in_ci:
            annotate("error", path, message)

    if report.errors:
        print(
            "\nValidation failed: {} error(s) in {} skill(s). See CONTRIBUTING.md for the "
            "skill format.".format(len(report.errors), count)
        )
        return 1
    if count == 0:
        print("No skills found in {}. Nothing to validate.".format(display_path(skills_dir)))
    else:
        print("All {} skill(s) are valid.".format(count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
