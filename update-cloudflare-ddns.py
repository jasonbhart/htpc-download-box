#!/usr/bin/python3
from cloudflare_ddns import CloudFlare
import sys

if len(sys.argv) > 1:
    cf = CloudFlare(sys.argv[1], sys.argv[2], sys.argv[3], False)
    print(cf.sync_dns_from_my_ip()) 
else:
    print("Usage: python update.py <email> <API-key> <domain>")
