---
name: stage-end
description: "Use when the user asks to end the stage of a standard project."
---

# Stage end protocol

The user may request to end the stage. This is achieved by following the *stage end protocol*.

The protocol is done so a fresh session can continue from the project spine + artifacts alone.

See the `standard-project` skill for the project layout and for what a stage is.

1. Artifacts are committed separately on their own cadence. Bring every modified artifact to a clean state: a plain repo gets a commit; an artifact that is itself a standard project gets its own stage end protocol (recurse) before that of the parent's.
2. Update TODO: move done items to the `# Recently finished` section checked off (don't delete), then re-plan. Don't mark an item as done unless it was implemented as well as tested! DO NOT ADD NEW TODO ITEMS WITHOUT CONSULTING THE USER FIRST.
3. Update DESIGN if the design or state changed. DO NOT MODIFY DESIGN WITHOUT CONSULTING THE USER FIRST.
4. VERY IMPORTANT: Re-read all live documents (eg TODO, DESIGN) for slop, using the `slop-clean` skill.
5. A single commit to the spine: a short subject + a structured body carrying what was done + observed (experiments, dead ends, verifications) and any relevant artifact SHAs. The subject stays short; the detail lives in the body, not a separate file.
