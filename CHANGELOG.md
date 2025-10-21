# Changelog

> [!TIP]
> Changelog format guideline: https://common-changelog.org

## [0.11.0]

### Added

- Semver support for the release notes generation code ([219](https://github.com/gardenlinux/python-gardenlinux-lib/pull/219)) (vivus-ignis, ByteOtter)

### Changed

- Update GLVD URL ([226](https://github.com/gardenlinux/python-gardenlinux-lib/pull/226)) (vivus-ignis)

## [0.10.2] - 2025-10-17

### Fixed

- Explicitly set `make_latest` value for github release creation JSON payload in `create_github_release` function (nkraetzschmar)

## [0.10.1] - 2025-10-17

### Added

- gl-gh script for creating Github releases ([222](https://github.com/gardenlinux/python-gardenlinux-lib/pull/222)) (vivus-ignis)
- Github release notes generation code ([202](https://github.com/gardenlinux/python-gardenlinux-lib/pull/202), [198](https://github.com/gardenlinux/python-gardenlinux-lib/pull/198), [217](https://github.com/gardenlinux/python-gardenlinux-lib/pull/217), [206](https://github.com/gardenlinux/python-gardenlinux-lib/pull/206)) (vivus-ignis)
- Support for reading metadata files, especially feature sets and platforms, without parsing data from the features directory ([172](https://github.com/gardenlinux/python-gardenlinux-lib/pull/172)) (NotTheEvilOne)

### Changed

- New dependency: `gitpython`
- Improve type annotations in apt module ([201](https://github.com/gardenlinux/python-gardenlinux-lib/pull/201)) (ByteOtter)
- Improve type annotations in git module ([203](https://github.com/gardenlinux/python-gardenlinux-lib/pull/203)) (ByteOtter)
- Improve type annotations in s3 module ([204](https://github.com/gardenlinux/python-gardenlinux-lib/pull/204)) (ByteOtter)

### Changed (dev setup)

- Improve configuration for local linting and code coverage generation
- New dev dependencies: `isort`, `requests-mock`, `pyright`

## [0.10.0] - 2025-09-16

### Added

- Code for artifacts upload to github release page ([191](https://github.com/gardenlinux/python-gardenlinux-lib/pull/191)) (vivus-ignis)
- Add support to additionally tag an existing OCI manifest ([176](https://github.com/gardenlinux/python-gardenlinux-lib/pull/176)) (NotTheEvilOne)

### Changed

- Python dependencies update
- Replace GitPython implementation with pygit2 one ([187](https://github.com/gardenlinux/python-gardenlinux-lib/pull/187)) (NotTheEvilOne)
