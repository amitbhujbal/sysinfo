#!/usr/bin/env python3
import platform
import os
import subprocess
import getpass
import shutil
import sys
import time
import threading
import argparse
import re

VERSION = "1.1"  # your current version

reset = "\033[0m"
bold_white = "\033[1;37m"
green = "\033[38;10;82m"  # 256-color bright green
banner = "\033[38;10;82m"

def supports_color() -> bool:
    return sys.stdout.isatty()

if supports_color():
    reset = "\033[0m"
    bold_white = "\033[1;97m"        # labels
    green_info = "\033[1;38;5;82m"   # system info
    pkg_color = "\033[1;36m"         # package versions (cyan)
    banner = "\033[38;5;82m"         # banner (non-bold green)
else:
    reset = bold_white = green_info = pkg_color = banner = ""

# --- Spinner Animation ---
loading = True

def spinner():
    symbols = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    i = 0
    while loading:
        _ = sys.stdout.write(f"\r{bold_white}Collecting system information... {symbols[i % len(symbols)]}{reset}")
        _ = sys.stdout.flush()
        i += 1
        _ = time.sleep(0.1)

# --- Run safe command ---
def run_cmd(cmd: str) -> str:
    try:
        return subprocess.getoutput(cmd).strip()
    except Exception:
        return "Unknown"

# --- Utility Functions ---
def get_resolution() -> str:
    system = platform.system()
    try:
        if system == "Darwin":
            res = subprocess.getoutput("system_profiler SPDisplaysDataType | grep Resolution")
            return res.strip() if res else "Unknown"
        elif system == "Linux":
            if shutil.which("xdpyinfo"):
                res = subprocess.getoutput("xdpyinfo | grep dimensions | awk '{print $2}'")
                return res.strip() if res else "Unknown"
    except (subprocess.CalledProcessError, OSError):
        return "Unknown"

    return "Unknown"

def get_terminal():
    if platform.system() in ["Darwin", "Linux"]:
        return os.environ.get("TERM_PROGRAM") or os.environ.get("TERM") or "Unknown"
    return "Unknown"

def get_version(cmd: str) -> str:
    if shutil.which(cmd):
        try:
            output = subprocess.getoutput(f"{cmd} --version")
            return output.split("\n")[0] if output else "Unknown"
        except (subprocess.CalledProcessError, OSError):
            return "Unknown"
    return "Not Installed"

def get_host_model():
    try:
        if platform.system() == "Darwin":
            return subprocess.getoutput("system_profiler SPHardwareDataType | grep 'Model Identifier' | awk '{print $3}'")
        elif platform.system() == "Linux":
            return subprocess.getoutput("cat /sys/devices/virtual/dmi/id/product_name 2>/dev/null")
    except (subprocess.CalledProcessError, OSError):
        return "Unknown"
    return "Unknown"

def parse_memory(mem_str: str) -> str:
    # Example mem_str: "PhysMem: 7586M used (1774M wired, 783M compressor), 605M unused"
    m = re.search(r"(\d+)M used", mem_str)
    if m:
        used_mb = int(m.group(1))
        # Round to nearest 4 GB
        total_gb = max(4, round(used_mb / 1024))
        return f"{total_gb} GB"
    return "Unknown"

def parse_uptime(uptime_str: str) -> str:
    # Example: "20:33  up  2:53, 2 users, load averages: 2.17 2.76 2.87"
    m = re.search(r"up\s+([0-9]+):([0-9]+)", uptime_str)
    if m:
        hours, mins = m.groups()
        return f"{hours}h {mins}m"
    return "Unknown"

def clean_version(output: str) -> str:
    if not output:
        return "unknown"

    # Match first "digit.digit(.digit)*"
    m = re.search(r"\d+(?:\.\d+)+", output)
    if m:
        return m.group(0)
    # Match year ranges like 1990-2008
    m = re.search(r"\b\d{4}-\d{4}\b", output)
    if m:
        return m.group(0)

    m_year = re.search(r"\b\d{4}\b", output)
    if m_year:
        return m_year.group(0)

    return "unknown"

def parse_mem_linux():
    """
    Returns memory as human-readable total GB string, e.g., '8 GB', '16 GB'
    """
    mem_output = run_cmd("free -b")  # get in bytes
    for line in mem_output.splitlines():
        if line.lower().startswith("mem:"):
            parts = line.split()
            total_bytes = int(parts[1])
            total_gb = total_bytes / (1024**3)
            # round to nearest integer for clean display
            if total_gb >= 1:
                return f"{int(round(total_gb))} GB"
            else:
                return f"{int(total_bytes / (1024**2))} MB"
    return "Unknown"

