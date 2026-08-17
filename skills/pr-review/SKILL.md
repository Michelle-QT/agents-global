---
name: pr-review
description: "Review a PR and consolidate PR review findings into a single editable document in /tmp; the user edits the document, and then you post it as ONE PR review with one approved command."
---

## Workflow

- Identify the PR.
	- Resolve `owner`, `repo`, and the PR number from the PR number/URL if given, else infer from the current branch (`gh pr view`, or `gh-ro pr view` under a read-only forge escape). You will write them into the doc header.
- Review.
	- Review the PR code with the `review-loop` skill.
- Write the staging document.
	- Path: `/tmp/pr-review-<owner>-<repo>-<pr>.md` (so it is findable and never clobbers another PR's doc).
	- Use the grammar in [[#Document grammar]].
	- Put the verdict in the `event:` line. Default to `comment`, leave `request-changes` and `approve` as commented options so the user can change it.
	- Consolidate every finding here. Prose findings reference `path:line` in the body; line-anchored findings go in the optional `## Inline` section.
	- !!! UNLESS THERE IS A VERY GOOD REASON TO, ONLY USE INLINE COMMENTS.
- Hand it to the user.
	- Tell them the exact path and that they can open and edit it freely.
	- Wait for their confirmation. Do not post until they say so.
- Post it as one review.
	- Run the bundled `post-review.py` (it sits next to this SKILL.md, in this skill's directory).
	- Preview first with `--dry-run` (works offline, no approval needed) so the user sees the exact payload.
	- The real post needs the `gh` token and network, so it cannot run sandboxed; it surfaces as a single approval prompt. That prompt is the user's approval of the post.

```
# preview the exact payload, no posting:
python3 "<this skill's dir>/post-review.py" /tmp/pr-review-<owner>-<repo>-<pr>.md --dry-run

# post as one review (prompts for the sandbox escape = the user's approval):
python3 "<this skill's dir>/post-review.py" /tmp/pr-review-<owner>-<repo>-<pr>.md
```

## Document grammar

```
# Review: <owner>/<repo> #<pr>
event: comment            # comment | approve | request-changes

## Summary
Free markdown. Becomes part of the review body. Do not hard-wrap lines.

## Findings
Free markdown. Becomes part of the review body. Reference `path:line` in prose. Do not hard-wrap lines.

## Inline                 # optional; must be the LAST section
--- src/foo.ts:42
Comment anchored to line 42 on the new (RIGHT) side by default.
--- api/auth.py:40-44 LEFT
Comment anchored to lines 40-44 on the old (LEFT) side.
```

- Everything before `## Inline`, minus the `# Review:` and `event:` lines, is posted verbatim as the review body. Add or rename prose sections freely; they all go to the body.
- `## Inline` is the only special section and must come last. Each comment is a `--- path:line` (or `path:start-end`) header, an optional trailing `LEFT`/`RIGHT`, then the comment text up to the next `---`.

## Notes and caveats

- One review per run: body plus any inline comments post in a single `gh api .../reviews` call.
- Inline comments only attach to lines that appear in the PR diff. If a target line is not in the diff the post fails; reference it in `## Findings` prose instead.
- The doc is plain markdown the user may rewrite. The script re-parses whatever they save, so their edits are authoritative.
- Overrides exist for when the header is wrong: `--repo owner/repo`, `--pr N`, `--event ...`.
