# 🚀 Pushing this project to GitHub (step by step)

You'll run these yourself — that's how you learn git. I've put the project folder on your computer
already; these commands turn it into a GitHub repo at **github.com/Jenzzzz7/airline-otp-analysis**
(that exact name matters — it's the link already in your resume).

Open **Git Bash**, **PowerShell**, or the **VS Code terminal** in the project folder.

---

## One-time setup (skip if you've done it before)

```bash
git config --global user.name "Jenoah Gonsalves"
git config --global user.email "jenoah2004@gmail.com"
```

Check whether the GitHub CLI is installed and logged in:
```bash
gh auth status
```
- If it says you're logged in → great, use **Option A** below.
- If `gh` isn't found or you're not logged in → use **Option B** (web + git), it's just as easy.

---

## Option A — with the GitHub CLI (fastest)

From inside the `airline-otp-analysis` folder:

```bash
git init                          # start tracking this folder with git
git add .                         # stage every file (respects .gitignore)
git commit -m "Airline on-time performance analysis: SQL, Power BI, Excel"
gh repo create airline-otp-analysis --public --source=. --push
```

That last line creates the repo on your GitHub **and** pushes in one step. Done — visit
`https://github.com/Jenzzzz7/airline-otp-analysis`.

---

## Option B — with the website + git (no CLI needed)

1. Go to **github.com/new**.
2. Repository name: **`airline-otp-analysis`** (exactly). Visibility: **Public**. Do **not** tick
   "Add a README" (you already have one). Click **Create repository**.
3. GitHub shows you a URL like `https://github.com/Jenzzzz7/airline-otp-analysis.git`. Copy it.
4. Back in your terminal, inside the project folder:

```bash
git init
git add .
git commit -m "Airline on-time performance analysis: SQL, Power BI, Excel"
git branch -M main
git remote add origin https://github.com/Jenzzzz7/airline-otp-analysis.git
git push -u origin main
```

When it asks you to sign in, use your browser or a Personal Access Token (GitHub will prompt).

---

## What each command actually does (so it's not magic)

| Command | What it does |
|---|---|
| `git init` | Turns the folder into a git repository (starts version history) |
| `git add .` | **Stages** your changes — tells git "include these in the next snapshot" |
| `git commit -m "..."` | Saves a **snapshot** with a message describing it |
| `git branch -M main` | Names your main branch `main` (the modern default) |
| `git remote add origin <url>` | Links your local repo to the one on GitHub |
| `git push -u origin main` | Uploads your commits to GitHub |

After the first push, your everyday loop is just three commands:
```bash
git add .
git commit -m "describe what changed"
git push
```

---

## After it's live — do these three things

1. **Add the live Power BI link** to the README (edit `README.md`, commit, push) once you've published
   the dashboard.
2. **Add a dashboard screenshot:** take a screenshot of your Power BI dashboard, save it as
   `docs/dashboard.png`, and the README already has a commented line ready to show it.
3. **Pin the repo** on your GitHub profile (profile → Customize your pins) so it's the first thing
   recruiters see.

> Note: the large raw data file (`data/fact_flights.csv`, 46 MB) is intentionally **not** pushed — it's
> in `.gitignore`. The repo ships the gzipped version (`fact_flights.csv.gz`) and `build_data.py`
> regenerates it. This keeps the repo small and is standard practice for data projects.
