# agents-global

Global agent config shared across Claude Code and Codex. This repo is the source of truth for personal global instructions, shared skills, and the small amount of runtime config that is safe to install from a repo.

## Convention

The source tree is shared-first and target-second.

| Repo path | Claude install | Codex install | Role |
| --- | --- | --- | --- |
| `AGENTS.md` | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` | Global instructions. This is the only instruction source; `CLAUDE.md` is an installed projection. |
| `skills/<name>/` | `~/.claude/skills/<name>/` | `~/.agents/skills/<name>/` | Shared skill source. The installed set is the `SKILLS` list in the `Makefile`. |
| `claude/settings.json` | `~/.claude/settings.json` | | Claude global settings. |
| `claude/scripts/statusline.sh` | `~/.claude/scripts/statusline.sh` | | Claude status line helper. |
| `codex/agents-global.config.toml` | | `~/.codex/agents-global.config.toml` | Optional Codex profile. It is not copied over `~/.codex/config.toml`. |

Do not add a source `CLAUDE.md`. Edit `AGENTS.md` and let `make claude` copy it to the filename Claude expects.

## Install

```sh
make install       # installs Claude and Codex targets
make claude        # copies config -> ~/.claude, scripts -> ~/.claude/scripts, skills -> ~/.claude/skills
make codex         # copies AGENTS.md -> ~/.codex, profile -> ~/.codex, skills -> ~/.agents/skills
make diff          # compares installed copies with this repo
```

`make install` copies files; the repo is not needed at runtime. Override the targets with `make claude CLAUDEDIR=...` or `make codex CODEXHOME=... CODEXSKILLDIR=...`.

## Caveat: copy model and drift

Unlike a symlink/in-place dotfiles setup, this repo is the source of truth and the installed files are disposable copies. Re-run the relevant install target after every edit here for changes to take effect.

The reverse matters too: Claude Code itself writes to `~/.claude/settings.json` when toggling things via `/config`, enabling plugins, and similar runtime operations. Those runtime writes land in the installed copy, not here, so they will drift. Use `make diff` to spot drift, backport any wanted changes into this repo, then `make reinstall`.

Codex is more stateful in `~/.codex/config.toml`: it stores local trust entries and user-specific settings there. For that reason `make codex` installs `codex/agents-global.config.toml` as a profile instead of overwriting `~/.codex/config.toml`. Use it with `codex --profile agents-global`, or merge selected keys into `~/.codex/config.toml` by hand when they should become the default.

## Relation to agents-modes

`claude/scripts/statusline.sh` reads `$AGENTS_CLAUDE_MODE`, which the Claude launchers in [[agents-modes]] set. Under a mode launcher (`claude --settings <mode>.json`), this global `claude/settings.json` still applies, with the mode file overriding the permission and sandbox keys. The two repos are complementary layers.