def parse_uptime_linux() -> str:
    """
    Return uptime in simplified format: 'X hours, Y minutes'
    """
    raw = run_cmd("uptime -p")  # gives 'up 3 minutes' or 'up 2 hours, 15 minutes'
    return raw.replace("up ", "") if raw else "Unknown"

def clean_ssh_version(output: str) -> str:
    if not output:
        return "unknown"

    # Example:
    # OpenSSH_9.0p1, LibreSSL 3.3.6
    m = re.search(
        r"OpenSSH[_\s]?(\d+(?:\.\d+)+)[^,]*,\s*([A-Za-z]+SSL)\s*(\d+(?:\.\d+)+)",
        output
    )

    if m:
        ssh_ver = m.group(1)
        ssl_name = m.group(2)
        ssl_ver = m.group(3)
        return f"{ssh_ver}, {ssl_name} {ssl_ver}"

    # Fallback: just SSH version
    m = re.search(r"\d+(?:\.\d+)+", output)
    if m:
        return m.group(0)

    return "unknown"

def clean_curl_version(output: str) -> str:
    if not output:
        return "Not Installed"
    # curl 8.5.0 (...)
    m = re.search(r"curl\s+(\d+(?:\.\d+)+)", output)
    return m.group(1) if m else "Unknown"

def clean_openssl_version(output: str) -> str:
    if not output:
        return "Not Installed"
    # OpenSSL 3.6.0 ...
    m = re.search(r"OpenSSL\s+(\d+(?:\.\d+)+)", output)
    return m.group(1) if m else "Unknown"

def clean_bash_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"version\s+(\d+(?:\.\d+)+)", output, re.IGNORECASE)
    return m.group(1) if m else "Unknown"

def clean_unzip_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"UnZip\s+(\d+(?:\.\d+)*)", output)
    return m.group(1) if m else "Unknown"

def clean_tar_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"tar\s+\(GNU tar\)\s+(\d+(?:\.\d+)*)", output)
    return m.group(1) if m else "Unknown"

def clean_brew_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"Homebrew\s+(\d+(?:\.\d+)*)", output)
    return m.group(1) if m else "Unknown"

def clean_git_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"git\s+version\s+(\d+(?:\.\d+)*)", output, re.IGNORECASE)
    return m.group(1) if m else "Unknown"

def clean_ruby_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"ruby\s+(\d+(?:\.\d+)*)", output)
    return m.group(1) if m else "Unknown"

def clean_python_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"Python\s+(\d+(?:\.\d+)*)", output)
    return m.group(1) if m else "Unknown"

def clean_swift_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"Swift\s+version\s+(\d+(?:\.\d+)*)", output, re.IGNORECASE)
    return m.group(1) if m else "Unknown"

def clean_rust_version(output: str) -> str:
    if not output:
        return "Not Installed"
    # rustup 1.28.2 (...)
    m = re.search(r"rustup\s+(\d+(?:\.\d+)*)", output, re.IGNORECASE)
    return m.group(1) if m else "Unknown"

def clean_cargo_version(output: str) -> str:
    if not output:
        return "Not Installed"
    # cargo 1.92.0 (...)
    m = re.search(r"cargo\s+(\d+(?:\.\d+)*)", output, re.IGNORECASE)
    return m.group(1) if m else "Unknown"

def clean_zsh_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"zsh\s+(\d+(?:\.\d+)*)", output, re.IGNORECASE)
    return m.group(1) if m else "Unknown"

def clean_zip_version(output: str) -> str:
    if not output:
        return "Not Installed"
    # Try to find Zip version first
    m = re.search(r"Zip\s+(\d+(?:\.\d+)*)", output, re.IGNORECASE)
    if m:
        return m.group(1)
    # Fallback: year range like 1990-2008
    m_year = re.search(r"\b\d{4}-\d{4}\b", output)
    if m_year:
        return m_year.group(0)
    return "Unknown"

def clean_node_version(output: str) -> str:
    if not output:
        return "Not Installed"
    m = re.search(r"v?(\d+(?:\.\d+)*)", output, re.IGNORECASE)
    return m.group(1) if m else "Unknown"

