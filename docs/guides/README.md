# basekit Guides

basekit guides are practical references for developers and AI agents working with this package.

## Guide Categories

### [config/](config/)

- `Config` base class
- `CONFIG_HOOK` loading
- path customization patterns

### [logging/](logging/)

- daily date-named log files
- package logger setup
- optional SQLAlchemy engine logging

### discovery

- generic package and module discovery
- structured import failures
- optional post-import hooks

### docker

- simple Docker Compose YAML generation
- shared Docker command helpers
- injectable Docker service manager base class

### [testing/](testing/)

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
