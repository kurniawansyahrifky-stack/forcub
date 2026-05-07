import asyncio
import re
import time

from datetime import datetime, timedelta

from telethon import events, Button
from telethon.utils import get_display_name

from database import premium_db
from config import ADMIN_GROUP, POST_CHANNEL
from __main__ import bot, is_owner

print("MENFESS MODULE LOADED")

# =========================
# SYSTEM
# =========================

cooldown = {}

# LIMIT MEDIA UPLOAD
media_semaphore = asyncio.Semaphore(3)

# LIMIT CALLBACK
callback_semaphore = asyncio.Semaphore(5)

# CLEANUP MEMORY
async def cleanup_cooldown():

    while True:

        try:

            now = time.time()

            delete = []

            for uid, tm in cooldown.items():

                if now - tm > 120:
                    delete.append(uid)

            for uid in delete:
                cooldown.pop(uid, None)

        except Exception as e:

            print(
                f"CLEANUP ERROR : {e}"
            )

        await asyncio.sleep(60)


bot.loop.create_task(
    cleanup_cooldown()
)

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

        print(
            f"RESOLVE ERROR : {e}"
        )

        return None


# =========================
# FORMAT TIME
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
            "┃ duration : 30 hari\n"
            "╰──────────────────────╯"
        )

    )


@bot.on(events.NewMessage(pattern=r"/lite"))
async def lite_cmd(event):

    await add_premium(
        event,
        "lite",
        10
    )


@bot.on(events.NewMessage(pattern=r"/basic"))
async def basic_cmd(event):

    await add_premium(
        event,
        "basic",
        30
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
# MENFESS
# =========================

@bot.on(events.NewMessage(incoming=True))
async def menfess_handler(event):

    try:

        # PRIVATE ONLY
        if not event.is_private:
            return

        text = event.raw_text or ""

        # SKIP COMMAND
        if text.startswith("/"):
            return

        sender = await event.get_sender()

        premium = await get_premium(
            sender.id
        )

        # =========================
        # COOLDOWN
        # =========================

        now = time.time()

        # PREMIUM
        if premium:

            cd = 3

        # FREE USER
        else:

            cd = 20

        last = cooldown.get(sender.id)

        if last:

            if now - last < cd:
                return

        cooldown[sender.id] = now

        mention = (
            f"[{get_display_name(sender)}]"
            f"(tg://user?id={sender.id})"
        )

        # =========================
        # PREMIUM AUTO POST
        # =========================

        if premium:

            limit = premium["limit"]

            if limit <= 0:

                return await event.reply(
                    "❌ limit premium kamu habis"
                )

            try:

                # MEDIA
                if event.media:

                    async with media_semaphore:

                        await bot.send_file(

                            POST_CHANNEL,

                            event.media,

                            caption=text if text else None,

                            supports_streaming=True

                        )

                # TEXT
                else:

                    await bot.send_message(
                        POST_CHANNEL,
                        text
                    )

                # LIMIT
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

                print(
                    f"POST ERROR : {e}"
                )

                return await event.reply(
                    "❌ gagal mengirim menfess"
                )

        # =========================
        # FREE USER APPROVE
        # =========================

        caption = (

            "╭──〔 📥 MENFESS MASUK 〕──╮\n"
            f"FROM : {mention}\n"
            f"USER ID : {sender.id}\n"
            "╰────────────────────╯\n\n"
            f"{text}"

        )

        try:

            # MEDIA
            if event.media:

                async with media_semaphore:

                    await bot.send_file(

                        ADMIN_GROUP,

                        event.media,

                        caption=caption,

                        supports_streaming=True,

                        buttons=[

                            [
                                Button.inline(
                                    "✅ APPROVE",
                                    data=f"approve_{sender.id}"
                                ),

                                Button.inline(
                                    "❌ REJECT",
                                    data=f"reject_{sender.id}"
                                )
                            ]

                        ]

                    )

            # TEXT
            else:

                await bot.send_message(

                    ADMIN_GROUP,

                    caption,

                    buttons=[

                        [
                            Button.inline(
                                "✅ APPROVE",
                                data=f"approve_{sender.id}"
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

            print(
                f"ADMIN ERROR : {e}"
            )

    except Exception as e:

        print(
            f"MESSAGE ERROR : {e}"
        )


# =========================
# APPROVE
# =========================

@bot.on(

    events.CallbackQuery(

        data=re.compile(
            b"approve_(.*)"
        )

    )

)
async def approve_handler(event):

    async with callback_semaphore:

        uid = int(
            event.data_match.group(1).decode()
        )

        try:

            msg = await event.get_message()

            # MEDIA
            if msg.media:

                async with media_semaphore:

                    await bot.send_file(

                        POST_CHANNEL,

                        msg.media,

                        caption=msg.raw_text,

                        supports_streaming=True

                    )

            # TEXT
            else:

                text = msg.raw_text

                lines = text.split("\n\n")

                menfess_text = lines[-1]

                await bot.send_message(
                    POST_CHANNEL,
                    menfess_text
                )

            await event.edit(
                "✅ menfess approved"
            )

            await bot.send_message(
                uid,
                "✅ menfess kamu berhasil dipost"
            )

        except Exception as e:

            print(
                f"APPROVE ERROR : {e}"
            )


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

    async with callback_semaphore:

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