# --- macOS Info ---
def get_macos_info():
    print(f"""{banner}

'    ███╗   ███╗ █████╗  ██████╗ ██████╗ ███████╗
'    ████╗ ████║██╔══██╗██╔════╝██╔═══██╗██╔════╝
'    ██╔████╔██║███████║██║     ██║   ██║███████╗
'    ██║╚██╔╝██║██╔══██║██║     ██║   ██║╚════██║
'    ██║ ╚═╝ ██║██║  ██║╚██████╗╚██████╔╝███████║
'    ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
'{reset}""")
    print("-" * 50)

    global loading
    loading = True
    t = threading.Thread(target=spinner)
    t.start()

    # collect system info
    product_name = subprocess.getoutput("sw_vers -productName")
    product_version = subprocess.getoutput("sw_vers -productVersion")
    build_version = subprocess.getoutput("sw_vers -buildVersion")
    cpu = subprocess.getoutput("sysctl -n machdep.cpu.brand_string")
    gpu = subprocess.getoutput("system_profiler SPDisplaysDataType | grep 'Chipset Model' | head -n 1")
    gpu_name = gpu.replace("Chipset Model:", "").strip()
    mem = subprocess.getoutput("top -l 1 | grep PhysMem")
    uptime = subprocess.getoutput("uptime")
    arch = platform.machine()
    kernel = platform.release()
    resolution = get_resolution()
    host = platform.node()
    host_model = get_host_model()
    user = getpass.getuser()
    terminal = get_terminal()
    ruby_ver = get_version("ruby")
    python_ver = get_version("python3")
    swift_ver = get_version("swift")
    rust_ver = get_version("rustup")
    cargo_ver = get_version("cargo")
    brew_ver = get_version("brew")
    git_ver = get_version("git")
    curl_ver = get_version("curl")
    openssl_ver = get_version("openssl")
    ssh_ver = get_version("ssh")
    node_ver = get_version("node")
    bash_ver = get_version("bash")
    zsh_ver = get_version("zsh")
    tar_ver = get_version("tar")
    unzip_ver = get_version("unzip")
    zip_ver = get_version("zip")

    # stop spinner
    loading = False
    t.join()
    _ = sys.stdout.write("\r" + " " * 60 + "\r")  # clear line

    # Clean all versions
    mem_clean = parse_memory(mem)
    resolution = resolution.replace("Resolution:", "").strip()
    uptime_clean = parse_uptime(uptime)
    ruby_ver = clean_version(ruby_ver)
    python_ver = clean_version(python_ver)
    swift_ver = clean_version(swift_ver)
    rust_ver = clean_version(rust_ver)
    cargo_ver = clean_version(cargo_ver)
    brew_ver = clean_version(brew_ver)
    git_ver = clean_version(git_ver)
    curl_ver = clean_version(curl_ver)
    openssl_ver = clean_version(openssl_ver)
    ssh_ver = clean_ssh_version(subprocess.getoutput("ssh -V 2>&1"))
    node_ver = clean_version(node_ver)
    bash_ver = clean_version(bash_ver)
    zsh_ver = clean_version(zsh_ver)
    tar_ver = clean_version(tar_ver)
    unzip_ver = clean_version(subprocess.getoutput("unzip -V"))
    zip_ver = clean_version(zip_ver)

    # print results
    print(f"{green_info}Product Name:{reset} {bold_white}{product_name}{reset}")
    print(f"{green_info}Product Version:{reset} {bold_white}{product_version}{reset}")
    print(f"{green_info}Build Version:{reset} {bold_white}{build_version}{reset}")
    print(f"{green_info}CPU:{reset} {bold_white}{cpu}{reset}")
    print(f"{green_info}Architecture:{reset} {bold_white}{arch}{reset}")
    print(f"{green_info}Kernel Version:{reset} {bold_white}{kernel}{reset}")
    print(f"{green_info}GPU:{reset} {bold_white}{gpu_name}{reset}")
    print(f"{green_info}Memory:{reset} {bold_white}{mem_clean}{reset}")
    print(f"{green_info}Resolution:{reset} {bold_white}{resolution}{reset}")
    print(f"{green_info}Uptime:{reset} {bold_white}{uptime_clean}{reset}")
    print(f"{green_info}Host:{reset} {bold_white}{host}{reset}")
    print(f"{green_info}Host Model:{reset} {bold_white}{host_model}{reset}")
    print(f"{green_info}Current User:{reset} {bold_white}{user}{reset}")
    print(f"{green_info}Terminal:{reset} {bold_white}{terminal}{reset}")

    print("-" * 50)  # <-- dashed line to separate

    # --- Packages / Tools ---
    print(f"{pkg_color}Ruby Version:{reset} {bold_white}{ruby_ver}{reset}")
    print(f"{pkg_color}Python Version:{reset} {bold_white}{python_ver}{reset}")
    print(f"{pkg_color}Swift Version:{reset} {bold_white}{swift_ver}{reset}")
    print(f"{pkg_color}Rust Version:{reset} {bold_white}{rust_ver}{reset}")
    print(f"{pkg_color}Cargo Version:{reset} {bold_white}{cargo_ver}{reset}")
    print(f"{pkg_color}Homebrew Version:{reset} {bold_white}{brew_ver}{reset}")
    print(f"{pkg_color}Git Version:{reset} {bold_white}{git_ver}{reset}")
    print(f"{pkg_color}Curl Version:{reset} {bold_white}{curl_ver}{reset}")
    print(f"{pkg_color}OpenSSL Version:{reset} {bold_white}{openssl_ver}{reset}")

    ssh_raw = subprocess.getoutput("ssh -V 2>&1")
    ssh_clean = clean_ssh_version(ssh_raw)

    # default values (match your original variables)
    ssh_ver = ssh_clean

    if "," in ssh_clean:
        ssh_version, ssl_full = [s.strip() for s in ssh_clean.split(",", 1)]
        parts = ssl_full.split()
        ssl_name = parts[0]
        ssl_version = " ".join(parts[1:])

        # build final string (replace words only)
        ssh_ver = f"{ssh_version}, {pkg_color}{ssl_name}{reset} {bold_white}{ssl_version}{reset}"

    # keep ORIGINAL print unchanged
    print(f"{pkg_color}SSH Version:{reset} {bold_white}{ssh_ver}{reset}")

    print(f"{pkg_color}Node Version:{reset} {bold_white}{node_ver}{reset}")
    print(f"{pkg_color}Bash Version:{reset} {bold_white}{bash_ver}{reset}")
    print(f"{pkg_color}Zsh Version:{reset} {bold_white}{zsh_ver}{reset}")
    print(f"{pkg_color}Tar Version:{reset} {bold_white}{tar_ver}{reset}")
    print(f"{pkg_color}Unzip Version:{reset} {bold_white}{unzip_ver}{reset}")
    print(f"{pkg_color}Zip Version:{reset} {bold_white}{zip_ver}{reset}\n")

