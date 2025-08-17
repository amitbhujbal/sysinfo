#!/usr/bin/env python3
import platform
import os
import subprocess
import getpass
import shutil

bold = "\033[1m"
bold_white = "\033[1;37m"
reset = "\033[0m"

# --- Utility Functions ---
def get_resolution():
    system = platform.system()
    try:
        if system == "Darwin":
            return subprocess.getoutput("system_profiler SPDisplaysDataType | grep Resolution")
        elif system == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            return f"{width}x{height}"
        elif system == "Linux":
            return subprocess.getoutput("xdpyinfo | grep dimensions | awk '{print $2}'")
    except:
        return "Unknown"
    return "Unknown"

def get_terminal():
    system = platform.system()
    if system in ["Darwin", "Linux"]:
        return os.environ.get("TERM_PROGRAM") or os.environ.get("TERM") or "Unknown"
    elif system == "Windows":
        return os.environ.get("COMSPEC") or "cmd.exe"
    return "Unknown"

def get_version(cmd):
    if shutil.which(cmd):
        try:
            return subprocess.getoutput(f"{cmd} --version").split("\n")[0]
        except:
            return "Unknown"
    else:
        return "Not Installed"

def get_host_model():
    system = platform.system()
    try:
        if system == "Darwin":
            return subprocess.getoutput("system_profiler SPHardwareDataType | grep 'Model Identifier' | awk '{print $3}'")
        elif system == "Windows":
            return subprocess.getoutput("wmic computersystem get model").splitlines()[1].strip()
        elif system == "Linux":
            return subprocess.getoutput("cat /sys/devices/virtual/dmi/id/product_name")
    except:
        return "Unknown"
    return "Unknown"

# --- macOS Info ---
def get_macos_info():
    bold = "\033[1m"
    reset = "\033[0m"

    print(f"""{bold}

███╗░░░███╗░█████╗░░█████╗░░█████╗░░██████╗
████╗░████║██╔══██╗██╔══██╗██╔══██╗██╔════╝
██╔████╔██║███████║██║░░╚═╝██║░░██║╚█████╗░
██║╚██╔╝██║██╔══██║██║░░██╗██║░░██║░╚═══██╗
██║░╚═╝░██║██║░░██║╚█████╔╝╚█████╔╝██████╔╝
╚═╝░░░░░╚═╝╚═╝░░╚═╝░╚════╝░░╚════╝░╚═════╝░
{reset}""")
    product_name = subprocess.getoutput("sw_vers -productName")
    product_version = subprocess.getoutput("sw_vers -productVersion")
    build_version = subprocess.getoutput("sw_vers -buildVersion")
    cpu = subprocess.getoutput("sysctl -n machdep.cpu.brand_string")
    gpu = subprocess.getoutput("system_profiler SPDisplaysDataType | grep 'Chipset Model'")
    gpu_name = gpu.replace("Chipset Model:", "").strip()
    mem = subprocess.getoutput("top -l 1 | grep PhysMem")
    # Split and extract numbers
    parts = mem.replace("PhysMem:", "").replace("M", "").replace("(", "").replace(")", "").replace(",", "").split()
    used = parts[0]
    wired = parts[2]
    compressor = parts[4]
    unused = parts[6]
    uptime = subprocess.getoutput("uptime")
    current_time = uptime.split()[0]
    arch = platform.machine()
    kernel = platform.release()
    resolution = get_resolution()
    resolution_name = resolution.replace("Resolution:", "").strip()
    host = platform.node()
    host_model = get_host_model()
    user = getpass.getuser()
    terminal = get_terminal()
    ruby_ver = get_version("ruby")
    python_ver = get_version("python3")
    swift_ver = get_version("swift")

    # ANSI escape codes for bold blue
    bold_white = "\033[1;37m"
    reset = "\033[0m"

    print(f"{bold}Product Name:{reset} {product_name}")
    print(f"{bold}Product Version:{reset} {product_version}")
    print(f"{bold}Build Version:{reset} {build_version}")
    print(f"{bold}CPU:{reset} {cpu}")
    print(f"{bold}Architecture:{reset} {arch}")
    print(f"{bold}Kernel Version:{reset} {kernel}")
    print(f"{bold}GPU:{reset} {gpu_name}")
    print(f"{bold}PhysMem:{reset} {used}M {bold_white}used{reset}, {wired}M {bold_white}wired{reset}, {compressor}M {bold_white}compressor{reset}, {unused}M {bold_white}unused{reset}")
    print(f"{bold}Resolution:{reset} {resolution_name}")
    print(f"{bold}Uptime:{reset} {current_time}")
    print(f"{bold}Host:{reset} {host}")
    print(f"{bold}Host Model:{reset} {host_model}")
    print(f"{bold}Current User:{reset} {user}")
    print(f"{bold}Terminal:{reset} {terminal}")
    print(f"{bold_white}Ruby Version:{reset} {ruby_ver}")
    print(f"{bold_white}Python Version:{reset} {python_ver}")
    print(f"{bold_white}Swift Version:{reset} {swift_ver}\n")

