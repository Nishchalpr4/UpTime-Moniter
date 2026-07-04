import os
import time
import httpx
import psycopg2
import psycopg2.extras
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

# ─────────────────────────────────────────
# 1. DATABASE
# One function that returns a fresh connection.
# Simple. No pool. Fine for a few dozen URLs.
# ─────────────────────────────────────────
DB_URL = os.environ.get("DATABASE_URL", "postgresql://uptime:secret@db:5432/uptime")

def get_db():
    return psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)


# ─────────────────────────────────────────
# 2. SCHEDULER (background URL pinger)
# Every 60 seconds: fetch all URLs, ping each
# one with httpx, save the result to DB.
# ─────────────────────────────────────────
def ping_all():
    print("⏱ Scheduler: pinging all URLs...")
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, url FROM monitored_urls")
        urls = cur.fetchall()
        print(f"  Found {len(urls)} URL(s) to ping")

        for row in urls:
            try:
                start = time.time()
                r = httpx.get(row["url"], timeout=10, follow_redirects=True)
                latency = int((time.time() - start) * 1000)
                status = "up" if r.status_code < 400 else "down"
                code = r.status_code
                print(f"  {row['url']} → {status} ({code}, {latency}ms)")
            except Exception as e:
                latency, status, code = None, "down", None
                print(f"  {row['url']} → down (error: {e})")

            cur.execute(
                "INSERT INTO health_checks (url_id, status, status_code, response_time) VALUES (%s, %s, %s, %s)",
                (row["id"], status, code, latency)
            )

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Ping cycle complete")
    except Exception as e:
        print(f"❌ Scheduler error: {e}")


def ping_one(url_id: int, url: str):
    """Ping a single URL immediately and save the result. Used on new URL add."""
    print(f"⚡ Instant ping: {url}")
    try:
        start = time.time()
        r = httpx.get(url, timeout=10, follow_redirects=True)
        latency = int((time.time() - start) * 1000)
        status = "up" if r.status_code < 400 else "down"
        code = r.status_code
        print(f"  → {status} ({code}, {latency}ms)")
    except Exception as e:
        latency, status, code = None, "down", None
        print(f"  → down (error: {e})")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO health_checks (url_id, status, status_code, response_time) VALUES (%s, %s, %s, %s)",
        (url_id, status, code, latency)
    )
    conn.commit()
    cur.close()
    conn.close()


scheduler = BackgroundScheduler()
scheduler.add_job(ping_all, "interval", minutes=1)


# ─────────────────────────────────────────
# 3. FASTAPI APP
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    # Run one ping immediately on boot so first results appear right away
    import threading
    threading.Thread(target=ping_all, daemon=True).start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# 4. API ROUTES
# ─────────────────────────────────────────

# The only Pydantic model we need — validates the POST body
class UrlIn(BaseModel):
    url: str
    label: str = ""


@app.get("/api/urls")
def list_urls():
    """Return all URLs with their latest ping status."""
    conn = get_db()
    cur = conn.cursor()
    # LATERAL JOIN grabs only the most recent health_check per URL
    cur.execute("""
        SELECT u.id, u.url, u.label, u.created_at,
               h.status, h.status_code, h.response_time, h.checked_at
        FROM monitored_urls u
        LEFT JOIN LATERAL (
            SELECT * FROM health_checks
            WHERE url_id = u.id
            ORDER BY checked_at DESC LIMIT 1
        ) h ON true
        ORDER BY u.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/urls", status_code=201)
def add_url(body: UrlIn):
    """Register a new URL to monitor."""
    url = body.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(400, "URL must start with http:// or https://")
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO monitored_urls (url, label) VALUES (%s, %s) RETURNING *",
            (url, body.label)
        )
        conn.commit()
        new_row = dict(cur.fetchone())
        # Ping the new URL immediately synchronously
        ping_one(new_row["id"], new_row["url"])
        return new_row
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(409, "URL already being monitored")
    finally:
        cur.close()
        conn.close()


@app.delete("/api/urls/{url_id}", status_code=204)
def delete_url(url_id: int):
    """Remove a URL from monitoring."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM monitored_urls WHERE id = %s", (url_id,))
    conn.commit()
    cur.close()
    conn.close()


@app.get("/api/urls/{url_id}/history")
def get_history(url_id: int):
    """Last 50 ping results for a URL."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM health_checks WHERE url_id = %s ORDER BY checked_at DESC LIMIT 50",
        (url_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]
