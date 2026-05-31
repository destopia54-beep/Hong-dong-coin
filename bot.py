import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# --- FLASK WEB SERVER FOR RENDER/UPTIMEROBOT ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render provides a PORT environment variable dynamically
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# -----------------------------------------------

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

WALLET_INPUT = 1

# Your active Telegram Bot Token
BOT_TOKEN = "8778645855:AAGCv065Sa8MNabJURs3nsYdxM7oiFyetkc"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Welcome {user.first_name} to the **CryptoProject Airdrop**!\n\n"
        "Complete the mandatory tasks below to earn **100 $PROJECT** tokens (~$10):\n\n"
        "1️⃣ Join our Telegram Channel\n"
        "2️⃣ Follow our Official Twitter (X)\n"
        "3️⃣ Submit your BEP-20 / ERC-20 wallet address"
    )
    keyboard = [
        [
            InlineKeyboardButton("📢 Join Channel", url="https://t.me/YourChannelUsername"),
            InlineKeyboardButton("🐦 Follow Twitter", url="https://twitter.com/YourTwitterHandle")
        ],
        [InlineKeyboardButton("✅ Check Membership & Submit Wallet", callback_data="proceed_airdrop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "proceed_airdrop":
        await query.edit_message_text(text="📥 **Step 3: Submit Wallet**\n\nPlease type and send your **BEP-20** or **ERC-20** wallet address.")
        return WALLET_INPUT

async def wallet_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet_address = update.message.text.strip()
    if wallet_address.startswith("0x") and len(wallet_address) == 42:
        success_text = f"🎉 **Airdrop Registration Complete!**\n\nYour submitted wallet:\n`{wallet_address}`"
        await update.message.reply_text(success_text, parse_mode="Markdown")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ **Invalid Address.** Please make sure it starts with `0x`.")
        return WALLET_INPUT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Airdrop registration cancelled.")
    return ConversationHandler.END

def main():
    if not BOT_TOKEN:
        print("ERROR: Please provide a valid BOT_TOKEN!")
        return

    # Start the web server right before launching the bot
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_click, pattern="^proceed_airdrop$")],
        states={WALLET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_received)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
