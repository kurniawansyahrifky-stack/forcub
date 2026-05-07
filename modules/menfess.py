from telethon import events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError

from database import premium_db

from config import ADMIN_GROUP, POST_CHANNEL

from __main__ import bot, is_owner

import re
import time
import random
import string
import asyncio
import time
from datetime import datetime, timedelta

print("MENFESS MODULE LOADED")

cooldown = {}
menfess_mode = set()
reply_sessions = {}

async def cleanup_reply():

    while True:

        now = time.time()

        expired = []

        for code, data in reply_sessions.items():

            if now - data["time"] > 86400:
                expired.append(code)

        for code in expired:
            del reply_sessions[code]

        await asyncio.sleep(3600)

bot.loop.create_task(cleanup_reply())
# =========================
# CHANNEL
# =========================

CHANNEL_1 = "usernamechannel1"
CHANNEL_2 = None
CHANNEL_3 = None

# =========================
# FORCE SUB
# =========================

async def check_join(user_id):

    channels = []

    if CHANNEL_1:
        channels.append(CHANNEL_1.replace("@", ""))

    if CHANNEL_2:
        channels.append(CHANNEL_2.replace("@", ""))

    if CHANNEL_3:
        channels.append(CHANNEL_3.replace("@", ""))

    if not channels:
        return True

    for channel in channels:

        try:

            await bot(
                GetParticipantRequest(
                    channel=channel,
                    participant=user_id
                )
            )

        except UserNotParticipantError:

            return False

        except Exception as e:

            print(f"JOIN CHECK ERROR : {e}")
            return True

    return True

# =========================
# RANDOM CODE
# =========================

def generate_code():

    while True:

        code = "".join(

            random.choice(
                string.ascii_uppercase + string.digits
            )

            for _ in range(8)

        )

        if code not in reply_sessions:
            return code

# =========================
# GET PREMIUM
# =========================

async def get_premium(user_id):

    user = await premium_db.find_one(
        {
            "user_id": user_id
        }
    )

    if not user:
        return None

    expired = user.get("expired")

    if expired:

        exp_time = datetime.fromtimestamp(
            expired
        )

        if datetime.now() > exp_time:

            await premium_db.delete_one(
                {
                    "user_id": user_id
                }
            )

            return None

    return user

# =========================
# RESOLVE USER
# =========================

async def resolve_user(target):

    target = target.replace("@", "")

    try:

        user = await bot.get_entity(
            target
        )

        return user

    except Exception as e:

        print(f"RESOLVE ERROR : {e}")

        return None

# =========================
# FORMAT EXPIRED
# =========================

def format_expired(timestamp):

    dt = datetime.fromtimestamp(
        timestamp
    )

    return dt.strftime(
        "%d-%m-%Y %H:%M"
    )

# =========================
# CEK PREMIUM
# =========================

@bot.on(events.NewMessage(pattern=r"/cekprem"))
async def cekprem(event):

    user = await get_premium(
        event.sender_id
    )

    if not user:

        return await event.reply(
            "❌ kamu bukan premium"
        )

    expired = format_expired(
        user["expired"]
    )

    await event.reply(

        (
            "╭──〔 💎 PREMIUM INFO 〕──╮\n"
            f"┃ tier : {user['tier']}\n"
            f"┃ limit : {user['limit']}\n"
            f"┃ expired : {expired}\n"
            "╰────────────────────╯"
        )

    )

# =========================
# ADD PREMIUM
# =========================

async def add_premium(
    event,
    tier,
    limit
):

    if not is_owner(event.sender_id):
        return

    args = event.raw_text.split()

    if len(args) < 2:

        return await event.reply(
            f"contoh : /{tier} @username"
        )

    user = await resolve_user(
        args[1]
    )

    if not user:

        return await event.reply(
            "❌ user tidak ditemukan"
        )

    expired = datetime.now() + timedelta(days=30)

    await premium_db.update_one(

        {
            "user_id": user.id
        },

        {
            "$set": {

                "name": user.first_name,
                "username": user.username,

                "tier": tier,
                "limit": limit,

                "expired": expired.timestamp()

            }

        },

        upsert=True

    )

    await event.reply(

        (
            "╭──〔 💎 PREMIUM ADDED 〕──╮\n"
            f"┃ user : {user.first_name}\n"
            f"┃ tier : {tier}\n"
            f"┃ limit : {limit}\n"
            f"┃ expired : 30 hari\n"
            "╰──────────────────────╯"
        )

    )

@bot.on(events.NewMessage(pattern=r"/lite"))
async def lite_cmd(event):

    await add_premium(
        event,
        "lite",
        5
    )

@bot.on(events.NewMessage(pattern=r"/basic"))
async def basic_cmd(event):

    await add_premium(
        event,
        "basic",
        15
    )

@bot.on(events.NewMessage(pattern=r"/pro"))
async def pro_cmd(event):

    await add_premium(
        event,
        "pro",
        999999
    )

# =========================
# REMOVE PREMIUM
# =========================

@bot.on(events.NewMessage(pattern=r"/unprem"))
async def unprem(event):

    if not is_owner(event.sender_id):
        return

    args = event.raw_text.split()

    if len(args) < 2:

        return await event.reply(
            "contoh : /unprem @username"
        )

    user = await resolve_user(
        args[1]
    )

    if not user:

        return await event.reply(
            "❌ user tidak ditemukan"
        )

    await premium_db.delete_one(
        {
            "user_id": user.id
        }
    )

    await event.reply(
        f"✅ premium {user.first_name} dihapus"
    )

# =========================
# BUTTON MENFESS
# =========================

