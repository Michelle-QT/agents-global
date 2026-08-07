---
name: standard-project-experiment
description: "Conventions and workflow for running and writing up experiments in a standard project"
---

## Per-project declaration (AGENTS.md)
- A project that runs experiments declares an `## Experiments` block in its `AGENTS.md`. It records:
	- where experiment code lives
	- where the per-experiment report goes
	- where extra outputs go, and what is tracked vs gitignored
	- where metric / row / column definitions live
	- where dataset descriptions live
## Methodology
- Isolate one variable at a time, otherwise it is not possible to attribute the outcome
- Report faithfully
	- State what was actually run, what was skipped, and what is still uncontrolled. Flag a conclusion as preliminary until it is verified more than one way.
- Do not just give up and hedge
	- A flat or negative result is a hypothesis about the *setup* first, not the *idea*
	- Rule out bugs before concluding: assume a defect until you have checked the obvious ones
	- Fix and rerun before writing the conclusion
- Do not over-conclude from one or a few versions
	- "This approach does not work" needs more than one or two configurations
	- Vary the obvious axes first
- When running a long experiment (more than a minute or two)
	- Supervise a long run; do not block on it or fire-and-forget.
	- Launch it detached, so control returns when it finishes.
	- Watch it as it runs: catch a crash, a swallowed error, or a divergent/flat loss early rather than after hours of compute; kill and fix at the first clear sign.

## Outputs
- experiment report.md; ideally, only containing
	- "# Plan" section: A succinct description of the experiment
	- "# Log" section: Important observed facts during experiment
		- can wikilink to detailed-log.md if there is a good reason
	- "# Results" section
		- One or two tables (columns = metrics, rows = approaches / models / pipelines / configs)
			- an itemized list defining every row and every column.
		- Optionally (ONLY WHEN IMPORTANT): Figures, Caveats, Sources (line pinning the code, outputs, or reports that produced the numbers; use wikilinks)
	- "# Conclusions" section
		- Do NOT include conclusions section or ANY conclusions unless specifically asked by the user
- experiment detailed-log.md
	- append only detailed log for the experiment
	- append each time that some step that carries actual information is executed
	- typical entries are as follows, but could be others if relevant:
```
# TIMESTAMP

TERMINAL_COMMAND

OUTPUT
```
- one or more csv containing numerical results
	- csv should be computed programmatically from output data
	- the tables in report.md should be computed programmatically from csv

## `REPORT.md` (the spine report)
- Holds only the headline tables and figures that would go in a paper, curated from the per-experiment reports.
- An itemized list of references to the per-experiment reports, so that numbers can be traced.

## End-experiment protocol
- Independent of the stage protocol: a stage may bundle several experiments or none (see the `standard-project` skill).

1. Finalize the experiment report
2. Place other outputs per the project's tracking policy
3. If requested by the user:
	- Update `REPORT.md` folding in the headline numbers and figures
	- Re-read `REPORT.md` (and any metrics or datasets doc) for stale references, numbers, and links; fix or flag.
