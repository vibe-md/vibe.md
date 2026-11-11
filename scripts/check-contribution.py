#!/usr/bin/env python3
"""Write a friendly, plain-language report about a Pull Request's changes.

    python3 scripts/check-contribution.py --base origin/main
    python3 scripts/check-contribution.py --base HEAD^1 --pr-body-file body.md --pr-author octocat   # in CI
    python3 scripts/check-contribution.py --files skills/my-skill/SKILL.md      # no Git needed

The same check runs on every Pull Request in CI, and contributors (or their agents,
through docs/skill-contribution-check/SKILL.md) can run it before they open one.

It only reads files. It never runs anything from the files it checks, never uses the
network, and never posts anything. The rules are fixed; there is no AI involved.

It fails only on problems that are clear-cut: validator errors, hidden characters in
skill files, text that looks like a real secret, and a package skill that its package
README does not mention. Everything that needs a human's judgement is a warning.
Exit status: 0 when nothing must be fixed, 1 otherwise, 2 for usage errors.
"""

import argparse
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = _load("validate_skills", "validate-skills.py")
builder = _load("build_packages", "build-packages.py")

# Zero-width, bidirectional control, invisible separator and Unicode "tag" characters.
# They can hide text from a human reviewer while an agent still reads it, so they never
# belong in a skill or in the instructions agents read. Written as escapes on purpose.
HIDDEN_CHARACTERS = re.compile("[\u061c\u180e\u200b-\u200f\u2028-\u202e\u2060-\u2064\u2066-\u2069\ufeff\U000e0000-\U000e007f]")

# Commands that are fine when the skill asks the user first, and harmful when it doesn't.
RISKY_COMMANDS = [
    (re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b"),
     "downloads something and runs it in a shell"),
    (re.compile(r"\brm\s+-[a-zA-Z]*(?:r[a-zA-Z]*f|f[a-zA-Z]*r)[a-zA-Z]*\b"), "deletes files recursively (rm -rf)"),
    (re.compile(r"\bgit\s+push\b[^\n]*(?:--force\b|\s-f\b)"), "force-pushes"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "discards local changes (git reset --hard)"),
    (re.compile(r"(?:^|[\s`(])sudo\s"), "uses sudo"),
]

# Agent folders are installation destinations. Skills are never committed there.
AGENT_FOLDERS = (".claude/skills/", ".agents/skills/", ".cursor/skills/", ".gemini/skills/", ".github/skills/")
# Folders that decide what every contribution may do. Maintainers change them; contributors rarely should.
MAINTAINER_AREAS = ("scripts/", ".github/", "tests/", "skills/_shared/")
ALLOWED_EXTRAS = {"evals/scenarios.json"}
WEBSITE_SECTIONS = ("When to Use", "Examples")
PR_DESCRIPTION = "Pull Request description"
CHECKBOX = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$")


class Findings:
    """Problems sorted the way the report shows them."""

    def __init__(self):
        self.must_fix = []      # (path, line, message): fail the check
        self.worth_a_look = []  # (path, line, message): warnings
        self.looks_good = []    # plain sentences

    def fail(self, path, message, line=None):
        self.must_fix.append((path, line, message))

    def warn(self, path, message, line=None):
        self.worth_a_look.append((path, line, message))

    def good(self, message):
        self.looks_good.append(message)


# ---------------------------------------------------------------------------
# Which files changed


def _git(root, *args):
    try:
        return subprocess.run(["git", "-C", str(root)] + list(args), check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.CalledProcessError) as error:
        detail = (getattr(error, "stderr", b"") or b"").decode("utf-8", "replace").strip()
        raise SystemExit("error: git {} failed: {}".format(" ".join(args), detail or error))


def changed_files_from_git(root, base):
    """(status, path) pairs from where the branch left base to the working tree, including new
    untracked files, without following renames. Comparing from the merge-base means changes
    that reached base later are not counted as the contributor's. In CI the working tree is
    the Pull Request's merge commit and base is its first parent."""
    if base.startswith("-"):
        raise SystemExit("error: --base must be a branch or commit, such as origin/main")
    start = _git(root, "merge-base", "--end-of-options", base, "HEAD").strip()
    parts = [part for part in _git(root, "diff", "--name-status", "--no-renames", "-z", "--end-of-options",
                                   start).split("\0") if part]
    changes = [(parts[i][0], parts[i + 1]) for i in range(0, len(parts) - 1, 2)]
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    changes += [("A", path) for path in untracked if path]
    return changes


