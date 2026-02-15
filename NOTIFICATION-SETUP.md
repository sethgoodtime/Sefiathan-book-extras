# Notification Setup Guide

Two ways to get texted when your Sefiathan book hits milestones or is complete. Pick one or use both.

---

## Option A: Twilio (Automated Texts via GitHub Actions)

Texts are sent automatically — you never have to trigger anything. You'll get notified at milestones (Day 30, 100, 200, 300) monthly previews, and when the book hits 365 entries.

### Step 1: Create a Twilio Account

1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio) and sign up
2. Verify your personal phone number (the one you want texts sent TO)
3. On the Twilio Console dashboard, note your:
   - **Account SID** (starts with `AC...`)
   - **Auth Token** (click to reveal)
4. Get a free Twilio phone number:
   - Console → Phone Numbers → Manage → Buy a Number
   - Pick any US number (free on trial)
   - This is the number texts will come FROM

### Step 2: Add Secrets to GitHub

Go to your repo → Settings → Secrets and variables → Actions → New repository secret.

Add these four secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `TWILIO_ACCOUNT_SID` | Your Account SID | `AC1234567890abcdef...` |
| `TWILIO_AUTH_TOKEN` | Your Auth Token | `abc123def456...` |
| `TWILIO_FROM_NUMBER` | Your Twilio phone number | `+15551234567` |
| `NOTIFY_TO_NUMBER` | Your personal phone number | `+15559876543` |

**Important:** Phone numbers must include country code with `+` prefix.

### Step 3: Add the Files to Your Repo

Copy these files into your project:
- `scripts/notify_and_compile.py` → goes in your `scripts/` folder
- `.github/workflows/milestones.yml` → goes in `.github/workflows/`

### Step 4: Update requirements.txt

Add `twilio` to your `requirements.txt`:

```
anthropic>=0.40.0
twilio>=9.0.0
```

### Step 5: Test It

1. Go to your repo → Actions tab
2. Find "Book Milestones & Notifications" 
3. Click "Run workflow" 
4. Check "Send text regardless of milestone" → true
5. Click "Run workflow"
6. You should receive a text within a minute

### What You'll Get

| Trigger | When | Message |
|---------|------|---------|
| **Monthly preview** | 1st of every month at noon UTC | Entry count, word count, link |
| **Milestone** | Day 30, 100, 200, 300 | Progress update with link |
| **Book complete** | Day 365 | "YOUR BOOK IS DONE" + link |
| **Manual** | Whenever you trigger the workflow | Current stats + link |

### Twilio Free Tier Notes

- Trial accounts get ~$15 in free credit
- Each text costs ~$0.0079
- That's enough for ~1,900 texts (way more than you need)
- Trial texts include a "Sent from your Twilio trial account" prefix
- To remove the prefix, upgrade your Twilio account ($20 minimum)

---

## Option B: iPhone Shortcut (Manual or Scheduled)

No Twilio needed. Your iPhone checks GitHub and texts you the link using iMessage.

### Build the Shortcut

Create a new Shortcut with these actions:

#### Actions (in order):

1. **Get Contents of URL**
   - URL: `https://api.github.com/repos/sethgoodtime/Sefiathan-book/contents/chapters`
   - Method: GET
   - Headers:
     - `Authorization`: `Bearer YOUR_GITHUB_TOKEN`
     - `Accept`: `application/vnd.github.v3+json`

2. **Count** → Count Items (this gives you the number of chapter files)

3. **If** → Count is greater than or equal to 365
   - **Text** → `Your Sefiathan book is DONE! 365 entries complete. Read it here: https://github.com/sethgoodtime/Sefiathan-book/blob/main/manuscript.md`
   - **Send Message** → Send the Text to yourself (or anyone)
4. **Otherwise**
   - **Text** → `Sefiathan book update: [Count] of 365 days complete. Keep going!`
   - **Send Message** → Send the Text to yourself
5. **End If**

#### Automate It (Optional):

1. Go to the **Automation** tab in Shortcuts
2. Create a new Personal Automation
3. Trigger: **Time of Day** → pick a weekly check-in time (e.g., Sunday 9:00 AM)
4. Action: **Run Shortcut** → select your book check shortcut
5. Turn OFF "Ask Before Running"

### Advanced: Monthly Compile + Text

If you want the Shortcut to also trigger the manuscript compilation:

1. **Get Contents of URL**
   - URL: `https://api.github.com/repos/sethgoodtime/Sefiathan-book/actions/workflows/milestones.yml/dispatches`
   - Method: POST
   - Headers:
     - `Authorization`: `Bearer YOUR_GITHUB_TOKEN`
     - `Accept`: `application/vnd.github.v3+json`
   - Request Body (JSON):
     ```json
     {
       "ref": "main",
       "inputs": {
         "force_notify": "true"
       }
     }
     ```

This triggers the GitHub Action remotely from your phone, which compiles the book AND sends you a Twilio text with the link. Best of both worlds.

---

## Which Should You Pick?

| | Twilio | Shortcuts |
|--|--------|-----------|
| **Fully automated** | Yes — never touch it | Semi — runs on schedule but needs iPhone on |
| **Cost** | Free (trial) or ~$0.10/year | Free |
| **Setup difficulty** | Medium (API keys, secrets) | Easy (visual builder) |
| **Works if phone is off** | Yes (runs on GitHub servers) | No (runs on your phone) |
| **Sends iMessage** | No (sends SMS from Twilio number) | Yes (native iMessage) |
| **Can text other people** | Yes | Yes |

**My recommendation:** Set up both. Twilio handles the automated milestones (set it and forget it). Use the Shortcut for on-demand "how's my book doing?" checks whenever you're curious.
