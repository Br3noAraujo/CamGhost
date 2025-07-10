#!/usr/bin/python3
#! coding: utf-8
"""
CamGhost  - Stealthy webcam privacy toolkit for Linux/macOS.
By Br3noAraujo | github.com/Br3noAraujo
"""
import argparse
import logging
import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
import psutil
from colorama import Fore, Style, init as colorama_init
import subprocess
import platform
import glob

colorama_init(autoreset=True)
logger = logging.getLogger("CamGhost")
DEVICES = [str(d) for d in Path("/dev").glob("video*")]
WIPE_TARGETS = [
    Path.home() / ".cache",
    Path.home() / ".config" / "zoom",
    Path.home() / ".config" / "obs-studio",
    Path.home() / ".config" / "Webex",
    Path.home() / ".config" / "Microsoft Teams",
    Path.home() / ".config" / "skypeforlinux",
]

BANNER = f"""
{Fore.LIGHTCYAN_EX}   
                          ____
                     _[]_/____\__n_
                    |_____.--.__()_|   
             CAM    |    //# \\\\    |   GHOST
                    |    \\\\__//    |
                    |     '--'     |
                    '--------------'
{'-'*56}
{Fore.LIGHTYELLOW_EX}      By Br3noAraujo | github.com/Br3noAraujo{Style.RESET_ALL}
{Fore.LIGHTGREEN_EX}"Not every eye sees. Not every camera captures. Some just... obey."{Style.RESET_ALL}
"""

def print_banner():
    print(BANNER)

def print_hacker(msg, color=Fore.YELLOW):
    print(f"{color}{msg}{Style.RESET_ALL}")

def setup_logging(enable_log: bool):
    logger.setLevel(logging.DEBUG if enable_log else logging.CRITICAL)
    fmt = '[%(asctime)s] %(levelname)s: %(message)s'
    if enable_log:
        fh = logging.FileHandler('camghost.log')
        fh.setFormatter(logging.Formatter(fmt))
        logger.addHandler(fh)

def require_root():
    if os.geteuid() != 0:
        print_hacker("[!] This operation requires root privileges.", Fore.LIGHTRED_EX)
        sys.exit(1)

def mode_ghost(args):
    require_root()
    video_devs = [Path(d) for d in DEVICES]
    if not video_devs:
        print_hacker("No /dev/video* devices found.", Fore.LIGHTRED_EX)
        print_hacker("Try: ls /dev/video*", Fore.YELLOW)
        sys.exit(1)
    affected = []
    if args.restore:
        for dev in video_devs:
            try:
                dev.chmod(0o666)
                logger.info(f"Restored permissions for {dev}")
                print_hacker(f"[+] Restored {dev}", Fore.LIGHTGREEN_EX)
                affected.append(str(dev))
            except Exception as e:
                logger.error(f"Failed to restore {dev}: {e}")
        print_hacker(f"[INFO] Devices restored: {', '.join(affected) if affected else 'None'}", Fore.LIGHTCYAN_EX)
        return
    for dev in video_devs:
        try:
            dev.chmod(0o000)
            logger.info(f"Set permissions 000 for {dev}")
            print_hacker(f"[+] Ghosted {dev}", Fore.LIGHTCYAN_EX)
            affected.append(str(dev))
        except Exception as e:
            logger.error(f"Failed to ghost {dev}: {e}")
    print_hacker(f"[INFO] Devices ghosted: {', '.join(affected) if affected else 'None'}", Fore.LIGHTCYAN_EX)

