spaceship-dns-updater
#####################

Tool for updating DNS records for domains hosted by https://www.spaceship.com/.

This tool uses the https://github.com/bwiessneth/spaceship-api Python library.

The script detects your system’s external IPv4 and/or IPv6 addresses and updates the configured DNS records using your Spaceship API credentials.

Configuration
#############

Basic Configuration
===================

Create a YAML configuration file with your domain name, API credentials, and details about the DNS records you want to update.

A minimal example configuration:

.. code-block:: yaml

    api_key: <YOUR_API_KEY>
    api_secret: <YOUR_API_SECRET>

    domains:
      your-domain.com:
        records:
          - type: "A"
            name: "@"
            ttl: 1800

Records
=======

.. note::

   Only DNS records of type ``A`` (IPv4) and ``AAAA`` (IPv6) are currently supported
   for dynamic updates. Other record types (e.g., ``CNAME``, ``TXT``, ``MX``) will be ignored.

Add each record you want to update under the domain’s ``records`` list:

.. code-block:: yaml

    records:
      - type: "A"
        name: "@"
        ttl: 1800
      - type: "AAAA"
        name: "@"
        ttl: 1800
      - type: "A"
        name: "subdomain"
        ttl: 1800

For ``A`` records, the IPv4 address is fetched from https://www.ipify.org/.  
If no IPv4 address is found, the record is skipped.

Similarly, for ``AAAA`` records, the IPv6 address is fetched from https://www.ipify.org/.  
If no IPv6 address is found, the record is skipped.

Multiple Domains
================

You can manage multiple domains in the same YAML config file by adding each domain section:

.. code-block:: yaml

    api_key: <YOUR_API_KEY>
    api_secret: <YOUR_API_SECRET>

    domains:
      your-first-domain.com:
        records:
          - type: "A"
            name: "@"
            ttl: 1800

      your-second-domain.com:
        records:
          - type: "A"
            name: "@"
            ttl: 1800

Installation
############

There are multiple ways to run this tool. The recommended method is using Docker.

Run spaceship-dns-updater as Docker Container
==============================================

Create a ``Dockerfile`` with the following content:

.. code-block:: dockerfile

    # Use a minimal Python base image
    FROM python:3.12-alpine

    # Set environment variables
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1

    # Install the spaceship-dns-updater package
    RUN pip install --no-cache-dir spaceship-dns-updater

    # Default command when container starts
    CMD ["spaceship-dns-updater"]

Create a ``docker-compose.yaml`` file with the following content:

.. code-block:: yaml

    services:
      spaceship-dns-updater:
        build:
          context: .
          dockerfile: Dockerfile
        image: spaceship-dns-updater
        container_name: spaceship-dns-updater
        volumes:
          - ./config.yaml:/spaceship-dns-updater/config.yaml
          - ./logs:/root/.local/share/spaceship-dns-updater/logs
        working_dir: /spaceship-dns-updater
        command: ["spaceship-dns-updater", "--config", "config.yaml"]

To build the image and start the container, run:

.. code-block:: bash

   sudo docker compose up --build

This will:

- Build the Docker image using the ``Dockerfile``.
- Mount your ``config.yaml`` and ``logs/`` directory into the container.
- Run the ``spaceship-dns-updater`` command with your config.
- Automatically stop the container after execution finishes.

Run Periodically with systemd Timer
-----------------------------------

You can schedule the container to run periodically using a ``systemd`` timer — a robust alternative to cron.

Step 1: Create the systemd Service Unit
***************************************

Create the service file:

.. code-block:: bash

   sudo nano /etc/systemd/system/spaceship-dns-updater.service

Add the following content:

.. code-block:: ini

   [Unit]
   Description=Run spaceship-dns-updater via Docker Compose
   Wants=network-online.target
   After=network-online.target

   [Service]
   Type=oneshot
   WorkingDirectory=/home/YOUR_NAME/spaceship-dns-updater
   ExecStart=/usr/bin/docker compose up --build --abort-on-container-exit
   ExecStop=/usr/bin/docker compose down

Step 2: Create the systemd Timer Unit
*************************************

Create the timer file:

.. code-block:: bash

   sudo nano /etc/systemd/system/spaceship-dns-updater.timer

Add the following content:

.. code-block:: ini

   [Unit]
   Description=Run spaceship-dns-updater periodically

   [Timer]
   # Run every 5 minutes
   OnCalendar=*:0/5
   Persistent=true

   [Install]
   WantedBy=timers.target

Step 3: Enable and Start the Timer
**********************************

Reload systemd, enable, and start the timer:

.. code-block:: bash

   sudo systemctl daemon-reexec
   sudo systemctl daemon-reload
   sudo systemctl enable --now spaceship-dns-updater.timer

Step 4: Monitor the Timer
*************************

Check upcoming runs:

.. code-block:: bash

   systemctl list-timers | grep spaceship-dns-updater

View logs:

.. code-block:: bash

   journalctl -u spaceship-dns-updater.service

Run the job immediately (for testing):

.. code-block:: bash

   sudo systemctl start spaceship-dns-updater.service


Manual Installation (Python Package)
====================================

You can also install directly with pip:

.. code-block:: bash

    pip install spaceship-dns-updater


Usage
#####

Run ``spaceship-dns-updater`` from the directory containing your config file.

To specify a different config file, use:

.. code-block:: bash

    spaceship-dns-updater --config <PATH_TO_YOUR_CONFIG_FILE>

Logs
####

On **Windows**, logs are located at:

``%LOCALAPPDATA%\spaceship-dns-updater\logs``  
(e.g., ``C:\Users\YOUR_NAME\AppData\Local\spaceship-dns-updater\logs``)

On **Linux/macOS**, logs are stored in:

``~/.local/state/spaceship-dns-updater/logs``

Logs rotate automatically after reaching 1 MB and are kept for up to 30 days.
