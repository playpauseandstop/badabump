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