def mode_monitor(args):
    require_root()
    target_dev = Path(args.device) if args.device else Path("/dev/video0")
    if not target_dev.exists():
        print_hacker(f"{target_dev} not found.", Fore.LIGHTRED_EX)
        print_hacker("Try: ls /dev/video*", Fore.YELLOW)
        sys.exit(1)
    print_hacker(f"[*] Monitoring access to {target_dev}. Press Ctrl+C to stop.", Fore.LIGHTCYAN_EX)
    logger.info(f"Started monitoring {target_dev} access.")
    accessed_pids = set()
    last_activity = time.time()
    try:
        while True:
            found = False
            # psutil method
            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    files = proc.info.get('open_files')
                    if files:
                        for f in files:
                            if f.path == str(target_dev) and proc.info['pid'] not in accessed_pids:
                                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                msg = f"[MONITOR] {ts} | PID {proc.info['pid']} | {proc.info['name']} accessed {target_dev}"
                                print_hacker(msg, Fore.YELLOW)
                                logger.info(msg)
                                accessed_pids.add(proc.info['pid'])
                                found = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            # /proc/*/fd method
            for pid_dir in glob.glob('/proc/[0-9]*/fd'):
                pid = pid_dir.split('/')[2]
                try:
                    for fd in os.listdir(pid_dir):
                        fd_path = os.path.join(pid_dir, fd)
                        try:
                            link = os.readlink(fd_path)
                            if link == str(target_dev) and int(pid) not in accessed_pids:
                                # Get process name
                                with open(f"/proc/{pid}/comm", "r") as commf:
                                    pname = commf.read().strip()
                                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                msg = f"[MONITOR] {ts} | PID {pid} | {pname} accessed {target_dev}"
                                print_hacker(msg, Fore.LIGHTYELLOW_EX)
                                logger.info(msg)
                                accessed_pids.add(int(pid))
                                found = True
                        except Exception:
                            continue
                except Exception:
                    continue
            if found:
                last_activity = time.time()
            elif time.time() - last_activity > 30:
                print_hacker(f"[INFO] No process has accessed {target_dev} in the last 30 seconds...", Fore.LIGHTCYAN_EX)
                last_activity = time.time()
            time.sleep(1)
    except KeyboardInterrupt:
        print_hacker("[!] Monitor stopped by user.", Fore.LIGHTRED_EX)
        logger.info("Monitor stopped by user.")

def mode_wipe(args):
    print_hacker("[*] Securely wiping webcam-related cache/config folders...", Fore.LIGHTCYAN_EX)
    wiped = []
    notfound = []
    for t in WIPE_TARGETS:
        if t.exists():
            try:
                if t.is_dir():
                    shutil.rmtree(t)
                    logger.info(f"Wiped directory {t}")
                    print_hacker(f"[+] Wiped {t}", Fore.LIGHTGREEN_EX)
                else:
                    t.unlink()
                    logger.info(f"Wiped file {t}")
                    print_hacker(f"[+] Wiped {t}", Fore.LIGHTGREEN_EX)
                wiped.append(str(t))
            except Exception as e:
                logger.error(f"Failed to wipe {t}: {e}")
        else:
            print_hacker(f"[-] Not found: {t}", Fore.YELLOW)
            notfound.append(str(t))
    print_hacker(f"[INFO] Wiped: {', '.join(wiped) if wiped else 'None'}", Fore.LIGHTCYAN_EX)
    print_hacker(f"[INFO] Not found: {', '.join(notfound) if notfound else 'None'}", Fore.YELLOW)

def install_dependencies():
    print_hacker("[*] Installing system dependencies...", Fore.LIGHTCYAN_EX)
    cmds = []
    os_name = platform.system().lower()
    if os_name == 'linux':
        if shutil.which('apt'):
            cmds = [
                ['sudo', 'apt', 'update'],
                ['sudo', 'apt', 'install', '-y', 'psutil', 'colorama']
            ]
        elif shutil.which('dnf'):
            cmds = [['sudo', 'dnf', 'install', '-y', 'python3-psutil', 'python3-colorama']]
        elif shutil.which('pacman'):
            cmds = [['sudo', 'pacman', '-Sy', '--noconfirm', 'python-psutil', 'python-colorama']]
        elif shutil.which('zypper'):
            cmds = [['sudo', 'zypper', 'install', '-y', 'python3-psutil', 'python3-colorama']]
        else:
            print_hacker('Unsupported package manager. Install psutil and colorama manually.', Fore.LIGHTRED_EX)
            sys.exit(1)
    elif os_name == 'darwin':
        if shutil.which('brew'):
            cmds = [['brew', 'install', 'psutil', 'colorama']]
        else:
            print_hacker('Homebrew not found. Install psutil and colorama manually.', Fore.LIGHTRED_EX)
            sys.exit(1)
    else:
        print_hacker('Unsupported OS for automatic install.', Fore.LIGHTRED_EX)
        sys.exit(1)
    for cmd in cmds:
        print_hacker(f"[+] Running: {' '.join(cmd)}", Fore.YELLOW)
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print_hacker(f"Failed to run {' '.join(cmd)}: {e}", Fore.LIGHTRED_EX)
            sys.exit(1)
    print_hacker("[+] Dependencies installed!", Fore.LIGHTGREEN_EX)
    sys.exit(0)

