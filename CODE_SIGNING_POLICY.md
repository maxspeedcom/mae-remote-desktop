# Code signing policy

MAE Remote Desktop has applied to the [SignPath Foundation](https://signpath.org/) open-source code signing program.
Once the application is approved, Windows releases are signed with this attribution:

> Free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by [SignPath Foundation](https://signpath.org/)

Until then, releases are not code signed.

## What gets signed

- Only the Windows installer (`MAERemote-<version>-x86_64.exe`) built by this repository's GitHub Actions workflow
  `.github/workflows/mae-windows.yml`, from a commit on the `mae` branch, on GitHub-hosted runners.
- Nothing built on a developer machine is submitted for signing.
- Every signing request is approved by hand by an approver (see below) before it is signed.
- The private key is held by SignPath on its hardware security module; the project never has access to it.

## Team roles

| Role | Members |
|---|---|
| Committers and reviewers | [maxspeedcom](https://github.com/maxspeedcom) (MAE Remote Desktop team) |
| Approvers | [maxspeedcom](https://github.com/maxspeedcom) |

All team members use multi-factor authentication for GitHub and SignPath.

## Privacy

The program connects only to the servers it needs to work, and sends this to them:

- **Rendezvous / relay server `rd.maesuaisystem.com`:** the device ID and the network address, so that two computers can find each other;
  the remote-desktop session itself is end-to-end encrypted.
- **Account service `remote.maesuaisystem.com`:** a heartbeat and system information (device ID, computer name, operating system,
  program version), connection records (who connected to whom, when, from which IP address) and the byte count of each session.
  Signing in is optional; an account adds the e-mail address and the saved address book.
- **Updates (build 11 and later):** `https://remote.maesuaisystem.com/version.json` is checked at start-up and once a
  day. A newer release is downloaded from this repository's GitHub releases together with `mae-update.json` and its
  signature; the client installs it only if the signature verifies with the MAE update key built into it and the
  installer's SHA-256 and size match, and only while no session is active. Settings > General > Auto update turns it off.

Nothing else is sent to other networked systems unless the user asks for it (for example, connecting to a computer or opening a link).
Full details: [privacy policy](https://remote.maesuaisystem.com/privacy.html).

Contact: [support@maesuaisystem.com](mailto:support@maesuaisystem.com)
