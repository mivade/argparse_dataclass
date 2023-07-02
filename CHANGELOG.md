# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - Unreleased

### Changed

+ Updated project structure to use `pyproject.toml`
+ Add `build` to `dev` dependencies

## [2.0.1] - Unreleased

### Fixed
* Update `MANIFEST.in` file when building source distributions

## [2.0.0] - 2023-06-11
### Added
* Support for using `metavar` in field metadata (#44)
* Support for using `Literal` types as an alternative to providing `choices` in
  field metadata (#46)

### Fixed
* `Union` type support (#42)

### Removed
* Support for Python 3.6 and 3.7 (#50)

## [1.0.0] - 2023-01-21
This is the 1.0 release of `argparse_dataclass`.
