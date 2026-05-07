from telethon import events
from __main__ import bot
import os

OWNER_ID = 8209644174  # ganti id telegram lu

# ========================
# UPLOAD START PHOTO
# ========================

@bot.on(events.NewMessage(pattern="/upstart"))
async def upload_start(event):

    if event.sender_id != OWNER_ID:
        return

    if not event.reply_to_msg_id:
        return await event.reply("reply foto start.")

    msg = await event.get_reply_message()

    if not msg.photo:
        return await event.reply("harus reply foto.")

    os.makedirs("photos", exist_ok=True)

    path = await msg.download_media(
        file="photos/start.jpg"
    )

    await event.reply(
        f"✅ start photo berhasil disimpan\n{path}"
    )

# ========================
# UPLOAD QR PHOTO
# ========================

@bot.on(events.NewMessage(pattern="/upqr"))
async def upload_qr(event):

    if event.sender_id != OWNER_ID:
        return

    if not event.reply_to_msg_id:
        return await event.reply("reply foto qr.")

    msg = await event.get_reply_message()

    if not msg.photo:
        return await event.reply("harus reply foto.")
    
    os.makedirs("photos", exist_ok=True)

    path = await msg.download_media(
        file="photos/qr.jpg"
    )

    await event.reply(
        f"✅ qr photo berhasil disimpan\n{path}"
    )
