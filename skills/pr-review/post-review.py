#!/usr/bin/env python3
"""Parse a staged PR-review doc and post it as ONE GitHub review.

The doc is written by the `pr-review` skill into /tmp and may be hand-edited by
the user before posting. Grammar (see SKILL.md for the authoritative spec):

    # Review: <owner>/<repo> #<pr>
    event: comment            # comment | approve | request-changes

    ## Summary
    ...free markdown...

    ## Findings
    ...free markdown, e.g. bullets that reference `path:line` in prose...

    ## Inline                 # optional; must be the LAST section
    --- path/to/file.py:42
    a comment anchored to line 42 (RIGHT side by default)
    --- path/to/file.py:40-44 LEFT
    a comment anchored to lines 40-44 on the LEFT (old) side

Everything before `## Inline`, minus the `# Review:` and `event:` metadata
lines, becomes the review body verbatim. The `## Inline` section, if present,
becomes line-anchored review comments. Body + comments post as a single review.

The post necessarily leaves the sandbox (it needs the gh token and network), so
it surfaces as one approval prompt. Use --dry-run to preview the exact payload
without posting (works offline).
"""

import argparse
import json
import re
import subprocess
import sys

EVENTS = {
    "comment": "COMMENT",
    "approve": "APPROVE",
    "request-changes": "REQUEST_CHANGES",
    "request_changes": "REQUEST_CHANGES",
}

HEADER_RE = re.compile(r"^#\s*Review:\s*([^/\s]+)/([^\s#]+)\s*#?\s*(\d+)", re.I)
EVENT_RE = re.compile(r"^event:\s*(\S+)", re.I)
INLINE_HEADER_RE = re.compile(r"^##\s+Inline\s*$", re.I)
COMMENT_HEADER_RE = re.compile(
    r"^---\s+(.+?):(\d+)(?:-(\d+))?(?:\s+(LEFT|RIGHT))?\s*$", re.I
)


def die(msg):
    print(f"post-review: {msg}", file=sys.stderr)
    sys.exit(1)


def split_doc(text):
    """Return (head_lines, inline_lines). inline_lines is None if no section."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if INLINE_HEADER_RE.match(line):
            return lines[:i], lines[i + 1 :]
    return lines, None


def parse_head(head_lines):
    owner = repo = pr = event = None
    body_lines = []
    for line in head_lines:
        m = HEADER_RE.match(line)
        if m and owner is None:
            owner, repo, pr = m.group(1), m.group(2), m.group(3)
            continue
        m = EVENT_RE.match(line)
        if m and event is None:
            event = m.group(1).strip().lower()
            continue
        body_lines.append(line)
    return owner, repo, pr, event, "\n".join(body_lines).strip()


def parse_inline(inline_lines):
    """Parse the Inline section into GitHub review comment objects."""
    comments = []
    current = None
    buf = []

    def flush():
        if current is not None:
            body = "\n".join(buf).strip()
            if not body:
                die(f"inline comment for {current['path']} has empty body")
            comments.append({**current, "body": body})

    for line in inline_lines:
        m = COMMENT_HEADER_RE.match(line)
        if m:
            flush()
            buf = []
            path, a, b, side = m.group(1).strip(), m.group(2), m.group(3), m.group(4)
            side = (side or "RIGHT").upper()
            comment = {"path": path, "side": side}
            if b is None:
                comment["line"] = int(a)
            else:
                start, end = sorted((int(a), int(b)))
                comment["start_line"] = start
                comment["start_side"] = side
                comment["line"] = end
            current = comment
        else:
            if current is None:
                # ignore blank/preamble lines before the first `---`
                if line.strip():
                    die(f"text before first `---` in Inline section: {line!r}")
            else:
                buf.append(line)
    flush()
    return comments


def main():
    ap = argparse.ArgumentParser(description="Post a staged PR-review doc as one GitHub review.")
    ap.add_argument("doc", help="path to the staged review doc (e.g. /tmp/pr-review-owner-repo-123.md)")
    ap.add_argument("--repo", help="override owner/repo from the doc header")
    ap.add_argument("--pr", help="override the PR number from the doc header")
    ap.add_argument("--event", help="override the event (comment|approve|request-changes)")
    ap.add_argument("--dry-run", action="store_true", help="print the payload and gh command; do not post")
    args = ap.parse_args()

    try:
        with open(args.doc, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        die(f"cannot read {args.doc}: {e}")

    head_lines, inline_lines = split_doc(text)
    owner, repo, pr, event, body = parse_head(head_lines)

    if args.repo:
        if "/" not in args.repo:
            die("--repo must be owner/repo")
        owner, repo = args.repo.split("/", 1)
    if args.pr:
        pr = str(args.pr).lstrip("#")
    if args.event:
        event = args.event.strip().lower()

    if not (owner and repo and pr):
        die("could not determine owner/repo/pr (fix the `# Review:` header or pass --repo/--pr)")
    if not body:
        die("review body is empty (write a ## Summary / ## Findings)")

    event = event or "comment"
    if event not in EVENTS:
        die(f"unknown event {event!r}; use one of: {', '.join(EVENTS)}")

    comments = parse_inline(inline_lines) if inline_lines else []

    payload = {"body": body, "event": EVENTS[event]}
    if comments:
        payload["comments"] = comments

    endpoint = f"repos/{owner}/{repo}/pulls/{pr}/reviews"
    cmd = ["gh", "api", endpoint, "--method", "POST", "--input", "-"]

    if args.dry_run:
        print("# would run:", " ".join(cmd))
        print(json.dumps(payload, indent=2))
        return

    try:
        subprocess.run(cmd, input=json.dumps(payload), text=True, check=True)
    except FileNotFoundError:
        die("`gh` not found on PATH")
    except subprocess.CalledProcessError as e:
        die(f"gh api failed (exit {e.returncode})")


if __name__ == "__main__":
    main()
