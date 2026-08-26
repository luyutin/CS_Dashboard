# Media cleaner editable configuration

These files are loaded when `process.media_cleaner` is imported. Restart the
Streamlit application after editing them.

- `target_columns.txt`: one tab-delimited `template column<TAB>description` per
  line. It must contain exactly the canonical columns defined by
  `process/template.py::template()`; output order always follows that template.
- `aliases.json`: deterministic source-header aliases grouped by target field.
- `ollama_system_prompt.txt`: stable model role, guardrails, and exclusions.
- `ollama_user_prompt.txt`: task template. Keep the placeholders
  `{target_descriptions}` and `{options}`.

When building a PyInstaller executable, include this entire directory at
`process/media_cleaner/config` inside the bundle.
