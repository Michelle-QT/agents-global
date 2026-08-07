#!/usr/bin/env python3
"""Parse a staged PR-message doc and either open a new GitHub pull request or edit an
existing one's title and body.

The doc is written by the `pr-open` skill into /tmp and may be hand-edited by the user
before applying. Grammar (see SKILL.md for the authoritative spec):

    # PR: <owner>/<repo>            # no number -> open a new PR
    # PR: <owner>/<repo> #123       # a number -> edit existing PR #123
    base: main                 # branch the PR merges into
    head: my-feature-branch    # source branch; defaults to the current branch (new PR only)
    draft: false               # true | false (new PR only)
    title: feat: add the thing

    ## Summary
    ...free markdown...

    ## Changes
    ...free markdown...

The `# PR:`, `base:`, `head:`, `draft:`, and `title:` lines are metadata. Everything
from the first body line onward (e.g. the `## Summary` section) becomes the PR body
verbatim.

Opening a NEW PR pushes the head branch to the remote (no force: it publishes the branch
if new, fast-forwards it if it already exists, and fails on divergence rather than
clobbering) and then runs `gh pr create`. EDITING an existing PR runs `gh pr edit` and
does not push (it only changes the title and body, and the base if given). Either way the
applying step needs the network and the gh token, so it cannot run sandboxed and surfaces
as one approval prompt. Use --dry-run to preview the exact commands and body without
doing anything (works offline).
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
import tempfile

HEADER_RE = re.compile(r"^#\s*PR:\s*([^/\s]+)/([^\s#]+)\s*(?:#\s*(\d+))?", re.I)
META_RE = re.compile(r"^(base|head|draft|title):\s*(.*)$", re.I)
TRUE = {"true", "yes", "1", "on"}
FALSE = {"false", "no", "0", "off", ""}


def die(msg):
    print(f"pr-open: {msg}", file=sys.stderr)
    sys.exit(1)


def note(msg):
    print(f"pr-open: {msg}", file=sys.stderr)


def parse_doc(text):
    """Return (owner, repo, pr, meta dict, body str). pr is None when absent.

    Metadata is recognized only in the leading header region. The body starts at the
    first non-blank line that is neither the `# PR:` header nor a known `key:` line,
    and from there everything is body verbatim (so a colon in body prose is safe).
    """
    lines = text.splitlines()
    owner = repo = pr = None
    meta = {}
    body_start = None
    for i, line in enumerate(lines):
        if not line.strip():
            continue  # blank lines in the header region are ignored
        m = HEADER_RE.match(line)
        if m and owner is None:
            owner, repo, pr = m.group(1), m.group(2), m.group(3)
            continue
        m = META_RE.match(line)
        if m and m.group(1).lower() not in meta:
            meta[m.group(1).lower()] = m.group(2).strip()
            continue
        body_start = i
        break
    body = "\n".join(lines[body_start:]).strip() if body_start is not None else ""
    return owner, repo, pr, meta, body


def current_branch():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def as_bool(val, what):
    v = val.strip().lower()
    if v in TRUE:
        return True
    if v in FALSE:
        return False
    die(f"{what} must be true or false, got {val!r}")


def run_with_body(cmd, body):
    """Run a gh command, passing the PR body via a temp file (--body-file)."""
    fd, path = tempfile.mkstemp(prefix="pr-open-body-", suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(body + "\n")
        try:
            subprocess.run(cmd + ["--body-file", path], check=True)
        except FileNotFoundError:
            die("`gh` not found on PATH")
        except subprocess.CalledProcessError as e:
            die(f"gh {cmd[1]} {cmd[2]} failed (exit {e.returncode})")
    finally:
        os.unlink(path)


def main():
    ap = argparse.ArgumentParser(description="Open a new PR or edit an existing one's title and body from a staged doc.")
    ap.add_argument("doc", help="path to the staged PR doc (e.g. /tmp/pr-open-owner-repo-branch.md)")
    ap.add_argument("--repo", help="override owner/repo from the doc header")
    ap.add_argument("--pr", help="edit this existing PR number instead of opening a new one")
    ap.add_argument("--base", help="override the base branch")
    ap.add_argument("--head", help="override the head branch (new PR only)")
    ap.add_argument("--remote", default="origin", help="git remote to push the head branch to (default: origin)")
    ap.add_argument("--draft", dest="draft", action="store_true", default=None, help="open as a draft PR (new PR only)")
    ap.add_argument("--no-draft", dest="draft", action="store_false", help="open as a ready (non-draft) PR (new PR only)")
    ap.add_argument("--no-push", action="store_true", help="do not push the head branch; assume it is already on the remote (new PR only)")
    ap.add_argument("--dry-run", action="store_true", help="print the commands and body; do nothing (works offline)")
    args = ap.parse_args()

    try:
        with open(args.doc, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        die(f"cannot read {args.doc}: {e}")

    owner, repo, pr, meta, body = parse_doc(text)

    if args.repo:
        if "/" not in args.repo:
            die("--repo must be owner/repo")
        owner, repo = args.repo.split("/", 1)
    if args.pr:
        pr = str(args.pr).lstrip("#")

    base = args.base or meta.get("base")
    title = meta.get("title")
    draft = args.draft if args.draft is not None else as_bool(meta.get("draft", "false"), "draft")

    if not (owner and repo):
        die("could not determine owner/repo (fix the `# PR:` header or pass --repo)")
    if not title:
        die("PR title is empty (add a `title:` line)")
    if not body:
        die("PR body is empty (write a ## Summary)")

    edit_mode = pr is not None

    if edit_mode:
        edit_cmd = ["gh", "pr", "edit", str(pr), "--repo", f"{owner}/{repo}", "--title", title]
        if base:
            edit_cmd += ["--base", base]
        if draft:
            note("note: draft state is not changed when editing a PR; use `gh pr ready` / `gh pr ready --undo`")
        if args.dry_run:
            print("# would run: ", shlex.join(edit_cmd + ["--body-file", "-"]))
            print("# --- body ---")
            print(body)
            return
        run_with_body(edit_cmd, body)
        return

    head = args.head or meta.get("head") or current_branch()
    if not head:
        die("could not determine the head branch (set `head:` or pass --head)")

    push_cmd = ["git", "push", "-u", args.remote, head]
    create_cmd = ["gh", "pr", "create", "--repo", f"{owner}/{repo}", "--head", head, "--title", title]
    if base:
        create_cmd += ["--base", base]
    if draft:
        create_cmd.append("--draft")

    if args.dry_run:
        print("# would push:", "(skipped: --no-push)" if args.no_push else shlex.join(push_cmd))
        print("# would run: ", shlex.join(create_cmd + ["--body-file", "-"]))
        print("# --- body ---")
        print(body)
        return

    if not args.no_push:
        try:
            subprocess.run(push_cmd, check=True)
        except FileNotFoundError:
            die("`git` not found on PATH")
        except subprocess.CalledProcessError as e:
            die(f"git push failed (exit {e.returncode}); resolve it or rerun with --no-push")
    run_with_body(create_cmd, body)


if __name__ == "__main__":
    main()
