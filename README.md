# LinkedIn Auto-Post Bot 🤖

Automatically generates and publishes recruiter-targeted LinkedIn posts 3x per week using Claude AI + Buffer.

**Schedule:** Monday / Wednesday / Friday at 10:00 AM EST

---

## How It Works

```
GitHub Actions (cron) → generate_post.py → Claude API (web search) → Buffer API → LinkedIn
```

1. GitHub Actions triggers the script on schedule
2. Claude picks a topic, searches the web for latest news, writes a post
3. Post is queued in Buffer → auto-publishes to LinkedIn

---

## Setup (One-Time)

### Step 1 — Create a Buffer App

1. Go to **https://buffer.com/developers/apps**
2. Click **"Create an App"**
3. Fill in:
   - **Name:** `LinkedIn Auto Bot` (anything works)
   - **Website:** `http://localhost`
   - **Callback URL:** `http://localhost`
4. Save your **Client ID** and **Client Secret**

### Step 2 — Get Your Buffer Token + Profile ID

1. Open `get_buffer_token.py`
2. Replace `YOUR_CLIENT_ID_HERE` and `YOUR_CLIENT_SECRET_HERE` with your values
3. Run it:
   ```bash
   pip install requests
   python get_buffer_token.py
   ```
4. A browser window will open → click **Authorize**
5. Copy the redirect URL and paste it back into the terminal
6. The script will print your **BUFFER_ACCESS_TOKEN** and **BUFFER_PROFILE_ID**

> ⚠️ Make sure LinkedIn is connected in your Buffer account before running this.

### Step 3 — Get Your Anthropic API Key

1. Go to **https://console.anthropic.com**
2. Navigate to **API Keys** → Create a new key
3. Copy it

### Step 4 — Create a GitHub Repository

```bash
git init linkedin-autopost
cd linkedin-autopost
# Copy all files into this folder
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/YOUR_USERNAME/linkedin-autopost.git
git push -u origin main
```

### Step 5 — Add GitHub Secrets

1. Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add these three:

| Secret Name            | Value                          |
|------------------------|--------------------------------|
| `ANTHROPIC_API_KEY`    | Your Anthropic API key         |
| `BUFFER_ACCESS_TOKEN`  | From Step 2                    |
| `BUFFER_PROFILE_ID`    | From Step 2                    |

### Step 6 — Test It Manually

1. Go to **Actions** tab in your GitHub repo
2. Click **"LinkedIn Auto Post"** → **"Run workflow"** → **"Run"**
3. Check the logs to confirm the post was generated
4. Check Buffer dashboard to see the queued post

---

## Post Topics (Rotating)

| Topic | Example Focus |
|-------|--------------|
| Healthcare Data Analytics | Claims processing, HEDIS, CMS reporting trends |
| X12 EDI / HIPAA / ICD-10 | EDI 837/835 insights, compliance updates |
| Python / SQL Tips | Practical code patterns for data analysts |
| AI & Data Engineering News | Latest from the industry, with your take |
| Career Insights | Job market observations, lessons learned |

---

## Customizing

**Change posting schedule** — edit `.github/workflows/linkedin_post.yml`:
```yaml
# Format: minute hour day-of-week
# Current: Mon/Wed/Fri at 10 AM EST
- cron: '0 15 * * 1'   # Monday
- cron: '0 15 * * 3'   # Wednesday
- cron: '0 15 * * 5'   # Friday
```

**Add/edit topics** — edit the `TOPICS` list in `generate_post.py`

**Change post length or tone** — edit the `system_prompt` in `generate_post.py`

---

## Files

```
linkedin-autopost/
├── generate_post.py           # Main script
├── get_buffer_token.py        # One-time setup helper
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .github/
    └── workflows/
        └── linkedin_post.yml  # GitHub Actions schedule
```

---

## Cost Estimate

- **Claude API:** ~$0.02–0.05 per post (claude-opus-4-6 with web search)
- **Buffer:** Free plan supports 1 channel + 10 queued posts
- **GitHub Actions:** Free (2,000 min/month on free tier; this uses ~1 min/run)

**Monthly total: ~$0.30–0.60** for 12 posts/month 🎉