def unit_of(path):
    """The skill or package a skills/ path belongs to, such as 'skills/gitly' or 'skills/api-check'."""
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "skills" and parts[1] != "_shared":
        return "skills/" + parts[1]
    return None


# ---------------------------------------------------------------------------
# Checks


UNSAFE_NAME = re.compile(r"[\x00-\x1f\x7f`]")


def check_file_names(changes, findings):
    """Control characters or backticks in a file name are never needed, and could forge
    report or annotation text. Report them by a safe description and drop them."""
    safe = []
    for status, path in changes:
        if UNSAFE_NAME.search(path) or HIDDEN_CHARACTERS.search(path):
            findings.fail(PR_DESCRIPTION, "a file name contains control or invisible characters "
                                          "({}). Rename it.".format(ascii(path)))
        else:
            safe.append((status, path))
    return safe


def check_scope(changes, findings):
    paths = [path for _, path in changes]
    if paths == ["skills/README.md"]:
        # The automated index update changes only the generated file. Nothing to say.
        findings.good("Only the generated skills index changed.")
        return []
    units = sorted({unit_of(path) for path in paths if unit_of(path)})
    for path in paths:
        if path.startswith(AGENT_FOLDERS):
            findings.warn(path, "this is an agent's installation folder. Skills live only in skills/; "
                                "remove this file from the Pull Request.")
        elif path.startswith(MAINTAINER_AREAS):
            findings.warn(path, "this file is in a maintainer area (scripts/, .github/, tests/ or "
                                "skills/_shared/). That is fine for tooling changes, but a skill "
                                "contribution should not need it. A maintainer must review it.")
        elif unit_of(path) is None and path not in ALLOWED_EXTRAS and path != "skills/README.md":
            findings.warn(path, "this file is outside your skill or package folder. Keep a skill "
                                "Pull Request to its own folder (plus evals/scenarios.json).")
        elif path == "skills/README.md":
            findings.warn(path, "skills/README.md is generated automatically after a merge. "
                                "Leave it out of your Pull Request.")
    if len(units) > 1:
        findings.warn(units[0], "this Pull Request changes {} skills or packages ({}). Unless they "
                                "belong together, open one Pull Request per skill.".format(
                                    len(units), ", ".join(units)))
    elif len(units) == 1 and not findings.worth_a_look:
        findings.good("All changes stay inside {}.".format(units[0]))
    return units


def check_validator(root, findings):
    previous = os.getcwd()
    os.chdir(str(root))
    try:
        report, count = validator.validate_collection(Path("skills"))
    finally:
        os.chdir(previous)
    for path, message in report.errors:
        file_part, _, line_part = path.partition(":")
        findings.fail(file_part, "the validator says: " + message,
                      int(line_part) if line_part.isdigit() else None)
    if not report.errors:
        findings.good("The skill validator passes ({} skills).".format(count))
    return report


def read_text(root, path):
    full = root / path
    if full.is_symlink() or not full.is_file():
        return None
    try:
        with open(str(full), "rb") as handle:
            data = handle.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", "replace")


def check_hidden_and_secrets(root, changes, findings):
    hidden_found = secret_found = False
    for status, path in changes:
        if status == "D":
            continue
        text = read_text(root, path)
        if text is None:
            continue
        in_skill = path.startswith(("skills/", "evals/")) or path.endswith(".md")
        for number, line in enumerate(text.splitlines(), 1):
            if in_skill and HIDDEN_CHARACTERS.search(line):
                hidden_found = True
                codes = sorted({"U+{:04X}".format(ord(c)) for c in HIDDEN_CHARACTERS.findall(line)})
                findings.fail(path, "this line contains invisible characters ({}). They can hide text "
                                    "from reviewers while an agent still reads it. Delete them.".format(
                                        ", ".join(codes)), number)
            for pattern, label in validator.SECRET_PATTERNS:
                if pattern.search(line):
                    secret_found = True
                    findings.fail(path, "this line looks like it contains {}. Remove it, and if it is real, "
                                        "revoke it now: it is already visible in this Pull Request.".format(label),
                                  number)
                    break
    if not hidden_found:
        findings.good("No hidden or invisible characters in skill files or Markdown.")
    if not secret_found:
        findings.good("No secrets or private keys found.")


