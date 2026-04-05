#!/usr/bin/env python3
"""
List all available process templates
"""
import os
import sys
import requests
from requests.auth import HTTPBasicAuth

ORGANIZATION = "ncryptedcloud"

PAT = os.environ.get('AZURE_DEVOPS_PAT')
if not PAT:
    print("ERROR: AZURE_DEVOPS_PAT environment variable not set")
    sys.exit(1)

url = f"https://dev.azure.com/{ORGANIZATION}/_apis/work/processes?api-version=7.1-preview.2"

response = requests.get(url, auth=HTTPBasicAuth('', PAT))
response.raise_for_status()

processes = response.json()['value']

print("Available Process Templates:")
print("=" * 80)
for process in processes:
    print(f"Name: {process['name']}")
    print(f"  Type ID: {process['typeId']}")
    print(f"  Is Enabled: {process.get('isEnabled', 'N/A')}")
    print(f"  Is Default: {process.get('isDefault', 'N/A')}")
    print()
