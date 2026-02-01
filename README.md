# Store 3729 Inventory (PWA + API)

Phone-first inventory app for Store #3729 with:
- Shared login (username + password) with in-app rotation
- Items with smart units (case + base units) and partial cases
- Adjustments allowed
- Transfer tickets (borrow/lend) with statuses
- Offline-first (IndexedDB outbox) + multi-device sync to server
- History/event log backing inventory totals

## Deploy (Click-only)
You will use:
- Supabase (Postgres DB)
- Render (backend API)
- Netlify (frontend PWA)

See `DEPLOY_CLICK_ONLY.md`.

## Local Dev (optional)
You can run with Docker:
```bash
docker compose up --build
```
Then:
- API: http://localhost:8000/health
- Web: http://localhost:5173
