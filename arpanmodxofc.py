# arpanmodxofc.py
import base64
import json
import time
import os
from urllib.parse import quote
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

TOKEN = "8319070992:AAGeV1PKn5k3squMO50SLifcOtPZSFtMyvY"
SITE_URL = "https://arpanmodxofc.netlify.app/"

HISTORY_FILE = "history.json"
CONFIG_FILE  = "config.json"

# ── LOAD / SAVE CONFIG ─────────────────────────────────
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "setup_url": "https://t.me/c/3262848619/131",
        "ffmax_url": "https://t.me/c/3262848619/129",
        "ff_url":    "https://t.me/c/3262848619/128",
    }

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ── LOAD / SAVE HISTORY ────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# ── INIT ───────────────────────────────────────────────
config  = load_config()
history = load_history()

ASK_NAME, ASK_URL, ASK_KEY = range(3)
CHANGE_SETUP, CHANGE_FFMAX, CHANGE_FF = range(3, 6)

# ── MAIN KEYBOARD ──────────────────────────────────────
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("✅ Create Post")],
        [KeyboardButton("🔗 Change FF Link"), KeyboardButton("🛡️ Change FF MAX Link")],
        [KeyboardButton("🎞️ Change Setup Link")],
        [KeyboardButton("📋 Show Current Links")],
        [KeyboardButton("🕓 Link History")],
    ],
    resize_keyboard=True
)

# ── START ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *ARPAN MODX OFC Link Bot*\n\n"
        "Use buttons below 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )

# ── SHOW CURRENT LINKS ─────────────────────────────────
async def show_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Current Saved Links:*\n\n"
        f"🛡️ FF: {config['ff_url']}\n\n"
        f"🛡️ FF MAX: {config['ffmax_url']}\n\n"
        f"🎞️ Setup: {config['setup_url']}",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=main_keyboard
    )

# ── SHOW HISTORY ───────────────────────────────────────
async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not history:
        await update.message.reply_text(
            "📭 *No history yet!*\n\nCreate your first post using ✅ Create Post",
            parse_mode="Markdown",
            reply_markup=main_keyboard
        )
        return

    await update.message.reply_text(
        f"🕓 *LINK HISTORY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Total posts created: *{len(history)}*",
        parse_mode="Markdown"
    )

    for i, item in enumerate(reversed(history), 1):
        msg = (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"*#{i} — {item['name']}*\n\n"
            f"📅 Date: {item['date']}\n"
            f"🔐 Key: `{item['key']}`\n\n"
            f"🛡️ FF Link:\n{item['ff_page']}\n\n"
            f"🛡️ FF MAX Link:\n{item['ffmax_page']}"
        )
        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    await update.message.reply_text(
        "✅ *End of history*",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )

# ── CREATE ─────────────────────────────────────────────
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📁 *STEP 1/3 — File Name*\n\n"
        "Send the mod file name\n\n"
        "✏️ *Example:*\n"
        "`PUBG MOBILE MOD MENU v3.5`\n"
        "`Free Fire MAX Hack v1.9.9`\n"
        "`COD Mobile MOD v2.0`",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text(
        "🔗 *STEP 2/3 — Download Link*\n\n"
        "Send the download URL for this file\n\n"
        "✏️ *Example:*\n"
        "`https://mediafire.com/file/xyz/file.apk`\n"
        "`https://drive.google.com/file/abc123`",
        parse_mode="Markdown"
    )
    return ASK_URL

async def ask_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['file_url'] = update.message.text.strip()
    await update.message.reply_text(
        "🔐 *STEP 3/3 — KEY*\n\n"
        "Send the key for this mod\n\n"
        "✏️ *Example:*\n"
        "`ARPAN-2025-FREE`\n"
        "`MODX-VIP-999`\n"
        "`AM-UNLOCK-777`",
        parse_mode="Markdown"
    )
    return ASK_KEY

