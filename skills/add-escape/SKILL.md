---
name: add-escape
description: Add a sandbox escape to a standard project: a small locked wrapper under sandbox-escapes/ that runs one privileged command outside the agent sandbox with no prompt.
---

# Add a sandbox escape

A wrapper under a project's `sandbox-escapes/` runs unsandboxed and unprompted, so its argument allowlist is the only gate on what it does. Keep it narrow.

## Steps

1. Create `sandbox-escapes/<name>` and `chmod +x` it (creating it prompts for approval):
	- shebang, then `set -euo pipefail`.
	- a header stating the contract: what it allows, what it refuses, why that is safe.
	- validate arguments; refuse anything off the allowlist with a clear message and a non-zero exit; `exec` the real command otherwise.
	- a pure passthrough is only for a fully trusted target; the header must say so.
2. Add `sandbox-escapes/tests/<name>.test.sh`: stub the real command on PATH, assert allowed calls reach it and refused ones exit non-zero.
3. Add one when-to-use line to the project's `AGENTS.md`.

Invoke as `sandbox-escape <name> <args>`, standalone; a pipe or operator re-sandboxes the line.
