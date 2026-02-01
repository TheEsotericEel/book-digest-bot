# 🚀 BookDigest Bot - Deployment Guide

Complete step-by-step guide to deploy and run BookDigest Bot in production.

## Prerequisites

- Python 3.8 or higher
- Telegram account
- 30 minutes of time

## Step 1: Create Telegram Bot (5 min)

### 1.1 Message BotFather

Open Telegram and search for [@BotFather](https://t.me/BotFather)

Send these commands:

```
/newbot
```

BotFather will ask for:
1. **Bot name:** "BookDigest Bot" (or any name you want)
2. **Bot username:** Must end in 'bot', e.g., `mybookdigestbot`

### 1.2 Save Your Token

BotFather will reply with:

```
Done! Congratulations on your new bot. You will find it at t.me/mybookdigestbot.
You can now add a description...

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
```

**Copy that token!** You'll need it in the next steps.

### 1.3 Optional: Customize Your Bot

```
/setdescription
```
Enter: "AI-powered book summaries - Get comprehensive summaries of any book instantly!"

```
/setabouttext
```
Enter: "📚 BookDigest delivers instant book summaries on Telegram. Cheaper than Blinkist!"

```
/setuserpic
```
Upload a book/brain icon image (optional)

## Step 2: Setup on Your Machine (10 min)

### 2.1 Install Python

**Check if Python is installed:**
```bash
python3 --version
```

If not installed:
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **Mac:** `brew install python3`
- **Linux:** `sudo apt-get install python3 python3-pip python3-venv`

### 2.2 Clone/Download Code

If you have Git:
```bash
git clone <your-repo-url>
cd BookDigestBot
```

Or just navigate to the folder:
```bash
cd /path/to/BookDigestBot
```

### 2.3 Create Virtual Environment

```bash
python3 -m venv venv
```

**Activate it:**
- **Linux/Mac:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

You should see `(venv)` in your terminal prompt.

### 2.4 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `python-telegram-bot==21.4` (Telegram Bot API)
- `requests==2.31.0` (HTTP requests for Google Books)

### 2.5 Set Bot Token

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**Windows (CMD):**
```cmd
set TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Make it permanent:**

Linux/Mac: Add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export TELEGRAM_BOT_TOKEN="your_token"' >> ~/.bashrc
source ~/.bashrc
```

Windows: Set via System Environment Variables (search "Environment Variables" in Start menu)

### 2.6 Initialize Database

```bash
python database.py
```

Output:
```
✅ Database initialized successfully
```

This creates `bookdigest.db` with all necessary tables.

## Step 3: Test the Bot (5 min)

### 3.1 Start Bot

```bash
python bot.py
```

Output:
```
2024-02-01 10:00:00 - INFO - 🚀 BookDigest Bot starting...
```

### 3.2 Test on Telegram

1. Open Telegram
2. Search for your bot username (e.g., `@mybookdigestbot`)
3. Click "Start" or send `/start`

You should receive the welcome message!

### 3.3 Test Commands

Try these:
```
/search Atomic Habits
/summary Atomic Habits
/credits
/library
/help
```

If everything works, **Ctrl+C** to stop the bot.

## Step 4: Run Bot Continuously (10 min)

The bot needs to run 24/7 to respond to users. Here are options:

### Option A: Screen/Tmux (Quick & Easy)

**Using screen (Linux/Mac):**
```bash
screen -S bookdigest
python bot.py
# Press Ctrl+A, then D to detach
```

To reattach later:
```bash
screen -r bookdigest
```

**Using tmux:**
```bash
tmux new -s bookdigest
python bot.py
# Press Ctrl+B, then D to detach
```

To reattach:
```bash
tmux attach -t bookdigest
```

### Option B: PM2 (Recommended for Production)

PM2 is a process manager that keeps your bot running.

**Install PM2:**
```bash
npm install -g pm2
```

**Create ecosystem file:**
```bash
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'bookdigest-bot',
    script: 'venv/bin/python',
    args: 'bot.py',
    interpreter: 'none',
    env: {
      TELEGRAM_BOT_TOKEN: 'your_token_here'
    },
    autorestart: true,
    watch: false,
    max_memory_restart: '500M'
  }]
}
EOF
```

**Start bot:**
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # Follow the instructions to enable auto-start on reboot
```

**Manage bot:**
```bash
pm2 status           # Check status
pm2 logs bookdigest-bot  # View logs
pm2 restart bookdigest-bot  # Restart
pm2 stop bookdigest-bot     # Stop
```

### Option C: Systemd Service (Linux)

Create `/etc/systemd/system/bookdigest.service`:

```ini
[Unit]
Description=BookDigest Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/BookDigestBot
Environment="TELEGRAM_BOT_TOKEN=your_token_here"
ExecStart=/path/to/BookDigestBot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable bookdigest
sudo systemctl start bookdigest
sudo systemctl status bookdigest
```

## Step 5: Setup Cron Job (10 min)

The cron worker runs daily to:
- Send book recommendations to Pro users
- Refresh weekly credits for free users
- Check expired subscriptions
- Clean up old data

### Linux/Mac: Crontab

```bash
crontab -e
```

Add this line (runs daily at 9 AM):
```bash
0 9 * * * cd /path/to/BookDigestBot && /path/to/BookDigestBot/venv/bin/python cron_worker.py >> /path/to/BookDigestBot/cron.log 2>&1
```

**Don't forget to set the token in cron:**

Option 1: Add to cron line:
```bash
0 9 * * * TELEGRAM_BOT_TOKEN="your_token" cd /path/to/BookDigestBot && /path/to/BookDigestBot/venv/bin/python cron_worker.py >> /path/to/BookDigestBot/cron.log 2>&1
```

Option 2: Create a wrapper script `run_cron.sh`:
```bash
#!/bin/bash
export TELEGRAM_BOT_TOKEN="your_token"
cd /path/to/BookDigestBot
source venv/bin/activate
python cron_worker.py
```

Make it executable:
```bash
chmod +x run_cron.sh
```

Then in crontab:
```bash
0 9 * * * /path/to/BookDigestBot/run_cron.sh >> /path/to/BookDigestBot/cron.log 2>&1
```

### Windows: Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "BookDigest Cron"
4. Trigger: Daily at 9:00 AM
5. Action: Start a program
   - Program: `C:\path\to\BookDigestBot\venv\Scripts\python.exe`
   - Arguments: `cron_worker.py`
   - Start in: `C:\path\to\BookDigestBot`
6. In "Conditions" tab: Uncheck "Start only if on AC power"
7. In "Settings" tab: Check "Run task as soon as possible after scheduled start is missed"

**Test it manually:**
```powershell
cd C:\path\to\BookDigestBot
venv\Scripts\activate
python cron_worker.py
```

## Step 6: Monitoring (Ongoing)

### Check Bot Status

```bash
# If using PM2
pm2 status

# If using systemd
sudo systemctl status bookdigest

# If using screen
screen -ls
```

### View Logs

```bash
# Bot logs
tail -f bot.log

# Cron logs
tail -f cron_worker.log

# PM2 logs
pm2 logs bookdigest-bot
```

### Check Stats

```bash
python stats.py
```

This shows:
- Total users, free vs pro
- Revenue
- Engagement metrics
- System health

**Run this weekly** to track growth!

## Step 7: Production Best Practices

### 7.1 Database Backups

**Daily backup:**
```bash
# Add to crontab
0 3 * * * cp /path/to/BookDigestBot/bookdigest.db /path/to/backups/bookdigest-$(date +\%Y\%m\%d).db
```

**Keep last 7 days:**
```bash
find /path/to/backups -name "bookdigest-*.db" -mtime +7 -delete
```

### 7.2 Monitor Disk Space

```bash
df -h
```

SQLite database should stay small (<100MB for thousands of users).

### 7.3 Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### 7.4 Security

- **Never commit your bot token to Git!**
- Add to `.gitignore`:
  ```
  *.db
  bot.log
  cron_worker.log
  .env
  venv/
  __pycache__/
  ```

## Troubleshooting

### Bot doesn't respond

1. Check if bot is running:
   ```bash
   ps aux | grep bot.py
   ```

2. Check logs:
   ```bash
   tail -50 bot.log
   ```

3. Verify token:
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   ```

4. Test manually:
   ```bash
   python bot.py
   ```

### Cron job not running

1. Check crontab syntax:
   ```bash
   crontab -l
   ```

2. Test manually:
   ```bash
   python cron_worker.py
   ```

3. Check cron logs:
   ```bash
   tail -50 cron.log
   ```

4. Verify cron service:
   ```bash
   sudo systemctl status cron
   ```

### Database errors

1. Reinitialize database:
   ```bash
   mv bookdigest.db bookdigest.db.backup
   python database.py
   ```

2. Check permissions:
   ```bash
   ls -la bookdigest.db
   ```

### "Module not found" errors

1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Scaling Tips

### When you hit 100+ users:

1. **Move to VPS:**
   - DigitalOcean $5/month droplet
   - Linode $5/month Nanode
   - Vultr $3.50/month Cloud Compute

2. **Add Redis for caching:**
   - Cache book search results
   - Rate limiting
   - Session management

3. **Use PostgreSQL:**
   - Better performance than SQLite
   - Handles concurrent writes better

4. **Enable webhooks:**
   - More efficient than polling
   - Reduce server load
   - Faster responses

5. **Add monitoring:**
   - Uptime monitoring (UptimeRobot)
   - Error tracking (Sentry)
   - Analytics (Mixpanel)

## Next Steps

1. ✅ Bot is running
2. ✅ Cron job is scheduled
3. 🎯 Share bot in communities (see README.md)
4. 📊 Monitor stats weekly
5. 💰 Reach 10 paying users!

---

**Questions?** Check logs, read error messages carefully, or contact @yourusername on Telegram.

Good luck! 🚀
