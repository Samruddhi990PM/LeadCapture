# STRIVE New Zealand – Lead Capture App
## Complete End-to-End Deployment Guide
### Stack: Pure HTML · Python serverless · Vercel Blob (no Postgres needed)

---

## 📁 Project Structure

```
strive-vercel/
├── api/
│   ├── submit-lead.py     ← POST: appends lead to Blob JSON file
│   └── get-leads.py       ← GET:  returns all leads as JSON
├── public/
│   ├── index.html         ← Lead capture form (full-screen mobile)
│   └── dashboard.html     ← Leads dashboard + CSV export
├── vercel.json            ← Routing config
├── requirements.txt       ← No pip packages needed (pure stdlib)
└── README.md
```

> **Database:** Vercel Blob stores all leads as a single `leads.json` file.
> No Postgres, no Edge Config — just Blob.

---

## ✅ Prerequisites

| Tool | Link | Verify |
|------|------|--------|
| Git | https://git-scm.com | `git --version` |
| GitHub account | https://github.com | — |
| Vercel account (free) | https://vercel.com | — |

No Node.js. No Python install needed locally. Everything runs on Vercel.

---

## 🚀 STEP 1 — Create a GitHub Repository

1. Go to **https://github.com/new**
2. Set:
   - **Repository name:** `strive-leads`
   - **Visibility:** Private ✅
3. Click **Create repository**
4. Copy the repo URL shown (e.g. `https://github.com/YOUR-NAME/strive-leads.git`)

---

## 🚀 STEP 2 — Push Files to GitHub

Open Terminal (Mac/Linux) or Git Bash (Windows):

```bash
# Enter project folder
cd strive-vercel

# Initialise git
git init

# Stage all files
git add .

# First commit
git commit -m "Initial commit – STRIVE lead capture"

# Link to your GitHub repo  ← paste YOUR repo URL here
git remote add origin https://github.com/YOUR-NAME/strive-leads.git

# Push
git branch -M main
git push -u origin main
```

✅ Refresh your GitHub page — all files should appear.

---

## 🚀 STEP 3 — Deploy to Vercel

1. Go to **https://vercel.com/new**
2. Click **Continue with GitHub** → authorise
3. Find `strive-leads` → click **Import**
4. On the config screen:
   - **Framework Preset:** Other (leave as-is)
   - **Root Directory:** `./` (leave as-is)
   - **Build & Output:** leave all blank
5. Click **Deploy**

⏳ ~60 seconds. You'll get a live URL like `https://strive-leads.vercel.app`

> ⚠️ Submitting the form will fail until Blob is connected (Step 4).
> Data is saved to browser localStorage as a fallback — nothing is lost.

---

## 🚀 STEP 4 — Add Vercel Blob Storage

### 4a. Create a Blob store

1. In your Vercel project dashboard, click **Storage** tab
2. Click **Create** → select **Blob**
3. Give it a name (e.g. `strive-leads-blob`)
4. Click **Create**

### 4b. Connect the store to your project

1. After creation, click **Connect to Project**
2. Select your `strive-leads` project
3. Choose environment: **Production, Preview, Development** (tick all)
4. Click **Connect**

Vercel automatically adds this environment variable to your project:
```
BLOB_READ_WRITE_TOKEN   ← used by both Python API functions
```

---

## 🚀 STEP 5 — Redeploy (picks up the Blob token)

**Option A — push an empty commit:**
```bash
git commit --allow-empty -m "Connect Blob storage"
git push
```

**Option B — from Vercel dashboard:**
Deployments tab → `...` on latest → **Redeploy**

⏳ ~30 seconds. Once live, submit a test lead from the form.

---

## ✅ STEP 6 — Test Everything

| Action | Expected result |
|--------|-----------------|
| Visit `/` | Full-screen form loads |
| Click radio button | Fields unlock & highlight |
| Fill form + submit | "You're In!" success screen |
| Visit `/dashboard` | Lead appears in table |
| Click "Export CSV" | Downloads `strive-leads.csv` |

---

## 🔄 How Blob Storage Works

All leads are stored as a **single JSON file** (`strive-leads/leads.json`) inside your Blob store.

- On every form submission, the API downloads the file, appends the new record, and re-uploads it.
- The dashboard reads the same file and renders the table.
- You can view / download this file directly in **Vercel → Storage → your Blob store → Browse**.

---

## 🔄 Making Future Changes

```bash
# Edit any file, then:
git add .
git commit -m "Your change description"
git push
# Vercel auto-deploys in ~30 seconds
```

---

## 📊 Viewing Raw Data in Vercel

1. Vercel dashboard → **Storage** tab → click your Blob store
2. Click **Browse** → open `strive-leads/` → click `leads.json`
3. Download or view all submissions as raw JSON

---

## 🔒 Protecting the Dashboard (Optional)

Add this at the very top of the `<script>` block in `dashboard.html`:

```javascript
const AUTH_PW = 'strive2025';  // change this to your password
const saved = localStorage.getItem('dash_auth');
if (saved !== AUTH_PW) {
  const entered = prompt('Dashboard password:');
  if (entered === AUTH_PW) {
    localStorage.setItem('dash_auth', AUTH_PW);
  } else {
    document.body.innerHTML = '<p style="color:#aaa;padding:40px;font-family:sans-serif">Access denied.</p>';
  }
}
```

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| "BLOB_READ_WRITE_TOKEN not set" error | Storage not connected — redo Step 4 then redeploy |
| Form submits but nothing in dashboard | Check localStorage fallback; Blob may not be connected yet |
| 500 error on submit | Vercel → Functions → Logs → check error message |
| Dashboard shows "No leads yet" | Submit a test lead first |
| Changes not visible after push | Hard refresh (`Ctrl+Shift+R`) or clear browser cache |
| Git push rejected | Run `git pull origin main --rebase` then push again |

---

## 📌 Your App URLs

| Page | URL |
|------|-----|
| Lead Form | `https://your-app.vercel.app/` |
| Dashboard | `https://your-app.vercel.app/dashboard` |
| Submit API | `https://your-app.vercel.app/api/submit-lead` (POST) |
| Get Leads API | `https://your-app.vercel.app/api/get-leads` (GET) |

---

## 🧰 Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Pure HTML + CSS + Vanilla JS |
| Backend | Python 3 (Vercel Serverless, zero pip deps) |
| Storage | Vercel Blob (JSON file, no SQL) |
| Hosting | Vercel (free tier) |
| Fonts | Google Fonts (Cormorant Garamond + Outfit) |
| Logo | Embedded as base64 (no external hosting) |
