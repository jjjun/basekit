# basekit project profile

## Responsibilities

basekit owns shared Python application foundation utilities used by sibling
projects. It provides reusable building blocks for configuration hooks, local
vault storage, logging setup, package/module discovery, Docker Compose YAML
generation, and Docker command/service management. Changes belong here when
they affect generic Python infrastructure that should be reused across multiple
projects rather than implemented in one application.

## Tech stack

- Python 3.12+ package managed with `uv`.
- Source package under `src/basekit`.
- `pytest` test suite under `tests/`.
- Documentation and usage guides under `docs/guides`.

## Public surface

- `basekit.config_hook`: shared `Config` base class and `CONFIG_HOOK` loading.
- `basekit.vault`: small TOML-backed local vault helper.
- `basekit.logging`: daily log file handler and opt-in logging helpers.
- `basekit.discovery`: generic package and module discovery helpers.
- `basekit.docker_compose`: Docker Compose YAML generation helpers.
- `basekit.docker_manager`: Docker command and service manager helpers.

## Example in-scope requests

- "Add a reusable config hook option needed by multiple Python repos."
- "Extend the local vault helper with a generic read/write behavior."
- "Make the shared logging setup support a new handler option."
- "Add Docker Compose generation support for a common service pattern."

## Example out-of-scope requests

- Application-specific API endpoints, models, or UI behavior in consumer repos.
- Database repository patterns owned by repom.
- FastAPI domain routing features owned by fast-domain.
- Browser automation and crawler behavior owned by py_cr_wrapper.
