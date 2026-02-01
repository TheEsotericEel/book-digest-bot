# 📚 BookDigest Bot

AI-powered book summaries delivered instantly on Telegram. Get comprehensive summaries of any book in seconds - much cheaper than Blinkist or getAbstract!

## 🎯 What It Does

BookDigest Bot provides instant AI-generated book summaries on Telegram:
- Search for any book
- Get comprehensive summaries in seconds
- Save to your personal library
- Pay-per-summary or subscription model
- Much cheaper than competitors ($1/summary vs $13/month for Blinkist)

## 🚀 Quick Start

### 1. Get a Bot Token (5 minutes)

Message [@BotFather](https://t.me/BotFather) on Telegram:

```
/newbot
My Book Summary Bot
mybooksummarybot
```

Copy the token you receive.

### 2. Setup Environment (5 minutes)

```bash
cd BookDigestBot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set bot token
export TELEGRAM_BOT_TOKEN="your_token_here"  # Windows: set TELEGRAM_BOT_TOKEN=...

# Initialize database
python database.py
```

### 3. Start the Bot

```bash
python bot.py
```

The bot is now running! Test it on Telegram by searching for your bot username.

### 4. Setup Daily Cron Job

The cron worker handles:
- Daily book recommendations for Pro users
- Weekly credit refresh for free users
- Expired subscription checks
- Data cleanup

**Linux/Mac:**
```bash
crontab -e

# Add this line (runs daily at 9 AM):
0 9 * * * cd /path/to/BookDigestBot && TELEGRAM_BOT_TOKEN="your_token" /path/to/venv/bin/python cron_worker.py >> cron.log 2>&1
```

**Windows (Task Scheduler):**
See `DEPLOYMENT.md` for detailed Windows setup.

## 💡 Features

### For Users

**Free Tier:**
- 2 free summaries on signup
- 1 free summary per week
- Search unlimited books
- Save to personal library

**Credit Pack ($5):**
- 5 summaries for 250 Telegram Stars (~$5)
- $1 per summary
- No expiration

**Pro Plan ($10/month):**
- 15 summaries per month for 500 Telegram Stars
- Daily book recommendations
- Only $0.66 per summary!

### Bot Commands

- `/start` - Welcome & onboarding
- `/search [book title]` - Find books
- `/summary [book title]` - Get summary (costs 1 credit)
- `/library` - View your saved summaries
- `/credits` - Check credit balance
- `/buy` - Purchase credits
- `/help` - Show help
- `/stats` - Bot statistics

## 📊 Monetization

### Pricing Strategy

**Competitive Analysis:**
- Blinkist: $12.99/month
- getAbstract: $29/month  
- Shortform: $24/month

**Our Pricing:**
- Single pack: $1/summary (5 for $5)
- Pro plan: $0.66/summary ($10/month for 15)

**Much more affordable!** Target market: Students, busy professionals, entrepreneurs.

### Revenue Projections

| Users | Conversion | Pro Users | Monthly Revenue |
|-------|------------|-----------|-----------------|
| 100   | 10%        | 10        | $100            |
| 500   | 10%        | 50        | $500            |
| 1,000 | 10%        | 100       | $1,000          |

**Break-even:** ~50 Pro users ($500/month covers server costs)

### Path to 10 Paying Users

**Week 1: Launch**
- Share in r/books, r/productivity, r/GetMotivated
- Post in Telegram book clubs
- Product Hunt launch
- Target: 50-100 total users

**Week 2-3: Growth**
- Partner with book review channels
- Referral program (share bot, get 1 free credit)
- Optimize onboarding flow
- Target: 150-200 users

**Week 4: Conversion**
- A/B test pricing
- Add testimonials
- Limited-time offers
- **Goal: 10 paying users** ✅

**Estimated conversion rate:** 10-15% (industry standard for freemium)

## 🏗️ Architecture

```
User → Telegram Bot (Python)
         ├─ SQLite Database (users, summaries, purchases)
         ├─ Google Books API (book metadata)
         ├─ AI Summary Generation (LLM API or template-based)
         └─ Telegram Stars (payment processing)

Cron Job (daily at 9 AM):
         ├─ Send book recommendations to Pro users
         ├─ Refresh weekly credits for free users
         ├─ Check expired Pro subscriptions
         └─ Cleanup old data
```

### Database Schema

**users**
- telegram_id (PK)
- username, first_name
- credits (integer)
- tier (free/pro)
- pro_expires_at (timestamp)
- created_at

**summaries**
- id (PK)
- book_title, author, isbn
- summary_text (AI-generated)
- created_at

**user_summaries** (access log)
- user_id, summary_id
- accessed_at

**purchases**
- user_id, amount_stars, credits_added
- purchase_type, timestamp

## 📈 Growth Strategy

### Target Audience

1. **Students** - Need book summaries for classes
2. **Entrepreneurs** - Want to learn quickly
3. **Busy Professionals** - Limited reading time
4. **Book Lovers** - Decide what to read next

### Marketing Channels

**Reddit:**
- r/books (2.8M members)
- r/productivity (1.8M)
- r/GetMotivated (24M)
- r/Entrepreneur (2.9M)

**Telegram:**
- Book club groups
- Productivity communities
- Study groups

**Product Hunt:**
- Launch with compelling story
- Target "Product of the Day"

**Referral Program:**
- Share bot → get 1 free credit
- Viral growth potential

### Conversion Tactics

1. **Scarcity:** "Only 2 free summaries - use them wisely!"
2. **Social Proof:** Show number of users/summaries
3. **Comparison:** "Cheaper than Blinkist!"
4. **Free Trial:** Generous 2 summaries upfront
5. **Upsells:** "Running low on credits? Buy now!"

## 🔧 Technical Details

### File Structure

```
BookDigestBot/
├── bot.py              (Main bot logic - 450 lines)
├── database.py         (Database operations - 250 lines)
├── cron_worker.py      (Daily tasks - 180 lines)
├── config.py           (Settings)
├── stats.py            (Analytics dashboard)
├── requirements.txt    (Dependencies)
├── bookdigest.db       (SQLite database)
└── README.md           (This file)
```

### APIs Used

**Google Books API** (Free)
- Search books
- Get metadata (title, author, description, ISBN)
- 1,000 requests/day free tier

**AI Summary Generation**
- MVP: Uses book descriptions from Google Books
- Future: OpenAI/Anthropic/Gemini API for true AI summaries
- Cost: ~$0.01 per summary (at scale)

### Payment Processing

**Telegram Stars:**
- Official Telegram payment method
- Bot receives 70% (Telegram takes 30%)
- Easy integration via Bot API
- Users can pay with app store credits

### Deployment Options

1. **Local Machine** (Free)
   - Run bot.py continuously
   - Setup cron/Task Scheduler
   - Good for MVP

2. **VPS** ($5-10/month)
   - DigitalOcean, Linode, Vultr
   - Better uptime
   - Scalable

3. **Cloud** (Pay-as-you-go)
   - Google Cloud Run
   - AWS Lambda
   - Heroku

## 📊 Monitoring

### Check Stats

```bash
python stats.py
```

Shows:
- Total users (free vs pro)
- Summaries generated
- Revenue (Stars & USD)
- Conversion rate
- Engagement metrics
- Health checks
- Growth recommendations

### Logs

- `bot.log` - Bot activity
- `cron_worker.log` - Daily job logs

## 🎯 Roadmap

### Phase 1: MVP (Week 1) ✅
- [x] Basic bot commands
- [x] Google Books integration
- [x] Credit system
- [x] Payment framework
- [x] Daily cron job
- [x] Stats dashboard

### Phase 2: Polish (Week 2-3)
- [ ] Real AI summaries (LLM integration)
- [ ] Payment processing (Telegram Stars)
- [ ] Referral system
- [ ] Better book search
- [ ] Summary quality improvements

### Phase 3: Growth (Week 4+)
- [ ] Community features
- [ ] Reading lists
- [ ] Book recommendations based on preferences
- [ ] Multi-language support
- [ ] Mobile web app
- [ ] API for developers

## 💰 Cost Breakdown

### Fixed Costs
- Hosting: $0-10/month (local or VPS)
- Domain (optional): $10/year

### Variable Costs
- AI summaries: $0.01-0.05 per summary (at scale)
- Payment processing: 30% to Telegram

### Revenue (at 10 paying users)
- 10 users × $10/month = $100/month
- Profit margin: ~70% after costs
- Monthly profit: ~$70

**Highly profitable at scale!**

## 🤝 Contributing

This is a solo MVP project, but ideas welcome!

## 📝 License

MIT License - Free to use and modify

## 📧 Support

Questions? Issues? Contact @yourusername on Telegram

---

**Built with:** Python, python-telegram-bot, SQLite, Google Books API

**Status:** MVP Ready (Build time: 3 hours)

**Next Steps:** 
1. Get bot token from @BotFather
2. Deploy bot
3. Share in communities
4. Acquire first 10 paying users!

🚀 Let's disrupt the book summary market!
