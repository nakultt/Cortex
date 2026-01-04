from dotenv import load_dotenv
import os
import sys
import psycopg2

load_dotenv()

def check(timeout=5):
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not set")
        return False

    try:
        conn = psycopg2.connect(
            url,
            connect_timeout=timeout,
            sslmode="require"
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                val = cur.fetchone()

        print("Postgres OK:", val[0])
        return True

    except Exception as e:
        print("Postgres ERROR:", e)
        return False

if __name__ == "__main__":
    ok = check()
    sys.exit(0 if ok else 1)
