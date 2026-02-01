# Click-only Deploy Guide (Supabase + Render + Netlify)

## 1) Supabase: create DB + tables
1. Create a Supabase project.
2. Open **SQL Editor** → New query.
3. Paste and run: `supabase/schema.sql` (entire file).

Then grab:
- **Database connection string (URI)**: Supabase → Project Settings → Database → Connection string.

## 2) Render: deploy backend API
1. Create a **new Web Service** from your GitHub repo.
2. Root Directory: `backend`
3. Environment: **Python**
4. Build Command:
   ```
   pip install -r requirements.txt
   ```
5. Start Command:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 10000
   ```

### Render environment variables
Set these in Render → Service → Environment:
- `DATABASE_URL` = (Supabase connection string URI)
- `JWT_SECRET` = (long random string)
- `INIT_USERNAME` = (your shared username, e.g. Store3629)
- `INIT_PASSWORD` = (a NEW password you haven't typed in chat)

The app will create the initial shared login on first start if none exists.

After deploy, test:
- `https://<your-render-service>.onrender.com/health` should return `{"ok": true}`

## 3) Netlify: deploy frontend PWA
1. Netlify → Add new site → Import from Git.
2. Pick your GitHub repo.
3. Base directory: `frontend`
4. Build command: `npm run build`
5. Publish directory: `dist`

### Netlify environment variables
Netlify Site → Site configuration → Environment variables:
- `VITE_API_URL` = `https://<your-render-service>.onrender.com`

Trigger a new deploy.

## 4) Install on iPhone as an app
1. Open the Netlify URL in Safari
2. Share → Add to Home Screen
3. Name: **Store 3729 Inventory**

## 5) Rotate the shared password
After first login:
Settings → Change Login (creates a new shared username/password).
