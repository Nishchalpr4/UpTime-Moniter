CREATE TABLE IF NOT EXISTS monitored_urls (
    id         SERIAL PRIMARY KEY,
    url        TEXT NOT NULL UNIQUE,
    label      TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS health_checks (
    id            SERIAL PRIMARY KEY,
    url_id        INTEGER REFERENCES monitored_urls(id) ON DELETE CASCADE,
    status        TEXT NOT NULL,
    status_code   INTEGER,
    response_time INTEGER,
    checked_at    TIMESTAMPTZ DEFAULT NOW()
);
