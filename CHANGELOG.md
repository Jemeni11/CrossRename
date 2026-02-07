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

## [1.4.0] - 2026-02-07

### Added

- TOCTOU (Time-of-Check to Time-of-Use) race condition mitigations in file renaming operations ([#7](https://github.com/Jemeni11/CrossRename/issues/7))
- File existence check before rename to prevent errors from concurrent file modifications
- Collision prevention when target filename already exists (appends counter suffix)
- Explicit handling for `FileNotFoundError`, `PermissionError`, and `FileExistsError` during rename

### Changed

- Replaced custom `parse_version()` function with `packaging.version.parse` for robust version comparison
- Added `packaging>=25.0` as a dependency in `pyproject.toml`
- Code formatting cleanup (consistent double quotes, improved argument layout in argparse)
- Added return type hints to `show_warning()` and `show_credits()`
- Updated `.gitignore` with more entries
- Updated README with macOS support documentation and improved code block formatting
- Added documentation clarifying that files with Windows-forbidden characters must be fixed from Linux/macOS (or WSL)

## [1.3.0] - 2025-09-28

### Added

- Unicode alternatives mode with `-a/--use-alternatives` flag to replace forbidden characters with Unicode lookalikes instead of removing them
- Enhanced warning system that alerts users about potential Unicode compatibility issues when alternatives mode is enabled
- Character mapping documentation showing which Unicode characters replace forbidden ones

### Changed

- Updated help text and documentation to include the new Unicode alternatives feature
- Improved function signatures and documentation for better maintainability

## [1.2.1] - 2025-08-03

### Fixed

- Broken links in rst readme

## [1.2.0] - 2025-08-03

### Added

- Directory renaming functionality with `-D/--rename-directories` flag
- Interactive safety warnings before performing renaming operations
- `--force` flag to skip safety prompts for automated scripts
- `--credits` command to show project information and support links
- Depth-first directory processing to prevent path breakage during renames
- Credits promotion in update check when user is on latest version
- Funding link in project metadata for easier support access

### Changed

- Enhanced recursive option to work with both files and directories when `-D` is used
- Updated project description and documentation for directory renaming capability
- Rewrote project story section in more casual tone
- Updated license format in pyproject.toml to modern standard
- Improved help text with epilog promoting credits command

### Fixed

- Added error handling for malformed version strings in update checker
- Fixed critical bug where directory renaming broke subsequent file operations
- Corrected path handling after directory renames to prevent "file not found" errors

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

[1.4.0]: https://github.com/Jemeni11/CrossRename/compare/v1.3.0...v1.4.0

[1.3.0]: https://github.com/Jemeni11/CrossRename/compare/v1.2.1...v1.3.0

[1.2.1]: https://github.com/Jemeni11/CrossRename/compare/v1.2.0...v1.2.1

[1.2.0]: https://github.com/Jemeni11/CrossRename/compare/v1.1.0...v1.2.0

[1.1.0]: https://github.com/Jemeni11/CrossRename/compare/v1.0.0...v1.1.0

[1.0.0]: https://github.com/Jemeni11/CrossRename/releases/tag/v1.0.0
