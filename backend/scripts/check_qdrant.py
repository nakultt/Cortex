"""Check Qdrant HTTP API using QDRANT_URL and QDRANT_API_KEY from .env

Usage:
  python scripts/check_qdrant.py
"""
from dotenv import load_dotenv
import os
import sys
import requests

load_dotenv()


def check(timeout=5):
    url = os.getenv("QDRANT_URL")
    key = os.getenv("QDRANT_API_KEY")
    if not url:
        print("QDRANT_URL not set")
        return False
    headers = {}
    if key:
        headers["api-key"] = key
    try:
        # test collections endpoint
        collections_url = url.rstrip('/') + '/collections'
        r = requests.get(collections_url, headers=headers, timeout=timeout)
        r.raise_for_status()
        try:
            j = r.json()
            print("Qdrant OK: collections responded; keys:", list(j.keys())[:5])
        except Exception:
            print("Qdrant OK: non-JSON response with status", r.status_code)
        return True
    except requests.HTTPError as http_e:
        print("Qdrant HTTP error:", http_e, getattr(http_e.response, 'text', None))
        return False
    except Exception as e:
        print("Qdrant ERROR:", e)
        return False

if __name__ == '__main__':
    ok = check()
    sys.exit(0 if ok else 1)