def check_risky_commands(root, changes, findings):
    for status, path in changes:
        if status == "D" or not path.startswith("skills/"):
            continue
        text = read_text(root, path)
        if text is None:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for pattern, label in RISKY_COMMANDS:
                if pattern.search(line):
                    findings.warn(path, "this line {}. Make sure the skill asks the user before doing "
                                        "this, and explains why.".format(label), number)
                    break


def frontmatter(text):
    """(data, body, number of lines before the body), or None when the frontmatter is broken."""
    try:
        raw, body = validator.split_frontmatter(text)
        data = validator.yaml.safe_load(raw) if raw.strip() else {}
    except Exception:
        return None
    return data, body, len(raw.splitlines()) + 2


def unclosed_fence(body):
    """The 1-based body line of a code fence that is never closed, or None."""
    fence, opened = None, None
    for number, line in enumerate(body.splitlines(), 1):
        match = validator.FENCE_PATTERN.match(line)
        if not match:
            continue
        token = match.group(1)
        if fence is None:
            fence, opened = token, number
        elif token[0] == fence[0] and len(token) >= len(fence) and not match.group(2).strip():
            fence = None
    return opened if fence is not None else None


def check_skill_files(root, changes, findings):
    skill_files = sorted({path for status, path in changes
                          if status != "D" and path.startswith("skills/") and path.endswith("/SKILL.md")})
    complete = 0
    for path in skill_files:
        text = read_text(root, path)
        if text is None:
            continue
        parsed = frontmatter(text)
        if parsed is None:  # the validator already reports broken frontmatter
            continue
        data, body, offset = parsed
        missing = [title for title in WEBSITE_SECTIONS if not builder.markdown_section(body, title)]
        if missing:
            findings.warn(path, "add {} section{} (exact heading{}). The website shows them on the "
                                "skill's page.".format(
                                    " and ".join("`## {}`".format(t) for t in missing),
                                    "s" if len(missing) > 1 else "", "s" if len(missing) > 1 else ""))
        else:
            complete += 1
        opened = unclosed_fence(body)
        if opened is not None:
            findings.warn(path, "a code block opened here is never closed, so the rest of the file may "
                                "show up as code.", opened + (offset or 0))
        standalone = path.count("/") == 2
        metadata = data.get("metadata") if isinstance(data, dict) else None
        if standalone and isinstance(metadata, dict) and not metadata.get("maintainers"):
            findings.warn(path, "add your GitHub username as `metadata.maintainers` so the website credits you.")
    if skill_files and complete == len(skill_files):
        findings.good("`## When to Use` and `## Examples` are there for the website.")
    for unit in sorted({unit_of(p) for _, p in changes if unit_of(p)}):
        readme = root / unit / "README.md"
        if (root / unit / "SKILL.md").is_file() or not readme.is_file():
            continue
        parsed = frontmatter(read_text(root, unit + "/README.md") or "")
        data = parsed[0] if parsed else None
        if isinstance(data, dict) and not data.get("maintainers"):
            findings.warn(unit + "/README.md", "add `maintainers: [your-github-username]` so the website credits you.")


GITHUB_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def maintainers_of(data):
    """The `maintainers` of a package README's frontmatter, lowercased."""
    value = data.get("maintainers") if isinstance(data, dict) else None
    if isinstance(value, str):
        value = value.replace(",", " ").split()
    if not isinstance(value, (list, tuple)):  # the validator reports any other type
        return set()
    return {str(login).strip().lstrip("@").lower() for login in value or [] if str(login).strip()}


