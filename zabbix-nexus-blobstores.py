#!/usr/bin/env python3

# Input:
#   ./zabbix-nexus-blobstores.py <zabbix_monitored_host> <nexus_address> <nexus_user> <nexus_password>

# Macros:
    # {$NEXUS_ADDRESS}
    # {$NEXUS_USER}
    # {$NEXUS_PASSWORD}

# Requirements:
    # nexus	priveleages/nx-blobstores-read	
    # nexus	roles/zbxapi priveleges: nx-blobstores-read
    # nexus	user/zbxapi roles: zbxapi
    
import requests
import re
import sys
import socket
import struct
import json
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Option 1: Send zabbix discovery and send zabbix trapper

if len(sys.argv) == 5:

    discoveryJSON = []
    trapperJSON = []

    zabbixMonitoredHost = sys.argv[1]
    nexusAddress = sys.argv[2]
    nexusUser = sys.argv[3]
    nexusPassword = sys.argv[4]

        # Blobstore

    blobstoreURL = f'https://{nexusAddress}/service/rest/v1/blobstores'

    try:
        response = requests.get(blobstoreURL, auth=(nexusUser, nexusPassword), verify=False)
        jsonObject = response.json()
    except BaseException as error:
        sys.exit(1)

    for blob in jsonObject:
        name = blob['name']
        unavailable = blob['unavailable']
        if unavailable != False:
            continue
        blobCount = int(blob['blobCount'])
        totalSizeInBytes = int(blob['totalSizeInBytes'])
        availableSpaceInBytes = int(blob['availableSpaceInBytes'])

        # Create zabbix key name
        pattern = '[^0-9a-zA-Z_\-\.]+'
        zabbixKeyName = re.sub(pattern, "-", name)

        # JSON for zabbix discovery
        discoveryJSON.append({'{#NEXUS_BLOB_NAME}': zabbixKeyName})

        # Zabbix trap item key name
        blobCountTrapKeyName = f'nexus.blobstore.[{zabbixKeyName},blobCount]'
        totalSizeInBytesTrapKeyName = f'nexus.blobstore.[{zabbixKeyName},totalSizeInBytes]'
        availableSpaceInBytesTrapKeyName = f'nexus.blobstore.[{zabbixKeyName},availableSpaceInBytes]'

        # JSON for zabbix item trap
        trapperJSON.append({'host': zabbixMonitoredHost, 'key': blobCountTrapKeyName, 'value': blobCount})
        trapperJSON.append({'host': zabbixMonitoredHost, 'key': totalSizeInBytesTrapKeyName, 'value': totalSizeInBytes})
        trapperJSON.append({'host': zabbixMonitoredHost, 'key': availableSpaceInBytesTrapKeyName, 'value': availableSpaceInBytes})

    # Send zabbix discovery
    print(json.dumps(discoveryJSON))

    # Send traps in one packet
    # Assemble packet
    trapperJSONfull = json.dumps({"request": "sender data", "data": trapperJSON})

    requestEncoded = trapperJSONfull.encode('utf-8')
    header = struct.pack('<4sBQ', b'ZBXD', 1, len(requestEncoded))
    packet = header + requestEncoded

    # Connect to server (script runs locally on zabbix)
    zbx_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    zbx_client.connect(('127.0.0.1', 10051))

    # Send packet to server
    zbx_client.sendall(packet)
    response = zbx_client.recv(4096)
    zbx_client.close()

    # Troubleshoot. Uncomment to see response
    # print (response[13:])

    sys.exit(0)


    # Option 2: Help.

if len(sys.argv) != 5:
    print ("""
    This script calls Nexus API and
        - returns blob names for discovery rule
        - sends zabbix trap items to zabbix server

    Usage: ./zabbix-nexus-blobstores.py <zabbix_monitored_host> <nexus_address> <nexus_user> <nexus_password>
    """)
    sys.exit(0)

