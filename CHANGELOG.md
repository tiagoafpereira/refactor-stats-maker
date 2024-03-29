# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2024-01-02

### Added

- Add --file-list argument to display list of files to refactor
- Add --stats option

## [0.5.0] - 2023-12-07

### Added

- Add a CHANGELOG
- Cache folder name is no longer hardcoded to "wcc"
- Add --leaderboard and --list-commits options

## [0.4.2] - 2023-11-29

### Changed

- Move repo handling functions to dedicated class

### Fixed

- Exclude Markdown files from statistics
- File path issue when removing leading folders
- Update plotext to 5.3.0. This fixes float formatting in bar plots

## [0.4.1] - 2023-11-21

### Added

- Replace --expands and --class-based options with --type

## [0.4.0] - 2023-11-20

### Added

- @pedromcosta owned files now take their root folder as team name

## [0.3.0] - 2023-11-17

### Added

- Calculate baseline from commit hash

### Changed

- Cleanup code and add tests

## [0.2.0] - 2023-09-28

### Added

- Initial commit
- Include options to copy to clipboard and format for Gitlab

<!-- generated by git-cliff -->