def check_package_credit(root, changes, findings, author=None):
    """A skill added to an existing package must be listed in that package's README, and its
    author belongs in the README's `maintainers`, which is how the website credits them.

    A package README added in this Pull Request is a new package, which the checks above cover.
    The README must mention every package skill that changes (all of them do on main), so a
    missing row fails. The author check only warns: a maintainer may open the Pull Request for
    someone else, and a skill moved or renamed inside its package is not new work."""
    status_of = {path: status for status, path in changes}
    login = author if author and GITHUB_LOGIN.fullmatch(author) else None
    by_package = {}
    for status, path in changes:
        parts = path.split("/")
        if status == "D" or len(parts) != 4 or parts[0] != "skills" or parts[3] != "SKILL.md":
            continue
        by_package.setdefault("skills/" + parts[1], []).append((status, parts[2]))
    for unit, skills in sorted(by_package.items()):
        readme_path = unit + "/README.md"
        if status_of.get(readme_path) == "A" or (root / unit / "SKILL.md").is_file():
            continue  # a new package, or a standalone skill with a folder inside it
        text = read_text(root, readme_path)
        parsed = frontmatter(text) if text is not None else None
        if parsed is None:  # no README, or broken frontmatter: the validator reports it
            continue
        data, body, _ = parsed
        listed = []
        for _, name in sorted(skills):
            if re.search(r"(?<![A-Za-z0-9-]){}(?![A-Za-z0-9-])".format(re.escape(name)), body):
                listed.append(name)
            else:
                findings.fail(readme_path, "`{}` is not mentioned in this package README. Add a row for it to the "
                                           "skills table: its name and what it does.".format(name))
        moved = any(status == "D" and path.startswith(unit + "/") and path.endswith("/SKILL.md")
                    for status, path in changes)
        new = [name for status, name in sorted(skills) if status == "A"]
        if not new or moved or login is None:
            continue
        if login.lower() in maintainers_of(data):
            findings.good("`{}` credits {} for {}.".format(readme_path, login,
                                                          ", ".join("`{}`".format(n) for n in new)))
        else:
            findings.warn(readme_path, "add your GitHub username ({}) to `maintainers` in this README, keeping "
                                       "the names already there, so the website credits you for {}. If you are "
                                       "opening this Pull Request for someone else, add their username "
                                       "instead.".format(login, ", ".join("`{}`".format(n) for n in new)))


def strip_comments(text):
    """Remove <!-- ... --> comments in one pass (an unclosed comment runs to the end)."""
    out, position = [], 0
    while True:
        start = text.find("<!--", position)
        if start < 0:
            out.append(text[position:])
            return "".join(out)
        out.append(text[position:start])
        end = text.find("-->", start + 4)
        if end < 0:
            return "".join(out)
        position = end + 3


def plain(text):
    """Untrusted text quoted in the report, with Markdown that could forge content removed."""
    return re.sub(r"[`\[\]<>*_#!|]", "", text)


def check_template(body, findings):
    """The Pull Request description, compared with .github/PULL_REQUEST_TEMPLATE.md."""
    if body is None:
        return
    text = strip_comments(body)
    if not text.strip():
        findings.warn(PR_DESCRIPTION, "the description is empty. Please fill in the "
                                                  "Pull Request template.")
        return
    summary = re.search(r"^##\s+Summary\s*$(.*?)(?=^##\s|\Z)", text, flags=re.M | re.S)
    if summary is not None and not summary.group(1).strip():
        findings.warn(PR_DESCRIPTION, "the Summary section is empty. Say what the "
                                                  "skill does and why.")
    agents = re.search(r"Agents tested:[ \t]*([^\n]*)", text)
    if agents is not None and not agents.group(1).strip():
        findings.warn(PR_DESCRIPTION, "'Agents tested' is empty. Name the agents you "
                                                  "tried the skill with, or say honestly that you did not test it yet.")
    section = None
    unticked = []
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.*)$", line)
        if heading:
            section = heading.group(1).strip()
            continue
        box = CHECKBOX.match(line)
        if box and box.group(1) == " " and section in ("Validation", "Skill checklist"):
            unticked.append(box.group(2).strip())
    if unticked:
        short = [item if len(item) <= 70 else item[:67].rstrip() + "..." for item in unticked]
        findings.warn(PR_DESCRIPTION, "{} checklist item{} not ticked yet: {}. Tick each one "
                                                  "that is true, and say in Notes for reviewers why any "
                                                  "other does not apply.".format(
                                                      len(unticked), " is" if len(unticked) == 1 else "s are",
                                                      "; ".join("\"{}\"".format(plain(item)) for item in short)))


