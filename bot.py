from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# ==== تنظیمات ====
BOT_TOKEN = "6348746381:AAFMOy7ylGRUAlNuEFpxTMI_yZK3ydCA0fA"
ADMIN_ID = 1220781431

# ذخیره ارتباط پیام‌ها
message_map = {}

# ==== دستور start ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👋 سلام مدیر!\n\n"
            "📩 پیام‌های ناشناس کاربران برایت ارسال می‌شود.\n"
            "برای پاسخ، روی دکمه «پاسخ» زیر پیام بزن."
        )
        return
    
    await update.message.reply_text(
        "👋 سلام!\n\n"
        "🔒 می‌توانی پیامت را به‌صورت *ناشناس* برای مدیر ارسال کنی.\n\n"
        "✍️ فقط پیامت را بنویس و بفرست:",
        parse_mode="Markdown"
    )

# ==== دریافت پیام از کاربر ====
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    
    if user.id == ADMIN_ID:
        return
    
    username = f"@{user.username}" if user.username else "ندارد"
    full_name = user.full_name or "نامشخص"
    
    header = (
        f"📩 *پیام ناشناس جدید*\n\n"
        f"🆔 آیدی عددی: `{user.id}`\n"
        f"👤 نام: {full_name}\n"
        f"🔗 یوزرنیم: {username}\n"
        f"━━━━━━━━━━━━━━"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ پاسخ به این کاربر", callback_data=f"reply_{user.id}")]
    ])
    
    try:
        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=header,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        await msg.copy(chat_id=ADMIN_ID)
        message_map[sent.message_id] = user.id
        
        await msg.reply_text("✅ پیامت به‌صورت ناشناس برای مدیر ارسال شد.")
    
    except Exception as e:
        await msg.reply_text(f"❌ خطا در ارسال: {e}")

# ==== دکمه پاسخ ====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ شما دسترسی ندارید.", show_alert=True)
        return
    
    if query.data.startswith("reply_"):
        target_user_id = int(query.data.split("_")[1])
        context.user_data["reply_to"] = target_user_id
        await query.message.reply_text(
            f"✍️ حالا پاسخ خودت را برای کاربر `{target_user_id}` بنویس:",
            parse_mode="Markdown"
        )

# ==== ارسال پاسخ ادمین ====
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id != ADMIN_ID:
        return
    
    target = context.user_data.get("reply_to")
    if not target:
        return
    
    try:
        await update.message.copy(chat_id=target)
        await update.message.reply_text("✅ پاسخ برای کاربر ارسال شد.")
        context.user_data.pop("reply_to", None)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

# ==== اجرا ====
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(
        filters.User(ADMIN_ID) & ~filters.COMMAND,
        admin_reply
    ), group=0)
    app.add_handler(MessageHandler(
        ~filters.User(ADMIN_ID) & ~filters.COMMAND,
        handle_user_message
    ), group=1)
    
    print("🤖 ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