# --- Detect Linux Distro ---
def get_linux_distro():
    os_release = run_cmd("cat /etc/os-release").lower()
    if "ubuntu" in os_release:
        return "ubuntu"
    elif "debian" in os_release:
        return "debian"
    elif "fedora" in os_release:
        return "fedora"
    elif "centos" in os_release:
        return "centos"
    elif "red hat" in os_release:
        return "rhel"
    else:
        return "linux"

def print_linux_banner(distro: str)-> None:
        banners = {
            "ubuntu": f"""{banner}

'    ██╗   ██╗██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗
'    ██║   ██║██╔══██╗██║   ██║████╗  ██║╚══██╔══╝██║   ██║
'    ██║   ██║██████╔╝██║   ██║██╔██╗ ██║   ██║   ██║   ██║
'    ██║   ██║██╔══██╗██║   ██║██║╚██╗██║   ██║   ██║   ██║
'    ╚██████╔╝██████╔╝╚██████╔╝██║ ╚████║   ██║   ╚██████╔╝
'     ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝    ╚═════╝
'{reset}""",
            "debian": f"""{banner}

'    ██████╗ ███████╗██████╗ ██╗ █████╗ ███╗   ██╗
'    ██╔══██╗██╔════╝██╔══██╗██║██╔══██╗████╗  ██║
'    ██║  ██║█████╗  ██████╔╝██║███████║██╔██╗ ██║
'    ██║  ██║██╔══╝  ██╔══██╗██║██╔══██║██║╚██╗██║
'    ██████╔╝███████╗██████╔╝██║██║  ██║██║ ╚████║
'    ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
'{reset}""",
            "fedora": f"""{banner}

'    ███████╗███████╗██████╗  ██████╗ ██████╗  █████╗
'    ██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗
'    █████╗  █████╗  ██║  ██║██║   ██║██████╔╝███████║
'    ██╔══╝  ██╔══╝  ██║  ██║██║   ██║██╔══██╗██╔══██║
'    ██║     ███████╗██████╔╝╚██████╔╝██║  ██║██║  ██║
'    ╚═╝     ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
'{reset}""",
            "rhel": f"""{banner}

'    ██████╗ ██╗  ██╗███████╗██╗
'    ██╔══██╗██║  ██║██╔════╝██║
'    ██████╔╝███████║█████╗  ██║
'    ██╔══██╗██╔══██║██╔══╝  ██║
'    ██║  ██║██║  ██║███████╗███████╗
'    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
'{reset}""",
            "centos": f"""{banner}

'     ██████╗███████╗███╗   ██╗████████╗ ██████╗ ███████╗
'    ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗██╔════╝
'    ██║     █████╗  ██╔██╗ ██║   ██║   ██║   ██║███████╗
'    ██║     ██╔══╝  ██║╚██╗██║   ██║   ██║   ██║╚════██║
'    ╚██████╗███████╗██║ ╚████║   ██║   ╚██████╔╝███████║
'     ╚═════╝╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚══════╝
'{reset}""",
            "linux": f"""{banner}

'    ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗
'    ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝
'    ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝
'    ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗
'    ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗
'    ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝
'{reset}"""
        }
        print(banners.get(distro, banners["linux"]))

        print("-" * 50)