# ---------------------------------------------------------------------------
# Output


def location(path, line):
    return "`{}:{}`".format(path, line) if line else "`{}`".format(path)


def render(findings, units):
    ready = not findings.must_fix
    lines = ["## Contribution check", ""]
    if ready:
        lines.append("**No blocking problems found.** A maintainer will still read your contribution "
                     "before it is merged.")
    else:
        lines.append("**Some things must be fixed before this can be merged.** Each one says where "
                     "it is and what to do.")
    if units:
        lines += ["", "Checked: " + ", ".join("`{}`".format(unit) for unit in units)]
    if findings.must_fix:
        lines += ["", "### Must fix", ""]
        lines += ["- {}: {}".format(location(p, n), m) for p, n, m in findings.must_fix]
    if findings.worth_a_look:
        lines += ["", "### Worth a look", "", "These do not fail the check. They are things a reviewer will ask about.", ""]
        lines += ["- {}: {}".format(location(p, n), m) for p, n, m in findings.worth_a_look]
    if findings.looks_good:
        lines += ["", "### Looks good", ""]
        lines += ["- " + message for message in findings.looks_good]
    lines += ["", "_This check uses fixed rules and reads files only. You can run it yourself with "
                  "`python3 scripts/check-contribution.py --base origin/main`, or ask your agent to "
                  "\"check my skill\". See CONTRIBUTING.md for the full rules._", ""]
    return "\n".join(lines)


def annotation_text(text):
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def annotation_property(text):
    return annotation_text(text).replace(":", "%3A").replace(",", "%2C")


def annotate(kind, path, line, message):
    """One workflow command per finding, always on a single line."""
    if path == PR_DESCRIPTION:
        print("::{}::{}".format(kind, annotation_text(message)))
        return
    where = "file={}".format(annotation_property(path)) + (",line={}".format(int(line)) if line else "")
    print("::{} {}::{}".format(kind, where, annotation_text(message)))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report on the changes in a vibe.md Pull Request.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--base", help="Git ref to compare HEAD with, for example origin/main or HEAD^1")
    source.add_argument("--files", nargs="+", help="check these repository paths instead of a Git diff")
    parser.add_argument("--root", default=str(REPO_ROOT), help="repository to check (default: this one)")
    parser.add_argument("--pr-body-file", help="file holding the Pull Request description")
    parser.add_argument("--pr-author", help="GitHub username of the Pull Request's author, to check that a "
                                            "skill added to an existing package credits them")
    parser.add_argument("--summary-file", default=os.environ.get("GITHUB_STEP_SUMMARY"),
                        help="append the Markdown report here (default: $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "skills").is_dir():
        sys.stderr.write("error: no skills/ directory in {}\n".format(root))
        return 2
    if args.files:
        changes = [("M", path.strip("/")) for path in args.files]
    else:
        changes = changed_files_from_git(root, args.base)
    body = None
    if args.pr_body_file:
        try:
            body = Path(args.pr_body_file).read_text(encoding="utf-8", errors="replace")
        except OSError:
            body = ""

    findings = Findings()
    if not changes:
        findings.warn(PR_DESCRIPTION, "no changed files were found, so nothing was checked. If you "
                                      "committed straight to main, compare with vibe.md's main instead.")
    changes = check_file_names(changes, findings)
    units = check_scope(changes, findings)
    check_validator(root, findings)
    check_hidden_and_secrets(root, changes, findings)
    check_risky_commands(root, changes, findings)
    check_skill_files(root, changes, findings)
    check_package_credit(root, changes, findings, args.pr_author)
    check_template(body, findings)

    report = render(findings, units)
    print(report)
    if args.summary_file:
        with open(args.summary_file, "a", encoding="utf-8") as handle:
            handle.write(report + "\n")
    if os.environ.get("GITHUB_ACTIONS") == "true":
        for path, line, message in findings.worth_a_look:
            annotate("warning", path, line, message)
        for path, line, message in findings.must_fix:
            annotate("error", path, line, message)
    return 1 if findings.must_fix else 0


if __name__ == "__main__":
    sys.exit(main())
