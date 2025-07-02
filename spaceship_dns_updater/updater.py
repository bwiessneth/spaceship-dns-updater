import logging
import os
import sys

import click
from loguru import logger
from spaceship_api.client import SpaceshipApiClient
from spaceship_api.dns_records_types import DNSRecordTypeAdapter

from .config import read_user_config
from .utils import get_external_ip_addresses, get_log_file_path


@click.command()
@click.option("--config", "config_file", default="config.yaml", help="Config file to use")
def main(config_file):

    fmt_file = "{time} - {name} - {level} - {message}"
    fmt_console = "<level>{message}</level>"
    logger.remove()
    logger.add(get_log_file_path(), level="DEBUG", rotation="1 MB", retention="90 days", format=fmt_file)
    logger.add(sys.stderr, level="INFO", format=fmt_console)

    config_data_root = read_user_config(config_file)
    if not config_data_root:
        logger.critical("There were errors while processing the config file. Stopping now!")
        sys.exit(1)

    ipv4, ipv6 = get_external_ip_addresses()
    if not ipv4 and not ipv6:
        logger.critical("There were errors while getting the external IP addresses. Stopping now!")
        sys.exit(1)

    for domain, config_data in config_data_root.domains.items():
        logger.info("Fetch current records")

        api_key = config_data_root.api_key or os.getenv("SPACESHIP_API_KEY")
        if not api_key:
            logger.error(
                "Missing API key! Add it to the config.yaml file or create an environment variable SPACESHIP_API_KEY with its value"
            )
            sys.exit(1)

        api_secret = config_data_root.api_secret or os.getenv("SPACESHIP_API_SECRET")
        if not api_secret:
            logger.error(
                "Missing API secret! Add it to the config.yaml file or create an environment variable SPACESHIP_API_SECRET with its value"
            )
            sys.exit(1)

        api_client = SpaceshipApiClient(api_key=api_key, api_secret=api_secret)

        current_records_on_domain = api_client.get_dns_records(domain)

        for record in current_records_on_domain:
            logger.info(f"{domain}\t{record.type:4} {record.name} -> {record.address} (TTL={record.ttl})")

        logger.info("Update records")
        for config_record in config_data.records:
            skip_record = False

            # Only work on A and AAAA records
            if config_record.type not in ["A", "AAAA"]:
                logger.warning(f"Ignoring configured records of type {config_record.type}")
                continue

            expected_address = ipv4 if config_record.type == "A" else ipv6

            if not expected_address:
                logger.warning(f"No {config_record.type} address available for {domain} {config_record.name}")
                continue            

            # Check if the current records on current domain already have an item with same type and name
            for existing_record in current_records_on_domain:
                if (
                    existing_record.type == config_record.type
                    and existing_record.name == config_record.name
                    and existing_record.ttl == config_record.ttl
                ):
                    if existing_record.address == expected_address:
                        logger.info(
                            f"{domain}\t{config_record.type:4} {config_record.name}: Current record has the same data as the new one! No update needed!"
                        )
                        skip_record = True
                    else:
                        logger.info(
                            f"{domain}\t{config_record.type:4} {config_record.name}: Current record already exists! Deleting it before updating..."
                        )
                        api_client.delete_dns_records(domain, [existing_record])

            if skip_record:
                continue

            logger.info(
                f"Updating domain {domain} with {config_record.type} record {config_record.name} with {expected_address} (TTL={config_record.ttl})"
            )

            new_record = config_record.model_dump()
            new_record["address"] = expected_address
            api_client.update_dns_records(domain, [DNSRecordTypeAdapter.validate_python(new_record)])


if __name__ == "__main__":
    sys.exit(main())
