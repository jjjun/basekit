# basekit Guides

basekit guides are practical references for developers and AI agents working with this package.

## Guide Categories

### [Configuration hooks](config/config_hook_guide.md)

- `Config` base class
- `CONFIG_HOOK` loading
- path customization patterns

### [Vault](vault_guide.md)

- local TOML loading
- named section access

### [Logging](logging/logging_guide.md)

- daily date-named log files
- package logger setup
- optional SQLAlchemy engine logging

### [Discovery](discovery_guide.md)

- generic package and module discovery
- structured import failures
- optional post-import hooks

### Docker

- [Simple Docker Compose YAML generation](docker_compose_guide.md)
- [Shared Docker command and service manager helpers](docker_manager_guide.md)
- injectable Docker service manager base class

### [Testing](testing/testing_guide.md)

- test command conventions
- environment variable handling
- focused tests for shared utilities

## Writing New Guides

Use this shape for new guide files:

```markdown
# Feature Name Guide

## Overview

## Basic Usage

## Advanced Usage

## Testing Notes

## Troubleshooting

## Related Files
```

Guides should be short, executable where possible, and tied to public APIs rather than private implementation details.
