# Setup Guide

Complete these steps in order. Budget ~30 minutes.

---

## 1. Set Anthropic Spend Limit (do this first)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Navigate to **Settings → Limits**
3. Set a **Monthly spend limit** of $5 (protects against runaway costs)
4. Create an API key under **API Keys** → **Create Key**
5. Copy the key — you'll need it in Step 4

---

## 2. Enable Gmail Dynamic Email (AMP)

1. Open Gmail → Settings (gear icon) → **See all settings**
2. Go to the **General** tab
3. Find **Dynamic email** → check **Enable dynamic email**
4. Click **Developer settings** → add your own Gmail address as an approved sender
5. Save changes

---

## 3. Create Gmail App Password

> Requires 2-Step Verification to be enabled on your Google account.

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select app: **Mail** / device: **Other** → name it "Daily Digest"
3. Copy the 16-character password

---

## 4. Update config.json

Open `config.json` and replace `YOUR_GMAIL_ADDRESS@gmail.com` with your actual address.

To add more stocks to your watchlist later:
```json
"watchlist": ["ATZ.TO", "AAPL", "VFV.TO"]
```

---

## 5. Create GitHub Fine-Grained PAT (for feedback voting)

1. Go to [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
2. Name: `daily-news-digest-vote`
3. Expiration: 1 year
4. Repository access: **Only select repositories** → `daily-news-digest`
5. Permissions: **Actions** → **Read and write**
6. Generate and copy the token
7. Open `feedback/index.html` and replace `YOUR_FINE_GRAINED_PAT_HERE` with this token

---

## 6. Add GitHub Actions Secrets

Go to: `https://github.com/crackerhands/daily-news-digest/settings/secrets/actions`

Add these two secrets:

| Secret name | Value |
|-------------|-------|
| `CLAUDE_API_KEY` | Your Anthropic API key from Step 1 |
| `GMAIL_APP_PASSWORD` | Your Gmail App Password from Step 3 |

---

## 7. Enable GitHub Pages

1. Go to `https://github.com/crackerhands/daily-news-digest/settings/pages`
2. Under **Source**: select **Deploy from a branch**
3. Branch: `main`, folder: `/feedback`
4. Click **Save**

---

## 8. Test the Workflow Manually

1. Go to `https://github.com/crackerhands/daily-news-digest/actions`
2. Click **Daily News Digest** → **Run workflow** → **Run workflow**
3. Watch the run — it should complete in ~60 seconds
4. Check your inbox

---

## 9. DST Reminder

The cron is set for **8am PDT (UTC-7)**. When clocks fall back in November, update `.github/workflows/daily_digest.yml`:

```yaml
- cron: "0 16 * * *"  # 8am PST (UTC-8)
```

And back to `0 15 * * *` in March.

---

## Future: Migrate Feedback App to Home Server

Replace the GitHub Actions vote trigger with a local Flask app on your Optiplex/Pi for richer feedback (per-story voting, history dashboard).
