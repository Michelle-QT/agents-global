---
name: review-loop
description: "Use whenever reviewing anything: code, a pull request, a document, or an experiment setup."
---

## Loop

- Do a thorough review of what the user asked to review.
- Use subagents if relevant; for example if context might get too full.
- Iterate until a review pass only surfaces trivial issues.
- Only review and address what is in scope.
- If by the end there are any issues that should be surfaced to the user, do so.
- Use other review tools or skills if relevant.

## Modes

The iteration step depends on whether you may change the target.

- The target is editable: your own branch, your own documents, experiment code.
	- Address the issues.
	- *Re-review* after the fixes, in case the fixes introduced new issues.
- The target is not editable: a pull request under review, third-party code.
	- Do not change the target.
	- Verify each finding against the code before you keep it; drop the findings you cannot support.
	- *Re-review* the findings themselves for correctness, scope, and duplication.