async def ask_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['key'] = update.message.text.strip()

    name      = context.user_data['name']
    key       = context.user_data['key']
    file_url  = context.user_data['file_url']
    setup_url = config['setup_url']
    ffmax_url = config['ffmax_url']

    # ── This file's download page — URL hidden inside encoding ──
    obj1 = {"n": name, "u": file_url, "t": int(time.time() * 1000)}
    encoded1 = base64.b64encode(json.dumps(obj1, separators=(',', ':')).encode()).decode()
    ff_page = f"{SITE_URL}?data={quote(encoded1)}"

    # ── FF MAX page — from saved config ──
    obj2 = {"n": name + " FF MAX", "u": ffmax_url, "t": int(time.time() * 1000)}
    encoded2 = base64.b64encode(json.dumps(obj2, separators=(',', ':')).encode()).decode()
    ffmax_page = f"{SITE_URL}?data={quote(encoded2)}"

    # ── Save to permanent history ──
    date_str = time.strftime("%d/%m/%Y %I:%M %p")
    history.append({
        "name":       name,
        "key":        key,
        "ff_page":    ff_page,
        "ffmax_page": ffmax_page,
        "date":       date_str
    })
    save_history()

    caption = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"╭━━━━ 〔💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗥𝗘𝗟𝗘𝗔𝗦𝗘  ━━━━╮\n"
        f"✨ P2077KNG MOD MENU :- 🔥 DOWNLOAD 🔥\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━╯\n"
        f"╭━━━━ 〔 ⚡ 𝗙𝗙 𝗠𝗔𝗫 𝗩𝗘𝗥𝗦𝗜𝗢𝗡 〕 ━━━━╮\n"
        f"  🚀 GET IT :- 🔥 DOWNLOAD 🔥\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━╯\n"
        f"╭━━━━━  〔 🔐 𝗦𝗘𝗖𝗥𝗘𝗧 𝗞𝗘𝗬 〕 ━━━━━╮\n"
        f"  🔑 ABC123-XYZ789\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━╯\n"
        f"╭━━━━━ 〔 🎬 𝗤𝗨𝗜𝗖𝗞 𝗦𝗘𝗧𝗨𝗣 ]  ━━━━━╮\n"
        f"   🎞️ 👉 CLICK HERE\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━╯\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ STATUS : WORKING ✅\n"
        f"⚡ UPDATED : LATEST VERSION\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"> 🚫 ONLY FOR ROOT USERS\n"
        f" ⚠️ ⌈ OFFICIAL DISCLAIMER ⌋ ⚠️\n"
        f"> This post doesn't promote any illegal activities\n"
        f"> 🔗 https://telegra.ph/Disclaimer-11-25-17\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

    # ── Message 1 — confirmation ──
    await update.message.reply_text(
        f"✅ *Done! Saved to history #{len(history)}*",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )

    # ── Message 2 — caption alone, easy to copy ──
    await update.message.reply_text(
        caption,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

    return ConversationHandler.END

# ── CHANGE SETUP ───────────────────────────────────────
async def setsetup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎞️ *Current Setup link:*\n{config['setup_url']}\n\n"
        "Send new Setup URL\n\n"
        "✏️ *Example:*\n"
        "`https://youtube.com/watch?v=abc123`",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove()
    )
    return CHANGE_SETUP

async def save_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config['setup_url'] = update.message.text.strip()
    save_config()
    await update.message.reply_text(
        f"✅ *Setup link updated!*\n\n🎞️ {config['setup_url']}",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=main_keyboard
    )
    return ConversationHandler.END

# ── CHANGE FF MAX ──────────────────────────────────────
async def setffmax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🛡️ *Current FF MAX link:*\n{config['ffmax_url']}\n\n"
        "Send new FF MAX download URL\n\n"
        "✏️ *Example:*\n"
        "`https://mediafire.com/file/xyz/ffmax.apk`",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove()
    )
    return CHANGE_FFMAX

async def save_ffmax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config['ffmax_url'] = update.message.text.strip()
    save_config()
    await update.message.reply_text(
        f"✅ *FF MAX link updated!*\n\n🛡️ {config['ffmax_url']}",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=main_keyboard
    )
    return ConversationHandler.END

# ── CHANGE FF ──────────────────────────────────────────
async def setff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🛡️ *Current FF link:*\n{config['ff_url']}\n\n"
        "Send new FF download URL\n\n"
        "✏️ *Example:*\n"
        "`https://mediafire.com/file/xyz/ff.apk`",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove()
    )
    return CHANGE_FF

async def save_ff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config['ff_url'] = update.message.text.strip()
    save_config()
    await update.message.reply_text(
        f"✅ *FF link updated!*\n\n🛡️ {config['ff_url']}",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=main_keyboard
    )
    return ConversationHandler.END

# ── CANCEL ─────────────────────────────────────────────
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_keyboard)
    return ConversationHandler.END

# ── MAIN ───────────────────────────────────────────────
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    create_conv = ConversationHandler(
        entry_points=[
            CommandHandler("create", create),
            MessageHandler(filters.Regex("^✅ Create Post$"), create)
        ],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_URL:  [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_url)],
            ASK_KEY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_key)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    setup_conv = ConversationHandler(
        entry_points=[
            CommandHandler("setsetup", setsetup),
            MessageHandler(filters.Regex("^🎞️ Change Setup Link$"), setsetup)
        ],
        states={
            CHANGE_SETUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_setup)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    ffmax_conv = ConversationHandler(
        entry_points=[
            CommandHandler("setffmax", setffmax),
            MessageHandler(filters.Regex("^🛡️ Change FF MAX Link$"), setffmax)
        ],
        states={
            CHANGE_FFMAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_ffmax)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    ff_conv = ConversationHandler(
        entry_points=[
            CommandHandler("setff", setff),
            MessageHandler(filters.Regex("^🔗 Change FF Link$"), setff)
        ],
        states={
            CHANGE_FF: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_ff)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(create_conv)
    app.add_handler(setup_conv)
    app.add_handler(ffmax_conv)
    app.add_handler(ff_conv)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📋 Show Current Links$"), show_links))
    app.add_handler(MessageHandler(filters.Regex("^🕓 Link History$"), show_history))

    print("✅ Bot is running...")
    app.run_polling()
