# Install/uninstall global agent config.
#
# Files are COPIED into the target agent's config directories. After install the
# repo is not needed at runtime. Re-run the relevant target after editing a file
# here.

CLAUDEDIR ?= $(HOME)/.claude
CODEXHOME ?= $(HOME)/.codex
CODEXSKILLDIR ?= $(HOME)/.agents/skills

CLAUDE_CONFIG := settings.json
INSTRUCTIONS := AGENTS.md
CLAUDE_SCRIPTS := statusline.sh
CODEX_PROFILE := agents-global.config.toml
SKILLS := standard-project standard-project-experiment stage-end add-escape pr-open pr-review pr-respond pr-status where-are-we git write-document zotero proceed-autonomously open-threads review-loop slop-clean

.PHONY: install uninstall reinstall list diff test claude uninstall-claude reinstall-claude list-claude diff-claude codex uninstall-codex reinstall-codex list-codex diff-codex

install: claude codex

test:
	@bash tests/run.sh

uninstall: uninstall-claude uninstall-codex

reinstall: uninstall install

diff: diff-claude diff-codex

list: list-claude list-codex

claude:
	@mkdir -p "$(CLAUDEDIR)" "$(CLAUDEDIR)/scripts" "$(CLAUDEDIR)/skills"
	@for c in $(CLAUDE_CONFIG); do \
	  install -m 0644 "claude/$$c" "$(CLAUDEDIR)/$$c" && echo "config  -> $(CLAUDEDIR)/$$c"; \
	done
	@install -m 0644 "$(INSTRUCTIONS)" "$(CLAUDEDIR)/CLAUDE.md" && echo "config  -> $(CLAUDEDIR)/CLAUDE.md"
	@for s in $(CLAUDE_SCRIPTS); do \
	  install -m 0755 "claude/scripts/$$s" "$(CLAUDEDIR)/scripts/$$s" && echo "script  -> $(CLAUDEDIR)/scripts/$$s"; \
	done
	@for k in $(SKILLS); do \
	  rm -rf "$(CLAUDEDIR)/skills/$$k" && cp -R "skills/$$k" "$(CLAUDEDIR)/skills/$$k" && echo "skill   -> $(CLAUDEDIR)/skills/$$k"; \
	done
	@echo "done."

uninstall-claude:
	@for c in $(CLAUDE_CONFIG); do \
	  rm -f "$(CLAUDEDIR)/$$c" && echo "removed $(CLAUDEDIR)/$$c"; \
	done
	@rm -f "$(CLAUDEDIR)/CLAUDE.md" && echo "removed $(CLAUDEDIR)/CLAUDE.md"
	@for s in $(CLAUDE_SCRIPTS); do \
	  rm -f "$(CLAUDEDIR)/scripts/$$s" && echo "removed $(CLAUDEDIR)/scripts/$$s"; \
	done
	@for k in $(SKILLS); do \
	  rm -rf "$(CLAUDEDIR)/skills/$$k" && echo "removed $(CLAUDEDIR)/skills/$$k"; \
	done

reinstall-claude: uninstall-claude claude

list-claude:
	@echo "config  (-> $(CLAUDEDIR)):" && printf '  %s\n' $(CLAUDE_CONFIG)
	@printf '  %s -> %s\n' "$(INSTRUCTIONS)" CLAUDE.md
	@echo "scripts (-> $(CLAUDEDIR)/scripts):" && printf '  %s\n' $(CLAUDE_SCRIPTS)
	@echo "skills  (-> $(CLAUDEDIR)/skills):" && printf '  %s\n' $(SKILLS)

# Show how the installed copies differ from this repo (drift check).
diff-claude:
	@for c in $(CLAUDE_CONFIG); do \
	  diff -u "$(CLAUDEDIR)/$$c" "claude/$$c" && echo "== $$c: in sync" || true; \
	done
	@diff -u "$(CLAUDEDIR)/CLAUDE.md" "$(INSTRUCTIONS)" && echo "== CLAUDE.md: in sync" || true
	@for s in $(CLAUDE_SCRIPTS); do \
	  diff -u "$(CLAUDEDIR)/scripts/$$s" "claude/scripts/$$s" && echo "== $$s: in sync" || true; \
	done
	@for k in $(SKILLS); do \
	  diff -ru "$(CLAUDEDIR)/skills/$$k" "skills/$$k" && echo "== $$k: in sync" || true; \
	done

codex:
	@mkdir -p "$(CODEXHOME)" "$(CODEXSKILLDIR)"
	@install -m 0644 "$(INSTRUCTIONS)" "$(CODEXHOME)/AGENTS.md" && echo "config  -> $(CODEXHOME)/AGENTS.md"
	@install -m 0644 "codex/$(CODEX_PROFILE)" "$(CODEXHOME)/$(CODEX_PROFILE)" && echo "profile -> $(CODEXHOME)/$(CODEX_PROFILE)"
	@for k in $(SKILLS); do \
	  rm -rf "$(CODEXSKILLDIR)/$$k" && cp -R "skills/$$k" "$(CODEXSKILLDIR)/$$k" && echo "skill   -> $(CODEXSKILLDIR)/$$k"; \
	done
	@echo "done."

uninstall-codex:
	@rm -f "$(CODEXHOME)/AGENTS.md" && echo "removed $(CODEXHOME)/AGENTS.md"
	@rm -f "$(CODEXHOME)/$(CODEX_PROFILE)" && echo "removed $(CODEXHOME)/$(CODEX_PROFILE)"
	@for k in $(SKILLS); do \
	  rm -rf "$(CODEXSKILLDIR)/$$k" && echo "removed $(CODEXSKILLDIR)/$$k"; \
	done

reinstall-codex: uninstall-codex codex

list-codex:
	@echo "config  (-> $(CODEXHOME)):"
	@printf '  %s\n' AGENTS.md $(CODEX_PROFILE)
	@echo "skills  (-> $(CODEXSKILLDIR)):" && printf '  %s\n' $(SKILLS)

diff-codex:
	@diff -u "$(CODEXHOME)/AGENTS.md" "$(INSTRUCTIONS)" && echo "== AGENTS.md: in sync" || true
	@diff -u "$(CODEXHOME)/$(CODEX_PROFILE)" "codex/$(CODEX_PROFILE)" && echo "== $(CODEX_PROFILE): in sync" || true
	@for k in $(SKILLS); do \
	  diff -ru "$(CODEXSKILLDIR)/$$k" "skills/$$k" && echo "== $$k: in sync" || true; \
	done
