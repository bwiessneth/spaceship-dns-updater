import sys
import os
from pathlib import Path
from loguru import logger
from requests import get


def get_external_ipv4():
    try:
        ipv4 = get("https://api.ipify.org").content.decode("utf8")
        return ipv4
    except:
        return None


def get_external_ipv6():
    try:
        ipv6 = get("https://api6.ipify.org").content.decode("utf8")
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