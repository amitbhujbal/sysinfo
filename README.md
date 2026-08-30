# sysinfo

A simple, cross-platform Python CLI tool for displaying essential system information directly in your terminal.

- **Operating System** — macOS, Ubuntu, Debian, Fedora, RHEL, CentOS, Linux
- **Architecture** — x86_64, arm64, etc.
- **Kernel version**
- **Hostname and current user**
- **Memory usage**
- **Development tools and languages** — Python, Ruby, Swift, Rust, Cargo, Homebrew
- **System utilities** — Git, curl, OpenSSL / LibreSSL (SSH), Node, Bash, Zsh, Tar, Zip / Unzip

It’s lightweight, easy to install, and works right from your terminal.

---

## Installation

### Homebrew (macOS/Linux)

If you use [Homebrew](https://brew.sh/), simply run:

```bash
brew trust amitbhujbal/sysinfo
brew tap amitbhujbal/sysinfo
brew install sysinfo
```
Once installed, run:

```bash
sysinfo
```

---

## Screenshots
![Screenshots.](https://amitbhujbal.com/images/screenshot-sysinfo.png "Screenshots")

---

## Troubleshooting

### Checksum mismatch

If you encounter a checksum mismatch, update the SHA256 checksum in the Homebrew formula to match the current release.

---
### Old version is installed

If Homebrew reports:

```
already installed and up-to-date
```
but you are still using an older version, reinstall the tap:

```bash
brew uninstall sysinfo
brew untap amitbhujbal/sysinfo
brew tap amitbhujbal/sysinfo
brew install sysinfo
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 **Amit Bhujbal**.