@bot.on(events.CallbackQuery(data=b"menfess"))
async def menfess_button(event):

    joined = await check_join(
        event.sender_id
    )

    if not joined:

        return await event.reply(

            "❌ wajib join channel dulu",

            buttons=[

                [
                    Button.url(
                        "✨ JOIN CHANNEL ✨",
                        f"https://t.me/{CHANNEL_1.replace('@', '')}"
                    )
                ]

            ]

        )

    menfess_mode.add(
        event.sender_id
    )

    await event.reply(
        "💌 silahkan kirim menfess sekarang"
    )

# =========================
# MENFESS
# =========================

@bot.on(events.NewMessage(incoming=True))
async def menfess_handler(event):

    try:

        if not event.is_private:
            return

        sender = await event.get_sender()

        if getattr(sender, "bot", False):
            return

        if event.sender_id not in menfess_mode:
            return

        text = event.raw_text or ""

        if text.startswith("/"):
            return

        menfess_mode.discard(
            event.sender_id
        )

        premium = await get_premium(
            sender.id
        )

        now = time.time()

        # =========================
        # COOLDOWN
        # =========================

        if premium:

            if sender.id in cooldown:

                delay = now - cooldown[sender.id]

                if delay < 5:

                    return await event.reply(
                        "❌ tunggu 5 detik"
                    )

            cooldown[sender.id] = now

        else:

            if sender.id in cooldown:

                delay = now - cooldown[sender.id]

                if delay < 15:

                    return await event.reply(
                        "❌ tunggu 15 detik"
                    )

            cooldown[sender.id] = now

        # =========================
        # GENERATE CODE
        # =========================

        reply_code = generate_code()

        reply_sessions[reply_code] = {
            "user_id": sender.id,
            "time": time.time()
        }

        final_caption = (
            f"{text}\n\n"
            f"↩️ reply code:\n"
            f"`/reply {reply_code}`"
        )

        # =========================
        # PREMIUM AUTO POST
        # =========================

        if premium:

            limit = premium.get("limit", 0)

            if limit <= 0:

                return await event.reply(
                    "❌ limit premium kamu habis"
                )

            try:

                if event.media:

                    await bot.send_file(
                        POST_CHANNEL,
                        file=event.media,
                        caption=final_caption
                    )

                else:

                    await bot.send_message(
                        POST_CHANNEL,
                        final_caption
                    )

                if premium["tier"] != "pro":

                    await premium_db.update_one(
                        {
                            "user_id": sender.id
                        },
                        {
                            "$inc": {
                                "limit": -1
                            }
                        }
                    )

                return await event.reply(
                    "✅ menfess berhasil dipost otomatis"
                )

            except Exception as e:

                print(f"POST ERROR : {e}")

                return await event.reply(
                    f"❌ gagal autopost\n\n{e}"
                )

        # =========================
        # FREE USER NEED APPROVE
        # =========================

        try:

            admin_caption = (
                f"{text}\n\n"
                f"CODE : {reply_code}"
            )

            if event.media:

                await bot.send_file(

                    ADMIN_GROUP,

                    file=event.media,

                    caption=admin_caption,

                    buttons=[

                        [
                            Button.inline(
                                "✅ APPROVE",
                                data=f"approve_{sender.id}_{reply_code}"
                            ),

                            Button.inline(
                                "❌ REJECT",
                                data=f"reject_{sender.id}"
                            )
                        ]

                    ]

                )

            else:

                await bot.send_message(

                    ADMIN_GROUP,

                    admin_caption,

                    buttons=[

                        [
                            Button.inline(
                                "✅ APPROVE",
                                data=f"approve_{sender.id}_{reply_code}"
                            ),

                            Button.inline(
                                "❌ REJECT",
                                data=f"reject_{sender.id}"
                            )
                        ]

                    ]

                )

            await event.reply(
                "✅ menfess dikirim ke admin"
            )

        except Exception as e:

            print(f"ADMIN ERROR : {e}")

            await event.reply(
                f"❌ gagal kirim admin\n\n{e}"
            )

    except Exception as e:

        print(f"MENFESS ERROR : {e}")

# =========================
# APPROVE
# =========================

@bot.on(
    events.CallbackQuery(
        data=re.compile(
            b"approve_(.*)_(.*)"
        )
    )
)
async def approve_handler(event):

    uid = int(
        event.data_match.group(1).decode()
    )

    code = event.data_match.group(2).decode()

    try:

        msg = await event.get_message()

        raw = msg.raw_text or ""

        menfess_text = raw.split(
            "\n\nCODE :",
            1
        )[0]

        final_caption = (
            f"{menfess_text}\n\n"
            f"↩️ reply code:\n"
            f"`/reply {code}`"
        )

        if msg.media:

            await bot.send_file(
                POST_CHANNEL,
                file=msg.media,
                caption=final_caption
            )

        else:

            await bot.send_message(
                POST_CHANNEL,
                final_caption
            )

        await event.edit(
            "✅ menfess approved"
        )

        await bot.send_message(
            uid,
            "✅ menfess kamu berhasil dipost"
        )

    except Exception as e:

        print(f"APPROVE ERROR : {e}")

# =========================
# REJECT
# =========================

@bot.on(
    events.CallbackQuery(
        data=re.compile(
            b"reject_(.*)"
        )
    )
)
async def reject_handler(event):

    uid = int(
        event.data_match.group(1).decode()
    )

    await event.edit(
        "❌ menfess rejected"
    )

    await bot.send_message(
        uid,
        "❌ menfess kamu ditolak admin"
    )
