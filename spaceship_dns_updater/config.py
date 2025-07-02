import logging

import yaml
from loguru import logger
from pydantic import ValidationError

from spaceship_dns_updater.config_model import ConfigModel


def read_user_config(config_file):
    logger.info("Read user config")
    try:
        # Load YAML
        with open(config_file, "r") as f:
            raw_data = yaml.safe_load(f)

        # Validate using Pydantic
        try:
            config = ConfigModel.model_validate(raw_data)
        except ValidationError as e:
            logger.error("Config file has some issues!")
            logger.error(e)
            return None

        # Access validated data
        # for domain, domain_config in config.root.items():
        #     logger.info(f"Domain: {domain}")
        #     logger.info(f"  API key: {domain_config.api_key}")
        #     logger.info(f"  API secret: {domain_config.api_secret}")
        #     logger.info(f"  Records:")
        #     for record in domain_config.records:
        #         logger.info(f"    - {record.type:4} {record.name} (TTL={record.ttl})")

        logger.info(f"Got config for {len(config.domains.items())} domains")

        return config

    except FileNotFoundError as e:
        logger.error(e)
        return None
