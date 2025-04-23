# Zabbix Nexus Blobstore Monitoring

A Python script for discovering Nexus blobstores and sending metrics to Zabbix for monitoring.

## Features

- Discovers all available Nexus blobstores via Nexus REST API
- Sends metrics to Zabbix server using Zabbix trapper protocol
- Monitors:
    - Blob count per blobstore
    - Total size in bytes per blobstore
    - Available space in bytes per blobstore
- Automatically creates Zabbix-compatible key names by sanitizing blobstore names

## Requirements

- Python 3.x
- `requests` library (can be installed via `pip install requests`)
- Nexus Repository with REST API access
- Zabbix server with properly configured trapper items

## Installation

1. Clone this repository or download the script to your Zabbix server/proxy:

    ```
    git clone https://github.com/gamelton/zabbix-discovery-rule.git
    ```

    
2. Ensure Python 3 and required dependencies are installed:
    
    ```
    pip install requests
    ```

3. Make the script executable:

    ```
    chmod +x zabbix-nexus-blobstores.py
    ```

## Configuration

### Zabbix Configuration

1. Create a host in Zabbix representing your Nexus server
2. Create a discovery rule with:

    - Type: Zabbix agent
    - Key: nexus.blobstore.discovery
    - Update interval: Appropriate for your needs (e.g., 1h)

3. For each discovered blobstore, create item prototypes for:

    - Blob count
    - Total size in bytes
    - Available space in bytes

### Script Usage

The script requires four arguments:

```
./zabbix-nexus-blobstores.py <zabbix_monitored_host> <nexus_address> <nexus_user> <nexus_password>
```

Where:

- zabbix_monitored_host: The hostname as configured in Zabbix
- nexus_address: Nexus server address (hostname or IP)
- nexus_user: Nexus username with API access
- nexus_password: Password for the Nexus user

## Scheduling

Set up a cron job or systemd timer to run the script periodically. Example cron job running every hour:

```
0 * * * * /path/to/zabbix-nexus-blobstores.py "Nexus Host" "nexus.example.com" "monitoring_user" "password" >/dev/null 2>&1
```

## Troubleshooting

1. Test the script manually with:

    ```
    ./zabbix-nexus-blobstores.py "Test Host" "nexus.example.com" "user" "password"
    ```

2. Check Zabbix server logs for trapper items
3. Uncomment the response debug line in the script (line 62) to see Zabbix server responses
