from __future__ import annotations
import sys

if 'SUBMITTED_URL' not in globals():
    for j in sys.argv:
        if "http" in j:
            SUBMITTED_URL = j
            continue

if 'SCRAPE_ID' not in globals():
    for j in sys.argv:
        if "--scrape_id" in j:
            parts = j.split("=")
            SCRAPE_ID = int(parts[1])
            continue