# Proposals

Use this directory when basekit work reveals that another project or package must change before the overall goal can be completed.

Examples of proposal targets include:

- `repom`
- `mine-py`
- `fast-domain`
- another package that consumes basekit

Use `docs/issues/` for basekit implementation work. Use `docs/proposals/` only for external coordination.

## Files

```text
docs/proposals/
├── README.md
├── _template.md
└── NNN_<target>_<slug>.md
```

`README.md` and `_template.md` are not counted when choosing the next number.

## Naming Rules

```text
NNN_<target>_<slug>.md
```

- `NNN`: zero-padded sequence number such as `001`
- `<target>`: target project or package in snake_case
- `<slug>`: short snake_case summary

Example:

```text
001_repom_migrate_config_base_to_basekit.md
```

## AI Agent Procedure

1. List Markdown files directly under `docs/proposals/`.
2. Ignore `README.md` and `_template.md`.
3. Use the next number after the current maximum.
4. Copy `_template.md` to `NNN_<target>_<slug>.md`.
5. Fill in why basekit cannot complete the change alone, what the target should change, and what remains in basekit.
6. Continue implementing any part that can be handled inside basekit.

Proposal files are temporary. Delete them after the target project has accepted, rejected, or otherwise completed the proposal and basekit no longer needs the tracking note.
