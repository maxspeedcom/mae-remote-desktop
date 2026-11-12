# MAE Remote Desktop

โปรแกรมรีโมทคอมพิวเตอร์ระยะไกล เชื่อมต่อด้วยที่อยู่เครื่อง 9 หลัก เข้ารหัสทุกการเชื่อมต่อ เซิร์ฟเวอร์ในประเทศไทย ใช้ฟรี

Remote desktop software for Windows: connect to any computer with its 9-digit ID. Encrypted end to end, servers in
Thailand, free to download and use. It is used by small businesses and IT support teams in Thailand to help users and
manage their own computers.

- Website and download: https://remote.maesuaisystem.com
- Builds and source code of every release: https://remote.maesuaisystem.com/source/ (Windows 10/11, 64-bit) and the
  `mae-<version>-r<N>` tags in this repository (e.g. `mae-1.5.3-r10`)
- Privacy policy: https://remote.maesuaisystem.com/privacy.html
- Contact: support@maesuaisystem.com

## License

GNU Affero General Public License v3.0, see [`LICENCE`](LICENCE). Every component in the installer is open source.

This program is a modified version of an open-source remote desktop program (currently version 1.5.3) licensed under the
AGPL-3.0. The modifications are listed in [`MAE-CHANGES.md`](MAE-CHANGES.md).

## Build

Windows x64 installers are built only by GitHub Actions on GitHub-hosted runners:
[`.github/workflows/mae-windows.yml`](.github/workflows/mae-windows.yml) (run it with *workflow_dispatch* on the
`mae` branch). The job builds the Rust core library and the Flutter interface and packs them into the
self-extracting installer `MAERemote-<version>-x86_64.exe`.

- [`apply-branding.py`](apply-branding.py) applies every MAE change to the upstream source
  (`python3 apply-branding.py <source-dir>`); each edit must match exactly once, so upstream changes are caught.
- [`update-upstream.sh`](update-upstream.sh) builds the whole tree for an upstream tag (`./update-upstream.sh 1.5.3`,
  run from the folder that holds this repository as `rustdesk/`): upstream source + vendored `libs/hbb_common` + the
  two scripts below. Run with the tag the branch is built on, it reproduces the branch exactly.
- [`gen-workflow.py`](gen-workflow.py) generates `mae-windows.yml` from the upstream Flutter build workflow
  (Windows x64 only, no closed-source driver in the package).

## Code signing

See [`CODE_SIGNING_POLICY.md`](CODE_SIGNING_POLICY.md).

## Code of conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
