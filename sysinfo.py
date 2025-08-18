#!/usr/bin/env python3
import platform
import os
import subprocess
import getpass
import shutil
import sys
import time
import threading

bold = "\033[1m"
bold_white = "\033[1;37m"
reset = "\033[0m"

# --- Spinner Animation ---
loading = True
def spinner():
    symbols = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    i = 0
    while loading:
        sys.stdout.write(f"\r{bold_white}Collecting system information... {symbols[i % len(symbols)]}{reset}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)

# --- Utility Functions ---
def get_resolution():
    system = platform.system()
    try:
        if system == "Darwin":
            res = subprocess.getoutput("system_profiler SPDisplaysDataType | grep Resolution")
            return res.strip() if res else "Unknown"
        elif system == "Linux":
            if shutil.which("xdpyinfo"):
                return subprocess.getoutput("xdpyinfo | grep dimensions | awk '{print $2}'")
    except:
        return "Unknown"
    return "Unknown"

def get_terminal():
    if platform.system() in ["Darwin", "Linux"]:
        return os.environ.get("TERM_PROGRAM") or os.environ.get("TERM") or "Unknown"
    return "Unknown"

def get_version(cmd):
    if shutil.which(cmd):
        try:
            return subprocess.getoutput(f"{cmd} --version").split("\n")[0]
        except:
            return "Unknown"
    return "Not Installed"

def get_host_model():
    try:
        if platform.system() == "Darwin":
            return subprocess.getoutput("system_profiler SPHardwareDataType | grep 'Model Identifier' | awk '{print $3}'")
        elif platform.system() == "Linux":
            return subprocess.getoutput("cat /sys/devices/virtual/dmi/id/product_name 2>/dev/null")
    except:
        return "Unknown"
    return "Unknown"

# --- macOS Info ---
def get_macos_info():
    print(f"""{bold}

███╗░░░███╗░█████╗░░█████╗░░█████╗░░██████╗
████╗░████║██╔══██╗██╔══██╗██╔══██╗██╔════╝
██╔████╔██║███████║██║░░╚═╝██║░░██║╚█████╗░
██║╚██╔╝██║██╔══██║██║░░██╗██║░░██║░╚═══██╗
██║░╚═╝░██║██║░░██║╚█████╔╝╚█████╔╝██████╔╝
╚═╝░░░░░╚═╝╚═╝░░╚═╝░╚════╝░░╚════╝░╚═════╝░
{reset}""")

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

    # stop spinner
    loading = False
    t.join()
    sys.stdout.write("\r" + " " * 60 + "\r")  # clear line

    # print results
    print(f"{bold}Product Name:{reset} {product_name}")
    print(f"{bold}Product Version:{reset} {product_version}")
    print(f"{bold}Build Version:{reset} {build_version}")
    print(f"{bold}CPU:{reset} {cpu}")
    print(f"{bold}Architecture:{reset} {arch}")
    print(f"{bold}Kernel Version:{reset} {kernel}")
    print(f"{bold}GPU:{reset} {gpu_name}")
    print(f"{bold}PhysMem:{reset} {mem}")
    print(f"{bold}Resolution:{reset} {resolution}")
    print(f"{bold}Uptime:{reset} {uptime}")
    print(f"{bold}Host:{reset} {host}")
    print(f"{bold}Host Model:{reset} {host_model}")
    print(f"{bold}Current User:{reset} {user}")
    print(f"{bold}Terminal:{reset} {terminal}")
    print(f"{bold_white}Ruby Version:{reset} {ruby_ver}")
    print(f"{bold_white}Python Version:{reset} {python_ver}")
    print(f"{bold_white}Swift Version:{reset} {swift_ver}")
    print(f"{bold_white}Rust Version:{reset} {rust_ver}")
    print(f"{bold_white}Cargo Version:{reset} {cargo_ver}")
    print(f"{bold_white}Homebrew Version:{reset} {brew_ver}\n")

# --- Linux Info ---
def get_linux_distro():
    try:
        os_release = subprocess.getoutput("cat /etc/os-release")
        for line in os_release.splitlines():
            if line.startswith("ID="):
                return line.split("=")[1].strip().replace('"', '')
    except:
        return "linux"
    return "linux"

def print_linux_banner(distro):
    def print_linux_banner(distro):
        banners = {
            "ubuntu": f"""{bold}

██╗░░░██╗██████╗░██╗░░░██╗███╗░░██╗████████╗██╗░░░██╗
██║░░░██║██╔══██╗██║░░░██║████╗░██║╚══██╔══╝██║░░░██║
██║░░░██║██████╦╝██║░░░██║██╔██╗██║░░░██║░░░██║░░░██║
██║░░░██║██╔══██╗██║░░░██║██║╚████║░░░██║░░░██║░░░██║
╚██████╔╝██████╦╝╚██████╔╝██║░╚███║░░░██║░░░╚██████╔╝
░╚═════╝░╚═════╝░░╚═════╝░╚═╝░░╚══╝░░░╚═╝░░░░╚═════╝░
    {reset}""",
            "debian": f"""{bold}

██████╗░███████╗██████╗░██╗░█████╗░███╗░░██╗
██╔══██╗██╔════╝██╔══██╗██║██╔══██╗████╗░██║
██║░░██║█████╗░░██████╦╝██║███████║██╔██╗██║
██║░░██║██╔══╝░░██╔══██╗██║██╔══██║██║╚████║
██████╔╝███████╗██████╦╝██║██║░░██║██║░╚███║
╚═════╝░╚══════╝╚═════╝░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝
    ╚═════╝░╚══════╝╚═════╝░╚═╝░╚════╝░╚═╝░░╚══╝
    {reset}""",
            "fedora": f"""{bold}

███████╗███████╗██████╗░░█████╗░██████╗░░█████╗░
██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
█████╗░░█████╗░░██║░░██║██║░░██║██████╔╝███████║
██╔══╝░░██╔══╝░░██║░░██║██║░░██║██╔══██╗██╔══██║
██║░░░░░███████╗██████╔╝╚█████╔╝██║░░██║██║░░██║
╚═╝░░░░░╚══════╝╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝
    {reset}""",
            "rhel": f"""{bold}

██████╗░██╗░░██╗███████╗██╗░░░░░
██╔══██╗██║░░██║██╔════╝██║░░░░░
██████╔╝███████║█████╗░░██║░░░░░
██╔══██╗██╔══██║██╔══╝░░██║░░░░░
██║░░██║██║░░██║███████╗███████╗
╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝╚══════╝
    {reset}""",
            "centos": f"""{bold}

░█████╗░███████╗███╗░░██╗████████╗░█████╗░░██████╗
██╔══██╗██╔════╝████╗░██║╚══██╔══╝██╔══██╗██╔════╝
██║░░╚═╝█████╗░░██╔██╗██║░░░██║░░░██║░░██║╚█████╗░
██║░░██╗██╔══╝░░██║╚████║░░░██║░░░██║░░██║░╚═══██╗
╚█████╔╝███████╗██║░╚███║░░░██║░░░╚█████╔╝██████╔╝
░╚════╝░╚══════╝╚═╝░░╚══╝░░░╚═╝░░░░╚════╝░╚═════╝░
    {reset}""",
            "linux": f"""{bold}

██╗░░░░░██╗███╗░░██╗██╗░░░██╗██╗░░██╗
██║░░░░░██║████╗░██║██║░░░██║╚██╗██╔╝
██║░░░░░██║██╔██╗██║██║░░░██║░╚███╔╝░
██║░░░░░██║██║╚████║██║░░░██║░██╔██╗░
███████╗██║██║░╚███║╚██████╔╝██╔╝╚██╗
╚══════╝╚═╝╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝
    {reset}"""
        }
        print(banners.get(distro, banners["linux"]))

def get_linux_info():
    distro = get_linux_distro()
    print_linux_banner(distro)

    global loading
    loading = True
    t = threading.Thread(target=spinner)
    t.start()

    os_release = subprocess.getoutput("cat /etc/os-release")
    cpu = subprocess.getoutput("lscpu 2>/dev/null") or "Unknown"
    gpu = subprocess.getoutput("lspci | grep -i vga") or (subprocess.getoutput("glxinfo -B | grep 'Device:'") if shutil.which("glxinfo") else "Unknown")
    mem = subprocess.getoutput("free -h") or "Unknown"
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

    loading = False
    t.join()
    sys.stdout.write("\r" + " " * 60 + "\r")  # clear line

    print(f"{bold}OS Info:{reset}\n{os_release}")
    print(f"{bold}Host:{reset} {host}")
    print(f"{bold}Host Model:{reset} {host_model}")
    print(f"{bold}CPU:{reset}\n{cpu}")
    print(f"{bold}Architecture:{reset} {arch}")
    print(f"{bold}Kernel Version:{reset} {kernel}")
    print(f"{bold}GPU:{reset}\n{gpu}")
    print(f"{bold}Memory:{reset}\n{mem}")
    print(f"{bold}Resolution:{reset} {resolution}")
    print(f"{bold}Uptime:{reset} {uptime}")
    print(f"{bold}Current User:{reset} {user}")
    print(f"{bold}Terminal:{reset} {terminal}")
    print(f"{bold}Ruby Version:{reset} {ruby_ver}")
    print(f"{bold}Python Version:{reset} {python_ver}")
    print(f"{bold}Swift Version:{reset} {swift_ver}")
    print(f"{bold_white}Rust Version:{reset} {rust_ver}")
    print(f"{bold_white}Cargo Version:{reset} {cargo_ver}")
    print(f"{bold_white}Homebrew Version:{reset} {brew_ver}\n")

# --- Main ---
def main():
    system = platform.system()
    if system == "Darwin":
        get_macos_info()
    elif system == "Linux":
        get_linux_info()
    else:
        print(f"Unsupported OS: {system}")

if __name__ == "__main__":
    main()
