spaceship-dns-updater
#####################

Tool for updating DNS records for domains hosted by https://www.spaceship.com/.

This tool utilizes https://github.com/bwiessneth/spaceship-api.

The script will detect your system's external IPv4 and/or IPv6 addresses and update the configured DNS records using your Spaceship API credentials.



Installation
************

.. code-block:: bash

    pip install spaceship-dns-updater


Usage
*****

Call ``spaceship-dns-updater`` from the directory where your config file is placed.

If you have several config files, specify the one you want:

.. code-block:: bash

    spaceship-dns-updater --config <PATH_TO_YOUR_CONFIG_FILE>


Logs
----

When running on **Windows**, the log files are located in:

``%LOCALAPPDATA%\spaceship-dns-updater\logs``  
(e.g., ``C:\Users\YOUR_NAME\AppData\Local\spaceship-dns-updater\logs``)

When using **Linux/macOS**, the log files are written to:

``~/.local/state/spaceship-dns-updater/logs``

These log files rotate automatically if they exceed 1 MB in size and are retained for up to 30 days.


🕒 Run Automatically with systemd (Linux only)
----------------------------------------------

To run ``spaceship-dns-updater`` on a schedule (e.g., every 15 minutes), you can create a user-level ``systemd`` timer.

Create the following two files in ``~/.config/systemd/user/``:

.. code-block:: ini

    # spaceship-dns-updater.service
    [Unit]
    Description=Spaceship DNS Updater

    [Service]
    Type=oneshot
    ExecStart=/usr/bin/python3 /home/YOUR_NAME/spaceship-dns-updater/spaceship_dns_updater.py
    WorkingDirectory=/home/YOUR_NAME/spaceship-dns-updater
    StandardOutput=append:%h/.local/state/spaceship-dns-updater/logs/systemd-output.log
    StandardError=append:%h/.local/state/spaceship-dns-updater/logs/systemd-error.log

.. code-block:: ini

    # spaceship-dns-updater.timer
    [Unit]
    Description=Run Spaceship DNS Updater every 15 minutes

    [Timer]
    OnBootSec=5min
    OnUnitActiveSec=5min
    Persistent=true

    [Install]
    WantedBy=timers.target

Then enable and start the timer:

.. code-block:: bash

    systemctl --user daemon-reload
    systemctl --user enable --now spaceship-dns-updater.timer

Check status or logs with:

.. code-block:: bash

    systemctl --user status spaceship-dns-updater.timer
    journalctl --user -u spaceship-dns-updater.service
    

Configuration
*************

Basic Configuration
-------------------

Create a YAML config file with your domain name, API credentials, and details about the DNS record you want to update.

The most basic config looks like this:

.. code-block:: yaml

    your-domain.com:
        api_key: <YOUR_API_KEY>
        api_secret: <YOUR_API_SECRET>
        records:
            - type: "A"
            name: "@"
            ttl: 1800


Records
-------

.. note::

   Only DNS records of type ``A`` (IPv4) and ``AAAA`` (IPv6) are currently supported
   for dynamic updates. All other record types (such as ``CNAME``, ``TXT``, ``MX``, etc.)
   will be ignored if included in the configuration file.

For each record you want to update, add it to the list of records:

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

For records of type ``A``, the IPv4 address obtained from https://www.ipify.org/ will be used.
If no IPv4 address is found, the record will be skipped.

Similarly, for records of type ``AAAA``, the IPv6 address retrieved from https://www.ipify.org/ will be used.
If no IPv6 address is available, the record will be skipped.


Multiple domains
----------------

If you are owner of multiple domains you can add them to the same YAML config file. 

.. code-block:: yaml

    your-first-domain.com:
        api_key: <YOUR_API_KEY>
        api_secret: <YOUR_API_SECRET>
        records:
            - type: "A"
            name: "@"
            ttl: 1800

    your-second-domain.com:
        api_key: <YOUR_API_KEY>
        api_secret: <YOUR_API_SECRET>
        records:
            - type: "A"
            name: "@"
            ttl: 1800
