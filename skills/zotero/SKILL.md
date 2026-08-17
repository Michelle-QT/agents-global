---
name: zotero
description: "Use before any Zotero MCP call."
---

- Before any `mcp__zotero__*` call, run `zotero_switch_library` with `library_id="8929442"`, `library_type="user"` (once per session). Skip `zotero_list_libraries`: it fails due to a missing sqlite path.
