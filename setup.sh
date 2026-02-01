#!/bin/bash
# Quick setup script for BookDigest Bot

echo "======================================"
echo "BookDigest Bot - Quick Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install -r requirements.txt

echo "[4/5] Initializing database..."
python database.py

echo "[5/5] Setup complete!"
echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "1. Get bot token from @BotFather on Telegram:"
echo "   /newbot"
echo ""
echo "2. Set your bot token:"
echo "   export TELEGRAM_BOT_TOKEN='your_token_here'"
echo ""
echo "3. Start the bot:"
echo "   python bot.py"
echo ""
echo "4. Test on Telegram by messaging your bot!"
echo ""
echo "For full deployment guide, see DEPLOYMENT.md"
echo ""
