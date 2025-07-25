import os
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Load environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))  # Must convert to int

# Wallet Addresses
STATE_MESSAGE = "Hey guys, please state the deal (value, platform, and coin)"
USDT = "0x331b412b3ed5367d7ffca7dcdbe7b697ac58d55a"
ETH = "0x331b412b3ed5367d7ffca7dcdbe7b697ac58d55a"
BTC = "bc1qmdzukhkxkyau4uyyvx75qxlhnw3f2ds945xcvy"
SOL = "Eia82vjxGs98EGAf3BvJnMvXybUDnx5nmaCeuUChkFWc"

user_private_groups = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is active!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = msg.from_user
    text = msg.text
    chat = msg.chat
    reply = msg.reply_to_message

    if text.startswith(".mm"):
        title = f"Deal - {user.first_name}"
        if user.id in user_private_groups:
            group_id = user_private_groups[user.id]
            await context.bot.send_message(chat_id=chat.id, text="Group already exists.")
            return
        new_group = await context.bot.create_chat(title, [user.id, OWNER_ID])
        invite_link = await context.bot.create_chat_invite_link(new_group.id)
        user_private_groups[user.id] = new_group.id
        await context.bot.send_message(chat_id=chat.id, text=f"🔗 Private group created: {invite_link.invite_link}")

    elif text.startswith(".state"):
        await msg.reply_text(STATE_MESSAGE)

    elif text.startswith(".usdt"):
        await msg.reply_text(f"💸 USDT Address:\n`{USDT}`", parse_mode="Markdown")
    elif text.startswith(".eth"):
        await msg.reply_text(f"💰 ETH Address:\n`{ETH}`", parse_mode="Markdown")
    elif text.startswith(".btc"):
        await msg.reply_text(f"₿ BTC Address:\n`{BTC}`", parse_mode="Markdown")
    elif text.startswith(".sol"):
        await msg.reply_text(f"🔷 SOL Address:\n`{SOL}`", parse_mode="Markdown")

    elif text.startswith(".close") and chat.type in ["group", "supergroup"]:
        member = await chat.get_member(user.id)
        if member.status in ["creator", "administrator"]:
            await context.bot.set_chat_permissions(chat_id=chat.id, permissions=ChatPermissions(can_send_messages=False))
            await msg.reply_text("🔒 Group has been closed for messaging.")
        else:
            await msg.reply_text("❌ You need to be an admin to use this command.")

    elif text.startswith(".remove") and reply and chat.type in ["group", "supergroup"]:
        member = await chat.get_member(user.id)
        if member.status in ["creator", "administrator"]:
            try:
                await context.bot.ban_chat_member(chat_id=chat.id, user_id=reply.from_user.id)
                await msg.reply_text(f"🚫 Removed {reply.from_user.full_name}")
            except:
                await msg.reply_text("⚠️ Couldn't remove user. Make sure I have admin rights.")
        else:
            await msg.reply_text("❌ Only admins can use this.")

    elif text.startswith(".del") and chat.type in ["group", "supergroup"]:
        member = await chat.get_member(user.id)
        if member.status in ["creator", "administrator"]:
            await msg.reply_text("👋 Leaving and deleting group...")
            await context.bot.leave_chat(chat_id=chat.id)
        else:
            await msg.reply_text("❌ Only admins can delete group.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
