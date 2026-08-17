---
name: pr-open
description: "Open GitHub pull request"
---

## Instructions


1. Identify the target
	- New PR: resolve `owner`, `repo`, the `base` branch (the repo's default), and the `head` branch (the current branch) from the checkout
	- Existing PR: resolve `owner`, `repo`, and the PR number, and pre-fill the doc with the PR's current title and body so the user edits the live message
2. Review the diff
	- Write findings to `/tmp/pr-review-<owner>-<repo>-<head>.md` BEFORE writing the staging doc. If that file does not exist, do not proceed to step 3.
	- Review with the `review-loop` skill.
	- Iterate with the user on real decisions; report findings even when you then dismiss them.
	- Make sure that only relevant files are being added
	- REPO REMAINS SELFCONTAINED: Guarantee no hardcoded user-specific files or paths. MAKE SURE CODE DOES NOT REFERENCE USER-SPECIFIC FILES ETC LIKE PATHS, OR DOCUMENTS THAT ARE NOT IN THE REPOSITORY
3. Write the staging document
	- Path: `/tmp/pr-open-<owner>-<repo>-<head-or-pr>.md`
	- Use the grammar in [[#Document grammar]]
	- Do not include tests run
	- FOR THE LOVE OF CHRIST BE CONCISE
	- MESSAGES REMAIN REPO-CONTAINED: Guarantee no hardcoded user-specific files or paths. MAKE SURE MESSAGES DO NOT REFERENCE USER-SPECIFIC FILES ETC LIKE PATHS, OR DOCUMENTS THAT ARE NOT IN THE REPOSITORY
4. Hand it to the user and tell them the exact path
	- Wait for their confirmation. Do not apply until they say so.
5. Apply it as one action
	- Run the bundled `pr-open.py` (it sits next to this SKILL.md, in this skill's directory).
	- Preview first with `--dry-run` (works offline, no approval needed) so the user sees the exact commands and body.
	- The real run needs the `gh` token and network, so it cannot run sandboxed; it surfaces as a single approval prompt. A new PR is pushed then created; an open PR is edited (no push).

```
# preview the exact commands and body, nothing is pushed, created, or edited:
python3 "<this skill's dir>/pr-open.py" /tmp/pr-open-<owner>-<repo>-<head-or-pr>.md --dry-run

# apply it (prompts for the sandbox escape = the user's approval):
python3 "<this skill's dir>/pr-open.py" /tmp/pr-open-<owner>-<repo>-<head-or-pr>.md
```

## Document grammar

```
# PR: <owner>/<repo>            # no number -> open a NEW PR
# PR: <owner>/<repo> #123       # a number -> EDIT existing PR #123
base: main                 # branch the PR merges into
head: my-feature-branch    # source branch; defaults to the current branch (new PR only)
draft: false               # true | false (new PR only)
title: feat: add the thing

## Summary
Free markdown. Becomes the PR body verbatim. Do not hard-wrap lines.
```

- The `# PR:`, `base:`, `head:`, `draft:`, and `title:` lines are metadata. Everything from the first body line onward (here the `## Summary` section) becomes the PR body verbatim; add or rename body sections freely.
- The `#<pr>` in the header selects edit mode. `title` is required in both modes; `head` defaults to the current branch.

## Notes and caveats

- New PR: the push is `git push -u <remote> <head>` with no force, so it publishes the branch if new, fast-forwards it if it already exists, and fails on divergence rather than clobbering. Pass `--no-push` if the branch is already on the remote.
- Edit: only the title, body, and base change; there is no push and the commits are untouched. Draft state is not toggled here; use `gh pr ready` / `gh pr ready --undo`.
- The doc is plain markdown the user may rewrite; the script re-parses whatever they save.
- Same-repo PRs are assumed; cross-fork PRs are out of scope.
- Overrides for when the header is wrong: `--repo owner/repo`, `--pr N` (forces edit mode), `--base`, `--head`, `--draft`/`--no-draft`, `--remote`.
