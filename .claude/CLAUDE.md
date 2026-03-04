# Property Manager — Project Guide for Claude Code

## Project Overview

Internal web-based tool for a small property management business (3 users).
Primary purpose: log and review property-related activities in a structured and searchable way.
Not a public-facing system.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Templating | Jinja2 (server-side rendering, no SPA) |
| Database | SQLite |
| Frontend CSS | Bootstrap CDN (or Tailwind CDN) |
| Frontend JS | Vanilla JS only |
| Dynamic enhancements | HTMX (optional, additive only) |
| Reverse proxy | Nginx |
| WSGI server | Gunicorn |
| SSL | Let's Encrypt (Certbot) |
| Hosting | DigitalOcean Basic Droplet (Ubuntu LTS) |
| Address autocomplete | Geoapify Autocomplete API |
| PWA | Web App Manifest + Service Worker |

---

## Design Principles

- Simplicity above all else
- No React, no Vite, no SPA, no frontend build step
- No Kubernetes, no microservices, no managed DB
- Server-rendered HTML is the default approach
- HTMX is additive only — the app must work fully without it
- Minimal operational complexity, low cost, low maintenance

---

## Database Schema

### `users`
- `id` INTEGER PRIMARY KEY
- `username` TEXT NOT NULL UNIQUE
- `password_hash` TEXT NOT NULL

3 predefined users. No registration. No roles. No email.

### `locations`
- `id` INTEGER PRIMARY KEY
- `address` TEXT NOT NULL UNIQUE — canonical string returned by Geoapify
- `name` TEXT — friendly label (e.g. "Riverside Apt")
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

### `property_activities`
- `id` INTEGER PRIMARY KEY
- `location_id` INTEGER NOT NULL — FK to locations (ON DELETE RESTRICT)
- `user_id` INTEGER NOT NULL — FK to users
- `activity_date` DATETIME NOT NULL — when the activity happened (user-set, defaults to now)
- `note` TEXT NOT NULL — free text description

---

## Key Behaviours & Business Logic

### Authentication
- Session-based login with username + password
- Passwords hashed with bcrypt
- No 2FA, no OAuth, no external provider

### Location Handling (important)
- Address field uses Geoapify Autocomplete API directly from the browser
- On form submit, Flask backend checks if the Geoapify-returned address string already exists in `locations`
- Query: `SELECT id FROM locations WHERE address = ?`
- If exists: reuse that `location_id`
- If not: insert new row into `locations`, use new `id`
- User never sees or manages this deduplication — it's silent and automatic
- Geoapify API key must come from environment variable, injected via Jinja template variable

### Activity Deletion
- Inline delete on the activity list page
- Activities can be deleted freely
- Locations cannot be deleted if activities reference them (ON DELETE RESTRICT)

### Activity Edit
- Not in scope (may be added later)

---

## Pages

### Page 1 — Create Activity + Activity List (single page)
- Form at top: location (Geoapify autocomplete), activity date/time, person name, note
- Activity table below with pagination, filtering (date range, address, person name), sort by date desc
- Inline delete button per row
- CSV export button (respects active filters)

### No other pages required beyond login.

---

## Geoapify Integration

- Use Geoapify Autocomplete API
- Trigger on keyup with debounce (~300ms)
- Show dropdown of address suggestions
- On selection, populate a hidden field with the canonical address string
- API key injected from environment: `GEOAPIFY_API_KEY`

---

## PWA

- `manifest.json` — app name, icons, theme color, display: standalone
- `service-worker.js` — cache app shell for fast load; no offline data sync needed
- Requires HTTPS (already covered by Let's Encrypt)

---

## Environment Variables

```
SECRET_KEY=...
GEOAPIFY_API_KEY=...
```

---

## Deployment

- Ubuntu LTS on DigitalOcean Basic Droplet (1GB RAM, ~$6/month)
- Python virtualenv
- Gunicorn managed via systemd
- Nginx as reverse proxy
- Certbot for SSL
- Deploy: SSH → git pull → restart gunicorn service
- A `deploy.sh` script should handle all three steps

### Backup
- Daily cron job copies SQLite file to backup folder
- Optionally upload to DigitalOcean Spaces or Backblaze B2
- Retain last 7–30 days

---

## Out of Scope

- Public API
- CI/CD pipeline
- Role-based access control
- Email or notifications
- Contacts/persons table (person_name is free text on activity)
- Fuzzy address matching