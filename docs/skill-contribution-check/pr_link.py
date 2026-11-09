#!/usr/bin/env python3
"""Print a GitHub link that opens a vibe.md Pull Request with the description filled in.

    python3 docs/skill-contribution-check/pr_link.py [--remote origin] [--skill-name NAME]

Used by step 9 of docs/skill-contribution-check/SKILL.md. It only reads: the current
branch, the fork's remote URL, and <git dir>/vibe-md-pr-body.md, which Git never
commits. It makes no network calls and opens nothing. Every part of the link is
percent-encoded, so text such as "&" or "#" in the description cannot change the link.
With --skill-name it also prints a quoted `gh pr create` command, for the agent to show
the user; it never runs it.

Exit status: 0 with the link printed, 1 when no link can be made (the reason is printed),
2 for usage errors.
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

UPSTREAM = ("vibe-md", "vibe.md")
BODY_NAME = "vibe-md-pr-body.md"
MAX_URL_LENGTH = 8000  # Longer links can be cut off by browsers or GitHub.
GITHUB_REMOTE = re.compile(
    r"(?:https://(?:[^@/?#\s]+@)?github\.com/|git@github\.com:|ssh://git@github\.com/)"
    r"([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/([A-Za-z0-9_-][A-Za-z0-9._-]*?)(?:\.git)?/?"
)
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SAFE_BRANCH = re.compile(r"[A-Za-z0-9._/-]+")


def git(*args):
    try:
        result = subprocess.run(["git"] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "replace").strip()


def parse_remote(url):
    """(owner, repo) for a GitHub remote URL, or None."""
    found = GITHUB_REMOTE.fullmatch(url or "")
    if not found or ".." in found.group(2):
        return None
    return found.groups()


def head_ref(owner, repo, branch):
    """The compare head: just the branch in vibe-md/vibe.md itself, owner:repo:branch in a fork."""
    return branch if (owner, repo) == UPSTREAM else "{}:{}:{}".format(owner, repo, branch)


def build_url(owner, repo, branch, body):
    return "https://github.com/vibe-md/vibe.md/compare/main...{}?quick_pull=1&body={}".format(
        head_ref(owner, repo, quote(branch, safe="/")), quote(body, safe=""))


def gh_command(owner, repo, branch, skill_name, body_path):
    """A `gh pr create` command with every value quoted, or None if a value looks wrong."""
    if not SKILL_NAME.fullmatch(skill_name or "") or len(skill_name) > 64 or not SAFE_BRANCH.fullmatch(branch):
        return None
    head = branch if (owner, repo) == UPSTREAM else "{}:{}".format(owner, branch)
    return " ".join(shlex.quote(part) for part in [
        "gh", "pr", "create", "--repo", "vibe-md/vibe.md", "--base", "main", "--head", head,
        "--title", "Add {} skill".format(skill_name), "--body-file", str(body_path)])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--remote", default="origin", help="the remote of your fork (default: origin)")
    parser.add_argument("--skill-name", help="also print a quoted `gh pr create` command for this skill")
    args = parser.parse_args(argv)

    git_dir = git("rev-parse", "--absolute-git-dir")
    if git_dir is None:
        print("Git is not installed, or this is not a Git repository.")
        return 1
    body_path = Path(git_dir) / BODY_NAME
    try:
        body = body_path.read_text(encoding="utf-8")
    except OSError:
        print("No description file at {}. Fill it in first (step 9).".format(body_path))
        return 1

    branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    if not branch:
        print("You are not on a branch. Switch to the branch with your skill first.")
        return 1
    remote = parse_remote(git("remote", "get-url", "--end-of-options", args.remote))
    if remote is None:
        print("The remote '{}' is not a GitHub repository. Paste the file into the "
              "Pull Request description instead: {}".format(args.remote, body_path))
        return 1

    last_commit = git("log", "-1", "--format=%ct")
    if last_commit and os.path.getmtime(str(body_path)) < int(last_commit):
        print("Note: the description file is older than your last commit. Fill it in again "
              "if it was written for other work.")
    # What this clone last saw of the branch on the fork. It can be out of date; GitHub is
    # not asked, so this is a reminder, not a guarantee.
    pushed = "refs/remotes/{}/{}".format(args.remote, branch)
    if git("rev-parse", "--verify", "--quiet", pushed) is None:
        print("Note: the branch '{}' is not on '{}' yet, as far as this clone knows. Push it to "
              "your fork first, or the link will not find it.".format(branch, args.remote))
    elif git("rev-list", "--count", pushed + "..HEAD") not in (None, "0"):
        print("Note: you have commits that are not pushed to '{}' yet. Push them first, "
              "or the Pull Request will not include them.".format(args.remote))
    if git("status", "--porcelain"):
        print("Note: you have changes that are not committed. They are not part of the Pull Request.")

    if args.skill_name is not None:
        command = gh_command(remote[0], remote[1], branch, args.skill_name, body_path)
        if command is None:
            print("No gh command: the skill name or the branch name has unexpected characters.")
        else:
            print("gh command: " + command)

    url = build_url(remote[0], remote[1], branch, body)
    print("Link length: {} characters.".format(len(url)))
    if len(url) > MAX_URL_LENGTH:
        print("Too long for a link. Paste the file into the Pull Request description instead: {}".format(body_path))
        return 1
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