def get_linux_info():
    distro = get_linux_distro()
    print_linux_banner(distro)

    global loading
    loading = True
    t = threading.Thread(target=spinner)
    t.start()

     # OS Info
    os_info: dict[str, str] = {}
    with open("/etc/os-release") as f:
         for line in f:
             if "=" in line:
                 k, v = line.strip().split("=", 1)
                 os_info[k] = v.strip('"')
    product_name = os_info.get("NAME", "Unknown")
    version = os_info.get("VERSION", "")
    codename = os_info.get("VERSION_CODENAME", "")
    os_id = os_info.get("ID", "")
    os_like = os_info.get("ID_LIKE", "")

    # CPU Info
    cpu_info: dict[str, str] = {}
    for line in run_cmd("lscpu").splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            cpu_info[key.strip()] = val.strip()
    model = cpu_info.get("Model name", "Unknown")
    cores = cpu_info.get("CPU(s)", "Unknown")
    arch = cpu_info.get("Architecture", platform.machine())

    # Other Info
    gpu = subprocess.getoutput("lspci | grep -i vga") or (subprocess.getoutput("glxinfo -B | grep 'Device:'") if shutil.which("glxinfo") else "Unknown")
    mem_clean = parse_mem_linux()
    uptime_clean = parse_uptime_linux()
    arch = platform.machine()
    kernel = platform.release()
    resolution = get_resolution()
    host = platform.node()
    host_model = get_host_model()
    user = getpass.getuser()
    terminal = get_terminal()
    ruby_raw = get_version("ruby")
    ruby_ver = clean_ruby_version(ruby_raw)
    python_raw = get_version("python3")
    python_ver = clean_python_version(python_raw)
    swift_raw = get_version("swift")
    swift_ver = clean_swift_version(swift_raw)
    rust_raw = get_version("rustup")
    rust_ver = clean_rust_version(rust_raw)
    cargo_raw = get_version("cargo")
    cargo_ver = clean_cargo_version(cargo_raw)
    brew_raw = get_version("brew")
    brew_ver = clean_brew_version(brew_raw)
    git_raw = get_version("git")
    git_ver = clean_git_version(git_raw)
    curl_raw = get_version("curl")
    curl_ver = clean_curl_version(curl_raw)
    openssl_raw = get_version("openssl")
    openssl_ver = clean_openssl_version(openssl_raw)
    node_raw = get_version("node")
    node_ver = clean_node_version(node_raw)
    bash_raw = get_version("bash")
    bash_ver = clean_bash_version(bash_raw)
    zsh_raw = get_version("zsh")
    zsh_ver = clean_zsh_version(zsh_raw)
    tar_raw = subprocess.getoutput("tar --version")
    tar_ver = clean_tar_version(tar_raw)
    unzip_raw = subprocess.getoutput("unzip -v")
    unzip_ver = clean_unzip_version(unzip_raw)
    zip_raw = get_version("zip")
    zip_ver = clean_zip_version(zip_raw)

    loading = False
    t.join()
    _ = sys.stdout.write("\r" + " " * 60 + "\r")  # clear line

    print(f"{green_info}Product Name:{reset} {bold_white}{product_name}{reset}")
    if version:
        print(f"{green_info}Product Version:{reset} {bold_white}{version}{reset}")
    if codename:
        print(f"{green_info}Codename:{reset} {bold_white}{codename}{reset}")

    print(f"{green_info}ID:{reset} {bold_white}{os_id} ({os_like}){reset}")
    print(f"{green_info}CPU:{reset} {bold_white}{model} ({cores} cores){reset}")
    print(f"{green_info}Architecture:{reset} {bold_white}{arch}{reset}")
    print(f"{green_info}Kernel Version:{reset} {bold_white}{kernel}{reset}")
    print(f"{green_info}GPU:{reset} {bold_white}{gpu}{reset}")
    print(f"{green_info}Memory:{reset} {bold_white}{mem_clean}{reset}")
    print(f"{green_info}Resolution:{reset} {bold_white}{resolution}{reset}")
    print(f"{green_info}Uptime:{reset} {bold_white}{uptime_clean}{reset}")
    print(f"{green_info}Host:{reset} {bold_white}{host}{reset}")
    print(f"{green_info}Host Model:{reset} {bold_white}{host_model}{reset}")
    print(f"{green_info}Current User:{reset} {bold_white}{user}{reset}")
    print(f"{green_info}Terminal:{reset} {bold_white}{terminal}{reset}")

    print("-" * 50)

    print(f"{pkg_color}Ruby Version:{reset} {bold_white}{ruby_ver}{reset}")
    print(f"{pkg_color}Python Version:{reset} {bold_white}{python_ver}{reset}")
    print(f"{pkg_color}Swift Version:{reset} {bold_white}{swift_ver}{reset}")
    print(f"{pkg_color}Rust Version:{reset} {bold_white}{rust_ver}{reset}")
    print(f"{pkg_color}Cargo Version:{reset} {bold_white}{cargo_ver}{reset}")
    print(f"{pkg_color}Homebrew Version:{reset} {bold_white}{brew_ver}{reset}")
    print(f"{pkg_color}Git Version:{reset} {bold_white}{git_ver}{reset}")
    print(f"{pkg_color}Curl Version:{reset} {bold_white}{curl_ver}{reset}")
    print(f"{pkg_color}OpenSSL Version:{reset} {bold_white}{openssl_ver}{reset}")

    ssh_raw = subprocess.getoutput("ssh -V 2>&1")
    ssh_clean = clean_ssh_version(ssh_raw)

    if "," in ssh_clean:
        ssh_version, ssl_full = [s.strip() for s in ssh_clean.split(",", 1)]
        parts = ssl_full.split()
        ssl_name = parts[0]
        ssl_version = " ".join(parts[1:])
        print(f"{pkg_color}SSH Version:{reset} {bold_white}{ssh_version}{reset}, {pkg_color}{ssl_name}{reset} {bold_white}{ssl_version}{reset}")
    else:
        print(f"{pkg_color}SSH Version:{reset} {bold_white}{ssh_clean}{reset}")

    print(f"{pkg_color}Node Version:{reset} {bold_white}{node_ver}{reset}")
    print(f"{pkg_color}Bash Version:{reset} {bold_white}{bash_ver}{reset}")
    print(f"{pkg_color}Zsh Version:{reset} {bold_white}{zsh_ver}{reset}")
    print(f"{pkg_color}Tar Version:{reset} {bold_white}{tar_ver}{reset}")
    print(f"{pkg_color}Unzip Version:{reset} {bold_white}{unzip_ver}{reset}")
    print(f"{pkg_color}Zip Version:{reset} {bold_white}{zip_ver}{reset}\n")

# --- Main ---
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sysinfo: Display detailed system information (macOS/Linux).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  sysinfo                     # Show full system information
  sysinfo -v / --version      # Show sysinfo version
  sysinfo -h / --help         # Show this help message
"""
    )

    # Assign return value to _ to silence Pyright warning
    _ = parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show sysinfo version and exit"
    )

    args: argparse.Namespace = parser.parse_args()

    # Explicitly type version flag to remove Pyright 'Any' warning
    version_flag: bool = bool(getattr(args, "version", False))

    if version_flag:
        print(f"sysinfo version {VERSION}")
        return

    system: str = platform.system()
    if system == "Darwin":
        get_macos_info()
    elif system == "Linux":
        get_linux_info()
    else:
        print(f"Unsupported OS: {system}")

if __name__ == "__main__":
    main()