class BannerHelpFormatter(argparse.RawTextHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = ''
        self.add_text(BANNER + Style.RESET_ALL)
        self.add_text(f"""
{Fore.LIGHTYELLOW_EX}CamGhost: Stealthy webcam privacy toolkit

Modes:
  --mode ghost     Hide/disable the physical webcam device (sets permissions 000 on /dev/video*)
                  Use --restore to bring devices back (sets permissions 666)
  --mode monitor   Monitor and log all processes accessing /dev/video0 (or --device) in real time
  --mode wipe      Securely delete webcam-related logs and user data (Zoom, OBS, Teams, etc)

Examples:
  python3 camghost.py --mode ghost
      # Hide all /dev/video* devices (root required)
  python3 camghost.py --mode ghost --restore
      # Restore all /dev/video* devices (root required)
  python3 camghost.py --mode monitor --device /dev/video1
      # Monitor access to /dev/video1 (root required)
  python3 camghost.py --mode wipe
      # Securely wipe webcam cache/configs (no root needed)

Tips:
  - Use {Fore.LIGHTCYAN_EX}--log{Fore.LIGHTYELLOW_EX} to enable detailed logging to camghost.log
  - Run as root for ghost/monitor modes
  - For troubleshooting, check permissions on /dev/video* and camghost.log
  - CamGhost is cross-platform but optimized for Linux

Troubleshooting:
  - If you see 'device busy', close all apps using the webcam and try again.
  - If 'permission denied', run as root (sudo).
  - For more info, check camghost.log.

{Fore.LIGHTGREEN_EX}Hacker tip: Use this tool before video calls or in public environments for extra privacy!{Style.RESET_ALL}
""")
        super().add_usage(usage, actions, groups, prefix)

def main():
    print_banner()
    if len(sys.argv) == 1:
        print(f"{Fore.LIGHTYELLOW_EX}Usage: python3 camghost.py --mode <ghost|monitor|wipe> [options]{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}Try: python3 camghost.py -h{Style.RESET_ALL}")
        sys.exit(0)
    parser = argparse.ArgumentParser(
        description="CamGhost: Stealthy webcam privacy toolkit.",
        formatter_class=BannerHelpFormatter,
        add_help=False,
        usage="python3 camghost.py --mode <ghost|monitor|wipe> [options]"
    )
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')
    parser.add_argument('-l', '--log', action='store_true', help='Enable detailed logging in camghost.log')
    parser.add_argument('--install-deps', action='store_true', help='Automatically install system dependencies and exit')
    parser.add_argument('--mode', required=True, choices=['ghost', 'monitor', 'wipe'], help='Operation mode')
    parser.add_argument('--restore', action='store_true', help='Restore webcam device (ghost mode)')
    parser.add_argument('--device', type=str, default='/dev/video0', help='Device to monitor (monitor mode only, default: /dev/video0)')
    args = parser.parse_args()
    if args.install_deps:
        install_dependencies()
    setup_logging(args.log)
    if args.mode == 'ghost':
        mode_ghost(args)
    elif args.mode == 'monitor':
        mode_monitor(args)
    elif args.mode == 'wipe':
        mode_wipe(args)
    if args.log:
        print_hacker("[INFO] Log file: camghost.log", Fore.LIGHTCYAN_EX)

if __name__ == "__main__":
    main() 