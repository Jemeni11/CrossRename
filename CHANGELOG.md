# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[//]: # (Types of changes)

[//]: # (- **Added** for new features.)

[//]: # (- **Changed** for changes in existing functionality.)

[//]: # (- **Deprecated** for soon-to-be removed features.)

[//]: # (- **Removed** for now removed features.)

[//]: # (- **Fixed** for any bug fixes.)

[//]: # (- **Security** in case of vulnerabilities.)

## [1.2.0] - 2025-08-03

### Added

- Directory renaming functionality with `-D/--rename-directories` flag
- Interactive safety warnings before performing renaming operations
- `--force` flag to skip safety prompts for automated scripts
- Depth-first directory processing to prevent path breakage during renames

### Changed

- Enhanced recursive option to work with both files and directories when `-D` is used
- Updated project description and documentation for directory renaming capability
- Rewrote project story section in more casual tone

### Fixed

- Added error handling for malformed version strings in update checker

## [1.1.0] - 2024-11-15

### Added

- Dry-run mode and recursive symlink handling.
- add --update flag to check for new version.

### Changed

- Changed logo

### Removed

- Removed debug argument option, it wasn't even implemented

## [1.0.0] - 2024-10-07

- Released CrossRename

[1.2.0]: https://github.com/Jemeni11/CrossRename/compare/v1.1.0...v1.2.0

[1.1.0]: https://github.com/Jemeni11/CrossRename/compare/v1.0.0...v1.1.0

[1.0.0]: https://github.com/Jemeni11/CrossRename/releases/tag/v1.0.0
