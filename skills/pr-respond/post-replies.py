#!/usr/bin/env python3
"""Parse a staged PR-respond doc and post its replies to GitHub.

The doc is written by the `pr-respond` skill into /tmp and may be hand-edited by
the user before posting. Grammar (see SKILL.md for the authoritative spec):

    # Respond: <owner>/<repo> #<pr>

    --- review 2101234567
    > the original comment, quoted for the user; `>` lines are not posted
    the reply, posted verbatim into that comment's thread

    --- issue
    a standalone comment on the PR conversation

`--- review <id>` replies in the thread of that review comment (POST to
pulls/<pr>/comments with in_reply_to). `--- issue` posts a new comment on the
PR conversation (POST to issues/<pr>/comments). Replies post one per call, in
document order.

The post necessarily leaves the sandbox (it needs the gh token and network), so
it surfaces as one approval prompt. Use --dry-run to preview every payload
without posting (works offline).
"""

import argparse
import json
import re
import subprocess
import sys

HEADER_RE = re.compile(r"^#\s*Respond:\s*([^/\s]+)/([^\s#]+)\s*#?\s*(\d+)", re.I)
REPLY_HEADER_RE = re.compile(r"^---\s+(?:review\s+(\d+)|issue)\s*$", re.I)


def die(msg):
    print(f"post-replies: {msg}", file=sys.stderr)
    sys.exit(1)


def strip_quotes(lines):
    """Drop the quoted original comment; `>` lines are context, not content."""
    return [line for line in lines if not line.lstrip().startswith(">")]


def parse_doc(text):
    """Return (owner, repo, pr, replies)."""
    owner = repo = pr = None
    replies = []
    current = None
    buf = []

    def flush():
        if current is None:
            return
        body = "\n".join(strip_quotes(buf)).strip()
        if not body:
            where = f"review {current}" if current != "issue" else "issue"
            die(f"reply for {where} has an empty body")
        replies.append({"in_reply_to": current, "body": body})

    for line in text.splitlines():
        m = REPLY_HEADER_RE.match(line)
        if m:
            flush()
            buf = []
            current = m.group(1) if m.group(1) else "issue"
            continue
        if current is None:
            m = HEADER_RE.match(line)
            if m and owner is None:
                owner, repo, pr = m.group(1), m.group(2), m.group(3)
            continue
        buf.append(line)
    flush()
    return owner, repo, pr, replies


def endpoint_and_payload(owner, repo, pr, reply):
    if reply["in_reply_to"] == "issue":
        return (
            f"repos/{owner}/{repo}/issues/{pr}/comments",
            {"body": reply["body"]},
        )
    return (
        f"repos/{owner}/{repo}/pulls/{pr}/comments",
        {"body": reply["body"], "in_reply_to": int(reply["in_reply_to"])},
    )


def main():
    ap = argparse.ArgumentParser(description="Post the replies staged in a PR-respond doc.")
    ap.add_argument("doc", help="path to the staged respond doc (e.g. /tmp/pr-respond-owner-repo-123.md)")
    ap.add_argument("--repo", help="override owner/repo from the doc header")
    ap.add_argument("--pr", help="override the PR number from the doc header")
    ap.add_argument("--dry-run", action="store_true", help="print every payload and gh command; do not post")
    args = ap.parse_args()

    try:
        with open(args.doc, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        die(f"cannot read {args.doc}: {e}")

    owner, repo, pr, replies = parse_doc(text)

    if args.repo:
        if "/" not in args.repo:
            die("--repo must be owner/repo")
        owner, repo = args.repo.split("/", 1)
    if args.pr:
        pr = str(args.pr).lstrip("#")

    if not (owner and repo and pr):
        die("could not determine owner/repo/pr (fix the `# Respond:` header or pass --repo/--pr)")
    if not replies:
        die("no replies found (each one starts with `--- review <id>` or `--- issue`)")

    posted = 0
    for reply in replies:
        endpoint, payload = endpoint_and_payload(owner, repo, pr, reply)
        cmd = ["gh", "api", endpoint, "--method", "POST", "--input", "-"]

        if args.dry_run:
            print("# would run:", " ".join(cmd))
            print(json.dumps(payload, indent=2))
            continue

        try:
            subprocess.run(cmd, input=json.dumps(payload), text=True, check=True)
        except FileNotFoundError:
            die("`gh` not found on PATH")
        except subprocess.CalledProcessError as e:
            die(
                f"gh api failed (exit {e.returncode}) on reply {posted + 1} of {len(replies)}; "
                f"the first {posted} already posted, so delete them from the doc before a rerun"
            )
        posted += 1

    if not args.dry_run:
        print(f"posted {posted} repl{'y' if posted == 1 else 'ies'}")


if __name__ == "__main__":
    main()
