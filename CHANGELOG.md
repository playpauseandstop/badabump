# 21.2.0 (2021-05-12)

Now `badabump` supports backticks in release notes, which allows to put code blocks in GitHub Releases description, using standard Markdown syntax,

```python
def new_release() -> str:
    return "It is working!"
```

## Features:

- [#34] Put refactor commits into separate section (#58)

## Fixes:

- [#64] Support pre-releases with multiple digits (#66)
- [#63] Escape backticks when setting output at GitHub Actions (#67)
- [#63] Do not escape backticks & shell vars (#70)

## Other:

- (**deps-dev**) Bump coverage from 5.3.1 to 5.4 (#47)
- (**deps-dev**) Bump pytest from 6.2.1 to 6.2.2 (#50)
- (**deps-dev**) Bump pytest-cov from 2.10.1 to 2.11.1 (#49)
- (**deps-dev**) Bump time-machine from 1.3.0 to 2.0.1 (#48)
- (**deps**) Bump peter-evans/create-pull-request from v3.6.0 to v3.8.0 (#51)
- Bump Python dev version to 3.9.2 (#57)
- (**deps**) Bump actions/cache from v2.1.3 to v2.1.4 (#55)
- (**deps**) Bump pypa/gh-action-pypi-publish from v1.4.1 to v1.4.2 (#54)
- (**deps**) Bump peter-evans/create-pull-request from v3.8.0 to v3.8.2 (#56)
- Update to Python 3.9.4 (#59)
- (**deps**) Bump actions/setup-python from v2.2.1 to v2.2.2 (#60)
- (**deps**) Bump actions/cache from v2.1.4 to v2.1.5 (#61)
- (**deps**) Bump pre-commit/action from v2.0.0 to v2.0.3 (#62)
- Update Python dev version to 3.9.5 (#65)

# 21.1.0 (2021-01-11)

## Fixes:

- [#44] (**calver**) Properly update CalVer scheme between years (#45)

## Other:

- (**deps**) Bump actions/setup-python from v2.1.4 to v2.2.1 (#43)
- (**deps**) Bump tibdex/github-app-token from v1.1.1 to v1.3 (#41)
- (**deps**) Bump peter-evans/create-pull-request from v3.5.1 to v3.6.0 (#42)
- (**deps**) Bump attrs from 20.2.0 to 20.3.0 (#35)
- (**deps-dev**) Bump pytest from 6.1.2 to 6.2.1 (#40)
- (**deps-dev**) Bump coverage from 5.3 to 5.3.1 (#39)

# 20.1.0 (2020-12-31)

First final release of ``badabump``: Python based tool to manage changelog and bump
project version number using conventional commits from latest git tag. Support Python &
JavaScript projects and CalVer & SemVer schemas. Designed to run at GitHub Actions.

## Other:

- [#28] Cover CI output and cli with tests (#32)
- [#28] Cover all main functionality with tests (#33)
- Enable dependabot for GitHub Actions (#36)
- (**deps**) Bump peter-evans/create-pull-request from v3.4.1 to v3.5.1 (#37)

## 20.1.0rc1 (2020-11-06)

### Fixes:

- [#29, #28] Properly understand initial pre-release version (#30)

## 20.1.0rc0 (2020-11-06)

### Features:

- [#15] **BREAKING CHANGE:** Allow create initial releases and pre-releases (#26)
- [#16] Allow to create final release PR (#18)
- [#17] Understand more issue refs in commit body (#19)
- Conform PEP-561 by adding py.typed files (#20)

### Other:

- (**deps**) Bump toml from 0.10.1 to 0.10.2 (#22)
- (**deps-dev**) Bump pytest from 6.1.1 to 6.1.2 (#21)
- Bump pre-commit hooks and update mypy config (#25)

## 20.1.0b0 (2020-10-25)

### Fixes:

- **BREAKING CHANGE:** Update logic behind formatting & updating changelog (#12)

### Other:

- Badabump args is optional input for release PR workflow (#13)

## 20.1.0a3 (2020-10-24)

### Fixes:

- Fix commit format rules (#10)

## 20.1.0a2 (2020-10-23)

### Features:

- Properly clean commit body on preparing release tag (#8)

## 20.1.0a1 (2020-10-23)

### Features:

- Provide badabump cli shortcut (#2)
- Provide various useful commands for CI needs (#3)

### Fixes:

- Remove attr dependency (#1)
- Fix changelog file format for badabump (#6)

### Other:

- Fix running badabump in release workflows (#4)

## 20.1.0a0 (2020-10-22)

- Initial release
