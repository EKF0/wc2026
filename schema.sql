-- Cloudflare D1 Subscribers Schema
CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
