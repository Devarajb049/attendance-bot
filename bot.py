import os
import json
import logging
import asyncio
from pathlib import Path
from telegram import Update, ReplyKeyboardRemove, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from scraper import get_attendance

# User data storage
USER_DATA_FILE = Path("users.json")

def load_user_data():
    if USER_DATA_FILE.exists():
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for ConversationHandler
USERNAME, PASSWORD = range(2)

# Token string provided by user
TOKEN = "8452982059:AAFufqqEzpJjZrbsdkR_kqgRrZc8VX837SM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! 🎓"
        "\n\nI can help you check your MITS IMS attendance."
        "\nUse /attendance to get your report.",
    )

async def attendance_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the attendance check process. Checks for saved credentials first."""
    user_id = str(update.effective_user.id)
    all_users = load_user_data()

    if user_id in all_users:
        user_info = all_users[user_id]
        username = user_info["username"]
        password = user_info["password"]
        
        await update.message.reply_text(f"🔄 Using saved credentials for ID: {username}...")
        return await fetch_and_report(update, context, username, password)

    await update.message.reply_text(
        "Please enter your IMS Student ID (Register No):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the username and asks for the password."""
    context.user_data["username"] = update.message.text
    await update.message.reply_text("Great! Now enter your IMS Password:")
    return PASSWORD

async def get_password_and_fetch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the password and fetches attendance."""
    password = update.message.text
    username = context.user_data.get("username")
    
    # Save for next time
    user_id = str(update.effective_user.id)
    all_users = load_user_data()
    all_users[user_id] = {"username": username, "password": password}
    save_user_data(all_users)

    # Delete the password message for security
    try:
        await update.message.delete()
    except:
        pass

    return await fetch_and_report(update, context, username, password)

async def fetch_and_report(update: Update, context: ContextTypes.DEFAULT_TYPE, username, password) -> int:
    """Helper to fetch and display report."""
    msg = await update.message.reply_text("🔍 Fetching your attendance report... Please wait.")

    # Call the scraper
    result = await get_attendance(username, password)

    if isinstance(result, dict) and "error" in result:
        error_msg = result['error']
        await msg.edit_text(f"❌ Error: {error_msg}")
        # If login failed, might want to clear saved data
        if "login" in error_msg.lower() or "credentials" in error_msg.lower():
            user_id = str(update.effective_user.id)
            all_users = load_user_data()
            if user_id in all_users:
                del all_users[user_id]
                save_user_data(all_users)
                await update.message.reply_text("Stored credentials cleared due to login failure. Please try /attendance again.")
    else:
        # Format the attendance report
        report = "📊 *Attendance Report*\n\n"
        total_attended = 0
        total_classes = 0
        
        for item in result:
            subj = item["subject"]
            att = item["attended"]
            tot = item["total"]
            perc = item["percentage"]
            
            report += f"*{subj}*: {att}/{tot} ({perc}%)\n"
            
            try:
                total_attended += int(att)
                total_classes += int(tot)
            except:
                pass

        if total_classes > 0:
            overall_perc = round((total_attended / total_classes) * 100, 2)
            report += f"\n🎯 *Total Attendance: {overall_perc}%*"
        else:
            report += "\n🎯 *Total Attendance: N/A*"

        await msg.edit_text(report, parse_mode="Markdown")

    return ConversationHandler.END

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears saved credentials."""
    user_id = str(update.effective_user.id)
    all_users = load_user_data()
    if user_id in all_users:
        del all_users[user_id]
        save_user_data(all_users)
        await update.message.reply_text("✅ Your saved credentials have been cleared. Use /attendance to set them again.")
    else:
        await update.message.reply_text("You don't have any saved credentials.")

async def show_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows saved credentials to the user."""
    user_id = str(update.effective_user.id)
    all_users = load_user_data()
    
    if user_id in all_users:
        user_info = all_users[user_id]
        username = user_info["username"]
        password = user_info["password"]
        await update.message.reply_text(
            f"🔐 *Your Saved Credentials*\n\n"
            f"👤 *Student ID:* `{username}`\n"
            f"🔑 *Password:* `{password}`\n\n"
            "To edit these, use /reset and then start /attendance again.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("No credentials saved yet. Use /attendance to set them up.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Action canceled.")
    return ConversationHandler.END

async def post_init(application: Application) -> None:
    """Set bot commands in the menu."""
    commands = [
        BotCommand("start", "Welcome message"),
        BotCommand("attendance", "Check attendance"),
        BotCommand("credentials", "See/Edit saved login info"),
        BotCommand("reset", "Clear saved credentials"),
        BotCommand("cancel", "Cancel current action"),
    ]
    await application.bot.set_my_commands(commands)

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        print("Error: TOKEN not set.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # Add conversation handler for attendance
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("attendance", attendance_start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password_and_fetch)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("credentials", show_credentials))
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
