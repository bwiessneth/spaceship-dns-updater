import sys
import os
from pathlib import Path
from loguru import logger
from requests import get


def get_external_ipv4():
    try:
        ipv4 = get("https://4.ipconfig.com").content.decode("utf8")
        return ipv4
    except:
        return None


def get_external_ipv6():
    try:
        ipv6 = get("https://6.ipconfig.com").content.decode("utf8")
        return ipv6
    except:
        return None


def get_external_ip_addresses():
    logger.info("Get external IP addresses")
    ipv4 = get_external_ipv4()
    ipv6 = get_external_ipv6()
    logger.info(f"External IPv4 address = {ipv4}")
    logger.info(f"External IPv6 address = {ipv6}")
    return ipv4, ipv6


def get_log_file_path():
    if sys.platform == "win32":
        base = Path(os.getenv("LOCALAPPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    log_dir = base / "spaceship-dns-updater" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "spaceship-dns-updater.log"
