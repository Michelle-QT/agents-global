---
name: proceed-autonomously
description: "Use when asked to proceed autonomously."
---

- When asked to proceed autonomously for accomplishing a task:
	- Enumerate to the user the steps you will follow without user input
	- Describe how many of those steps you expect to accomplish without the user's supervision
	- Provide your best estimate and confidence of when you expect the last step you can drive autonomously to conclude
- Then drive the entire task

- Verify each step started correctly before you wait for it to finish
- For monitoring, use ONLY terminal-native commands (sleep, a watcher, or other scripts that call you when steps or sub-steps are completed so you can continue). Do not use harness-specific tools, as these may prompt the user.
- Do not use commands that prompt the user for permission when working autonomously. This blocks you so you are effectively not working autonomously. In particular, never disable the sandbox preemptively. Before the first call of any new command shape, state which of the two outcomes you expect: simply runs silently or prompts. If the answer is "prompts", find the no-prompt path first.
