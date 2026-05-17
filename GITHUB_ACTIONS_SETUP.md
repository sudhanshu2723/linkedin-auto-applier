# 🚀 GitHub Actions Setup — Free Daily Bot Hosting

## How it works
GitHub Actions runs your bot on a free Ubuntu VM every day at 8:30 AM IST (3:00 AM UTC).
No server needed. No cost. 2000 free minutes/month (bot uses ~200 min/day).

---

## Step 1 — Push to GitHub

```bash
# If you haven't already, create a GitHub repo and push
git init
git add .
git commit -m "LinkedIn auto job applier"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

> ⚠️ Make sure `.gitignore` excludes `config/secrets.py` so your credentials aren't public.

---

## Step 2 — Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 4 secrets:

| Secret Name | Value |
|-------------|-------|
| `LINKEDIN_USERNAME` | `sudhanshu2723@gmail.com` |
| `LINKEDIN_PASSWORD` | `Algebra"1234` |
| `OPENAI_API_KEY` | `sk-proj-TG0eiTx9S05-...` |
| `RESUME_BASE64` | *(run step 3 below)* |

---

## Step 3 — Encode your resume

Run this locally to get the base64 string for your resume:

```bash
python encode_resume_for_github.py > resume_b64.txt
```

Open `resume_b64.txt`, copy the entire content, paste as the `RESUME_BASE64` secret.

---

## Step 4 — Update .gitignore

Make sure these are in `.gitignore` so secrets stay private:

```
config/secrets.py
all resumes/
all excels/
logs/
resume_b64.txt
```

---

## Step 5 — Trigger manually to test

Go to your repo → **Actions** → **LinkedIn Auto Job Applier - Daily Run** → **Run workflow**

Watch the logs live. After it works, it will run automatically every day.

---

## Schedule

The bot runs at **3:00 AM UTC = 8:30 AM IST** every day.

To change the time, edit `.github/workflows/daily_bot.yml`:
```yaml
schedule:
  - cron: '0 3 * * *'   # Change this
```

Cron format: `minute hour day month weekday`
- `0 3 * * *` = 3:00 AM UTC daily
- `30 2 * * *` = 2:30 AM UTC daily  
- `0 1 * * 1-5` = 1:00 AM UTC weekdays only

---

## View results

After each run:
1. Go to **Actions** tab → click the latest run
2. Download the **bot-logs** artifact to see:
   - `logs/github_actions_run.log` — full console output
   - `all excels/all_applied_applications_history.csv` — jobs applied to

---

## Troubleshooting

### Bot applies 0 jobs
- Check if LinkedIn login worked in the logs
- LinkedIn may require 2FA — disable it or use an app password

### Workflow fails immediately
- Check all 4 secrets are set correctly
- Check the Actions tab for the error message

### To disable temporarily
Go to **Actions** → **LinkedIn Auto Job Applier** → **...** → **Disable workflow**

---

## Free tier limits

| Resource | GitHub Free | Bot Usage |
|----------|-------------|-----------|
| Minutes/month | 2,000 | ~200/day = 6,000/month ⚠️ |
| Storage | 500 MB | ~10 MB/run |
| Concurrent jobs | 20 | 1 |

> ⚠️ 45 jobs/day with 45s–3min gaps = ~3-4 hours/run = ~90-120 min of compute.
> Free tier gives 2000 min/month. That's ~16-22 days of runs per month.
> For full month coverage, reduce `max_applications_per_day` to 25 or use a paid plan ($4/month).
