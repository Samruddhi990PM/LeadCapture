# STRIVE New Zealand – Lead Capture App
### Complete Deployment Guide: GitHub → Vercel + Postgres Database

---

## 📁 Project Structure

```
strive-vercel/
├── api/
│   ├── submit-lead.py     ← POST: saves lead to database
│   └── get-leads.py       ← GET:  returns all leads as JSON
├── public/
│   ├── index.html         ← Lead capture form (main page)
│   └── dashboard.html     ← Leads dashboard with table + CSV export
├── vercel.json            ← Vercel routing config
├── requirements.txt       ← Python dependency (psycopg2)
├── .gitignore
└── README.md
```

---

## ✅ Prerequisites (one-time setup)

Install these if you don't have them:

| Tool | Download | Check if installed |
|------|----------|--------------------|
| Git  | https://git-scm.com | `git --version` |
| A GitHub account | https://github.com | — |
| A Vercel account | https://vercel.com (free) | — |

> **No Node.js required.** Backend is pure Python, served by Vercel.

---

## 🚀 STEP 1 — Create a GitHub Repository

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name:** `strive-leads` (or any name you like)
   - **Visibility:** Private ✅ (recommended)
   - Leave all other options as default
3. Click **"Create repository"**
4. Copy the repository URL shown — it looks like:
   ```
   https://github.com/YOUR-USERNAME/strive-leads.git
   ```

---

## 🚀 STEP 2 — Push Files to GitHub

Open **Terminal** (Mac/Linux) or **Git Bash** (Windows), then:

```bash
# 1. Navigate into the project folder
cd strive-vercel

# 2. Initialise git
git init

# 3. Stage all files
git add .

# 4. Make first commit
git commit -m "Initial commit – STRIVE lead capture app"

# 5. Link to your GitHub repo (paste YOUR repo URL here)
git remote add origin https://github.com/YOUR-USERNAME/strive-leads.git

# 6. Push to GitHub
git branch -M main
git push -u origin main
```

✅ Refresh your GitHub repo page — you should see all files there.

---

## 🚀 STEP 3 — Deploy to Vercel

1. Go to **https://vercel.com/new**
2. Click **"Continue with GitHub"** and authorise Vercel
3. Find your `strive-leads` repository and click **"Import"**
4. On the configuration screen:
   - **Framework Preset:** leave as `Other`
   - **Root Directory:** leave as `./`
   - **Build & Output Settings:** leave all blank
5. Click **"Deploy"**

⏳ Wait ~60 seconds. Vercel will show a success screen with your live URL, e.g.:
```
https://strive-leads.vercel.app
```

> ⚠️ The form will load, but submitting will fail until the database is connected (Step 4). Data is saved to browser localStorage as a fallback — no leads are lost.

---

## 🚀 STEP 4 — Add a Postgres Database

### 4a. Create the database

1. In your Vercel project dashboard, click the **"Storage"** tab (top nav)
2. Click **"Create Database"**
3. Select **"Postgres"** → click **"Continue"**
4. Choose a name (e.g. `strive-leads-db`) and a region:
   - **Recommended for NZ:** `Singapore (sin1)` or `Sydney (syd1)` if available
5. Click **"Create"**

### 4b. Connect the database to your project

1. After creation, click **"Connect Project"**
2. Select your `strive-leads` project
3. Click **"Connect"**

Vercel automatically adds these environment variables to your project:
```
POSTGRES_URL
POSTGRES_PRISMA_URL
POSTGRES_URL_NON_POOLING
POSTGRES_USER
POSTGRES_HOST
POSTGRES_PASSWORD
POSTGRES_DATABASE
```

> The Python API uses `POSTGRES_URL` — it's set automatically, no action needed.

---

## 🚀 STEP 5 — Redeploy with Database

The environment variables only take effect after a new deployment:

**Option A — Push an empty commit:**
```bash
git commit --allow-empty -m "Connect database"
git push
```

**Option B — Trigger from Vercel dashboard:**
- Go to your project → **Deployments** tab → click **"..."** on the latest deployment → **"Redeploy"**

⏳ Wait ~30 seconds. The database table is **automatically created** on the first form submission.

---

## ✅ STEP 6 — Test Everything

1. Visit `https://your-app.vercel.app` — the lead form loads
2. Click the radio button, fill in the form, hit **"Claim My Exclusive Offer"**
3. Visit `https://your-app.vercel.app/dashboard` — your lead appears in the table
4. Click **"Export CSV"** to download all leads

---

## 🔄 Making Future Changes

Whenever you edit files, push them to GitHub and Vercel auto-deploys:

```bash
# After editing any file:
git add .
git commit -m "Describe your change"
git push
```

Vercel picks up the push and redeploys in ~30 seconds.

---

## 🔒 Protecting the Dashboard (Optional)

To prevent the public from accessing `/dashboard`, add a simple password gate.

Open `public/dashboard.html`, find the `<script>` tag and add at the very top:

```javascript
// Simple password gate — change 'strive2025' to your own password
const pw = localStorage.getItem('dash_auth');
if (pw !== 'strive2025') {
  const entered = prompt('Enter dashboard password:');
  if (entered === 'strive2025') {
    localStorage.setItem('dash_auth', 'strive2025');
  } else {
    document.body.innerHTML = '<p style="color:white;padding:40px;font-family:sans-serif">Access denied.</p>';
  }
}
```

For stronger protection, use [Vercel Password Protection](https://vercel.com/docs/security/deployment-protection) (Pro plan) or [Vercel Authentication](https://vercel.com/docs/security/vercel-authentication).

---

## 📊 Viewing Data Directly in Vercel

1. Vercel dashboard → **Storage** tab → click your database
2. Click **"Data"** tab — browse your `leads` table directly
3. Or use the **"Query"** tab to run SQL:
   ```sql
   SELECT * FROM leads ORDER BY created_at DESC;
   ```

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| Form submits but dashboard shows no leads | Check Storage tab — ensure DB is connected and redeployed |
| `500` error on submit | Check Vercel → Functions → logs for Python errors |
| Dashboard shows "No leads yet" | Submit a test lead from the form first |
| Deployment fails | Check `vercel.json` syntax; ensure `requirements.txt` exists |
| Changes not showing | Hard refresh browser (`Ctrl+Shift+R`) or clear cache |

---

## 📌 Your App URLs

| Page | URL |
|------|-----|
| Lead Form | `https://your-app.vercel.app/` |
| Dashboard | `https://your-app.vercel.app/dashboard` |
| Submit API | `https://your-app.vercel.app/api/submit-lead` |
| Get Leads API | `https://your-app.vercel.app/api/get-leads` |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Pure HTML + CSS + Vanilla JS (no framework) |
| Backend | Python 3 (Vercel Serverless Functions) |
| Database | Vercel Postgres (managed PostgreSQL) |
| Hosting | Vercel (free tier) |
| Fonts | Google Fonts (Cormorant Garamond + Outfit) |
| Logo | Embedded as base64 (no external image hosting needed) |
