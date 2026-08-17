---
name: standard-project
description: "Conventions and workflow for the user's standard projects"
---

# Standard project structure

A *standard project* consists of
- a directory tracked by a git repo, called the *spine* of the project, which contains
- files tracked by the spine
- any number of *artifacts*, which are subdirectories, typically gitignored sub-repos
 
The spine tracks the user's layer/perspective of the project.

A directory declares itself as a standard project by saying so in its root `AGENTS.md`.

This skill is the canonical source of the standard. Do not copy it into project docs.

## Layout of a standard project

- project-root/
	- AGENTS.md
		- user's
		- contains
			- manual, ops, device specific instructions, etc (eg github identities, running boxes, ssh, etc)
	- DESIGN.md
		- user's
		- living document
		- contains
			- current design / index / other project-wide information
	- TODO.md
		- user's
		- living document
		- contains tasks to be carried out by the user
		- each task consists of
			- title = at most one sentece
			- body = at most 5 bullet points; if it needs to be longer, make a spine document and wikilink it
		- ends with a `# Recently finished` section
			- completed items move there and are checked off, not deleted
	- MEETINGS.md
		- user's
		- living document
		- contains append-only notes from meetings between the user and collaborators
	- REPORT.md
		- user's
		- living document
		- optional; present when the project runs experiments
		- contains the project's current headline experiment results, curated (see the `standard-project-experiment` skill)
	- references/
		- user's
		- optional
		- contains typically frozen, read-only imports (PDFs, datasets, sources, code snippets)
		- it is gitignored only if it bloats the repo
	- archive/
		- optional
		- on-disk home for retired material kept deliberately, not a catch-all for everything removed (see [[#Retiring a file]])
	- sandbox-escapes/
		- user's
		- optional
		- locked wrappers that run outside the agent sandbox (see [[#Sandbox escapes]])
	- < lowercase >.md
		- user's
		- contains working files, either scratch or durable
		- these documents can serve as reports, notes, details that don't fit other documents, etc
	- artifact-repo/
		- potentially shared between user and collaborators
		- eg code-repo, paper-repo, etc
		- typically named `*-repo`
		- each artifact is typically its own git repo, and it is gitignored by the spine
			- commits in an artifact occur at their own cadence, not coupled with the spine
		- an artifact may have its own DESIGN / README / AGENTS / etc
		- an artifact may itself be a standard project (in that case, its AGENTS.md would declare this; see [[#Nesting]])
	- .gitignore
		- mine
		- ignores the artifact dirs

The commit messages in the spine serve as a lab-notebook record; they include what was done + observed, at each stage (see [[#Stages]]).

## Naming conventions

- CAPS = closed pillar vocabulary
	- for the spine, it is restricted to DESIGN, TODO, MEETINGS, REPORT, AGENTS
	- do not invent new CAPS files, unless confirmed by the user
- lowercase = working files, either scratch or durable

## Retiring a file

- Retiring a file is a deliberate choice between git-deleting it and moving it to `archive/`; do not default to archive (git-delete dead scratch).
- A retired artifact (a gitignored sub-repo) either goes to `archive/` or is deleted for good, depending on user's preference.

## Nesting

- an artifact may itself be a standard project
	- its AGENTS.md declares it as implementing a standard project
	- if it has AGENTS.md but no such declaration, it is a plain artifact
- the standard applies recursively
	- each nested project has its own spine, stages, protocol, and cadence
	- its docs are from its own perspective (the parent's stage commit notes it at a high level; the nested project's own commit history holds the detail)
	- it never references the parent (the artifact -> spine rule), so it stays shareable standalone
- consistency
	- when a parent stage touched a nested standard project, run that project's protocol too, so the whole tree is clean-handoff-able

## Invariants

### Single source of truth
- Do not write the same piece of information in more than one place; duplication leads to staleness and divergence.
- Information that is documented in an artifact should be referenced from the spine, not copied.

### References (what may point at what)
- Ideally a document may reference another only if the target is at least as stable AND at least as shareable as itself.
- Point toward more stable/shareable, never toward more volatile/private.

- Forbidden: artifact -> any spine doc (keeps each artifact standalone and shareable).
- Allowed: spine -> artifact: sparingly (each link is coupling; prefer one reference over a duplicated copy, but keep links few).
- Allowed, required: REPORT -> the per-experiment reports it curates (an artifact path), for traceability; this is the one reference REPORT is expected to make.
- Allowed: live docs -> MEETINGS, references/, artifact.
- Allowed: AGENTS.md -> any spine doc.
- Allowed: MEETINGS -> anything (explicit exception: meeting notes are contextual snapshots; refs may go stale, accepted).
- Discouraged: DESIGN <-> TODO cross-refs; DESIGN <-> REPORT and TODO <-> REPORT cross-refs; artifact -> artifact.

## Sandbox escapes

- `sandbox-escapes/` holds small wrappers that run OUTSIDE the agent sandbox with no prompt, for the few privileged actions a project needs unattended. This is set up globally, so a project adds no config of its own.
- The agent runs a wrapper with no prompt, but creating or editing one prompts for approval, so an escape cannot be silently added or changed. The grant lives outside the project, beyond the agent's reach.
- Each wrapper is a narrow allowlist: it validates its own arguments and refuses anything off-list, because an excluded command runs its whole process unsandboxed. Its header records its contract, so a project's escapes are just the directory contents.
- Invoke from the project root, standalone: `sandbox-escape <name> <args>`. A pipe or operator re-sandboxes the line, so shape output with the tool's own flags.
- Add or change one from outside the sandbox (a plain session, or edit directly); it is live once present. The `add-escape` skill does this end to end.
- Single source of truth: this section for the mechanism, each wrapper's header for its contract, AGENTS.md for when to reach for a given escape.

# Standard project dynamics

When an agent session is started and this skill is invoked, the agent must make sure to map everything described in this document to the current directory, and then ask the user what they would like to work on.

## Stages
- Work on a project is by stages.
- A *stage* corresponds to one commit to the spine repo.
- Past stages can be accessed via git.
- The stage commit message is the lab-notebook record
	- a short subject + a body with what was done + observed (experiments, results, dead ends, verifications), and it may pin artifact paths/SHAs. State facts, not conclusions (those go to DESIGN or other documents).
- The purpose of stages is that
	- After a stage commit the agent session should be disposable: the user can close the agent and start fresh with nothing lost, all relevant information is in the user's files; never only in the conversation.
	- This holds at stage boundaries, not mid-stage.

## Stage end protocol

- A stage is ended by the *stage end protocol*, which brings the artifacts and the spine to a clean, handoff-able state.
- The protocol lives in the `stage-end` skill.

## Working on artifacts

Whenever you work on an artifact, by default, use the latest main branch (check upstream as well), UNLESS there is a good reason to: eg a branch that combines main and some open PRs. CONSULT WITH THE USER if it isn't absolutely obvious which branch to use.