# --- Windows Info ---
def get_windows_info():
    bold = "\033[1m"
    reset = "\033[0m"

    print(f"""{bold}

░██╗░░░░░░░██╗██╗███╗░░██╗██████╗░░█████╗░░██╗░░░░░░░██╗░██████╗
░██║░░██╗░░██║██║████╗░██║██╔══██╗██╔══██╗░██║░░██╗░░██║██╔════╝
░╚██╗████╗██╔╝██║██╔██╗██║██║░░██║██║░░██║░╚██╗████╗██╔╝╚█████╗░
░░████╔═████║░██║██║╚████║██║░░██║██║░░██║░░████╔═████║░░╚═══██╗
░░╚██╔╝░╚██╔╝░██║██║░╚███║██████╔╝╚█████╔╝░░╚██╔╝░╚██╔╝░██████╔╝
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░░╚════╝░░░░╚═╝░░░╚═╝░░╚═════╝░
{reset}""")
    os_name = subprocess.getoutput("systeminfo | findstr /B /C:'OS Name'")
    os_version = subprocess.getoutput("systeminfo | findstr /B /C:'OS Version'")
    cpu = subprocess.getoutput("wmic cpu get name,NumberOfCores,MaxClockSpeed")
    gpu = subprocess.getoutput("wmic path win32_videocontroller get name")
    mem = subprocess.getoutput("systeminfo | findstr /C:'Total Physical Memory'")
    uptime = subprocess.getoutput("net stats srv | findstr 'Statistics since'")
    arch = platform.machine()
    kernel = platform.release()
    resolution = get_resolution()
    host = platform.node()
    host_model = get_host_model()
    user = getpass.getuser()
    terminal = get_terminal()
    ruby_ver = get_version("ruby")
    python_ver = get_version("python")
    swift_ver = get_version("swift")

    print(f"{bold}OS Name:{reset} {os_name.split(':',1)[-1].strip()}")
    print(f"{bold}OS Version:{reset} {os_version.split(':',1)[-1].strip()}")
    print(f"{bold}CPU:{reset}\n{cpu}")
    print(f"{bold}Architecture:{reset} {arch}")
    print(f"{bold}Kernel Version:{reset} {kernel}")
    print(f"{bold}GPU:{reset}\n{gpu}")
    print(f"{bold}Memory:{reset} {mem.split(':',1)[-1].strip()}")
    print(f"{bold}Resolution:{reset} {resolution}")
    print(f"{bold}Uptime:{reset} {uptime.split('Statistics since')[-1].strip()}")
    print(f"{bold}Host:{reset} {host}")
    print(f"{bold}Host Model:{reset} {host_model}")
    print(f"{bold}Current User:{reset} {user}")
    print(f"{bold}Terminal:{reset} {terminal}")
    print(f"{bold_white}Ruby Version:{reset} {ruby_ver}")
    print(f"{bold_white}Python Version:{reset} {python_ver}")
    print(f"{bold_white}Swift Version:{reset} {swift_ver}\n")

# --- Linux Info ---
def get_linux_info():
    bold = "\033[1m"
    reset = "\033[0m"

    print(f"""{bold}

██╗░░░░░██╗███╗░░██╗██╗░░░██╗██╗░░██╗
██║░░░░░██║████╗░██║██║░░░██║╚██╗██╔╝
██║░░░░░██║██╔██╗██║██║░░░██║░╚███╔╝░
██║░░░░░██║██║╚████║██║░░░██║░██╔██╗░
███████╗██║██║░╚███║╚██████╔╝██╔╝╚██╗
╚══════╝╚═╝╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝
{reset}""")
    try:
        os_release = subprocess.getoutput("cat /etc/os-release")
    except:
        os_release = "Unknown"
    cpu = subprocess.getoutput("lscpu")
    gpu = subprocess.getoutput("lspci | grep -i vga")
    mem = subprocess.getoutput("free -h")
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
    print(f"{bold}Swift Version:{reset} {swift_ver}\n")

# --- Main ---
def main():
    system = platform.system()
    if system == "Darwin":
        get_macos_info()
    elif system == "Windows":
        get_windows_info()
    elif system == "Linux":
        get_linux_info()
    else:
        print(f"Unsupported OS: {system}")

if __name__ == "__main__":
    main()
