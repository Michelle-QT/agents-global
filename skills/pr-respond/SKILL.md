---
name: pr-respond
description: "Respond to review comments on the user's own PR: triage every open comment, stage the replies in one editable document, then post them as threaded replies with one approved command."
---

## Workflow

- Identify the PR.
	- Resolve `owner`, `repo`, and the PR number from the PR number/URL if given, else infer from the current branch (`gh pr view`, or `gh-ro pr view` under a read-only forge escape).
- Collect the comments.
	- Review comments
	- Issue comments
- Triage each comment. Read the code it points at; do not answer from the comment text alone.
	- Review code with the `review-loop` skill.
	- Fix in code: the comment is right and the change is in scope.
	- Reply only: the comment is answered by an explanation, or it asks a question.
	- Escalate: the comment needs a decision that is the user's to make. Do not invent an answer; surface it.
- Apply the code fixes first, and commit them, so a reply can reference the commit that resolves the comment.
- Write the staging document.
	- Path: `/tmp/pr-respond-<owner>-<repo>-<pr>.md` (so it is findable and never clobbers another PR's doc).
	- Use the grammar in [[#Document grammar]].
	- One block per comment you answer. Quote the comment so the user can judge the reply without opening GitHub.
	- Drop a comment from the doc when it needs no reply; list the escalations for the user instead.
- Hand it to the user.
	- Tell them the exact path and that they can open and edit it freely.
	- Report the escalations, and the comments you left unanswered.
	- Wait for their confirmation. Do not post until they say so.
- Post the replies.
	- Run the bundled `post-replies.py` (it sits next to this SKILL.md, in this skill's directory).
	- Preview first with `--dry-run` (works offline, no approval needed) so the user sees every exact payload.
	- The real post needs the `gh` token and network, so it cannot run sandboxed; it surfaces as a single approval prompt. That prompt is the user's approval of the post.

```
# preview every reply, no posting:
python3 "<this skill's dir>/post-replies.py" /tmp/pr-respond-<owner>-<repo>-<pr>.md --dry-run

# post the replies (prompts for the sandbox escape = the user's approval):
python3 "<this skill's dir>/post-replies.py" /tmp/pr-respond-<owner>-<repo>-<pr>.md
```

## Document grammar

```
# Respond: <owner>/<repo> #<pr>

--- review 2101234567          # reply in the thread of review comment id 2101234567
> quoted comment, for the user's benefit; `>` lines are not posted
Reply text, posted verbatim.

--- issue                      # a new comment on the PR conversation
Reply text, posted verbatim.
```

- Each reply starts with a `--- review <id>` or `--- issue` header and runs to the next `---` header.
- `--- review <id>` posts into that comment's thread. The id is the `id` field of a `pulls/<pr>/comments` entry, not the thread position.
- `--- issue` posts a standalone comment on the PR. Use it for a top-level answer, or when a thread cannot be replied to.
- Lines starting with `>` are stripped before posting, so the quoted original never gets echoed back to the reviewer.

## Notes and caveats

- One HTTP call per reply, in document order. The script stops at the first failure and reports which replies already posted, so a rerun after a fix does not double-post the earlier ones.
- Replies only. Resolving a thread needs the GraphQL API and is out of scope; resolve threads in the GitHub UI.
- A reply to a comment on an outdated diff still posts; GitHub keeps it in the thread.
- The doc is plain markdown the user may rewrite. The script re-parses whatever they save, so their edits are authoritative.
- Overrides exist for when the header is wrong: `--repo owner/repo`, `--pr N`.
