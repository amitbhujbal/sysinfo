# 📦 sysinfo

A simple, cross-platform Python CLI tool to display essential system information directly from your terminal.

- **Operating System** (macOS, ubuntu, debian, fedora, RHEL, CentOS, Linux)
- **Architecture** (x86_64, arm64, etc.)
- **Kernel version**
- **Hostname and current user**
- **Memory usage**
- **Programming languages installed** (Python, Ruby, Swift, Rust, Cargo, Homebrew)
- **Programming languages installed** (Git, Curl, OpenSSL / LibreSSL (SSH), Node, Bash, Zsh, Tar, Zip / Unzip)

It’s lightweight, easy to install, and works right from your terminal.

---

## 🚀 Installation

### Homebrew (macOS/Linux)

If you use [Homebrew](https://brew.sh/), simply run:

```bash
brew tap amitbhujbal/sysinfo
brew install sysinfo
```

> **Homebrew 6+**
>
> If Homebrew asks you to trust the tap, run:
>
> ```bash
> brew trust amitbhujbal/sysinfo
> ```
>
> Then install again:
>
> ```bash
> brew install sysinfo
> ```

Then run:

```bash
sysinfo
```

---

## 📸 Screenshots
![Screenshots.](https://amitbhujbal.com/images/screenshot-sysinfo.webp "Screenshots")

---

## ⚠️ Troubleshooting

### Checksum mismatch

Update SHA to match release.

---
### Old version installs
```
already installed and up-to-date
```

**Fix:**
```bash
brew uninstall sysinfo
brew untap amitbhujbal/sysinfo
brew tap amitbhujbal/sysinfo
brew install sysinfo
```

---


## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 **Amit Bhujbal**.
