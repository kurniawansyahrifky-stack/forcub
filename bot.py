import logging
import re
import asyncio
import os
import sys
import gc

from datetime import datetime

from decouple import config

from telethon import (
    TelegramClient,
    events,
    Button
)

from telethon.errors.rpcerrorlist import (
    UserNotParticipantError
)

from telethon.tl.functions.channels import (
    GetParticipantRequest
)

from telethon.utils import (
    get_display_name
)

from reset_daily import reset_limits


# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

log = logging.getLogger("MENFESS")

log.info("STARTING BOT...")


# =========================
# CONFIG
# =========================

API_ID = config(
    "API_ID",
    cast=int
)

API_HASH = config(
    "API_HASH"
)

BOT_TOKEN = config(
    "BOT_TOKEN"
)

CHANNEL = config(
    "CHANNEL"
)

OWNER_IDS = list(
    map(
        int,
        config("OWNER_IDS").split(",")
    )
)

ON_JOIN = config(
    "ON_JOIN",
    cast=bool,
    default=True
)

ON_NEW_MSG = config(
    "ON_NEW_MSG",
    cast=bool,
    default=True
)


# =========================
# CLIENT
# =========================

bot = TelegramClient(
    "menfessbot",
    API_ID,
    API_HASH
).start(
    bot_token=BOT_TOKEN
)

channel = CHANNEL.replace(
    "@",
    ""
)

bot_self = bot.loop.run_until_complete(
    bot.get_me()
)


# =========================
# OWNER CHECK
# =========================

def is_owner(user_id):

    return user_id in OWNER_IDS


# =========================
# JOIN CHECK
# =========================

async def get_user_join(user_id):

    try:

        await bot(

            GetParticipantRequest(

                channel=channel,

                participant=user_id

            )

        )

        return True

    except UserNotParticipantError:

        return False

    except Exception as e:

        log.error(
            f"JOIN CHECK ERROR: {e}"
        )

        return False


# =========================
# NOT JOIN TEXT
# =========================

WELCOME_NOT_JOINED = (

    "╭──〔 🚫 ACCESS DENIED 〕──╮\n"
    "┃\n"
    "┃ kamu belum join\n"
    "┃ channel wajib bot\n"
    "┃\n"
    "┃ join dulu supaya bisa\n"
    "┃ mengirim pesan 💌\n"
    "┃\n"
    "╰────────────────╯"

)


# =========================
# MEMBER JOIN
# =========================

@bot.on(events.ChatAction)
async def welcome_handler(event):

    if not ON_JOIN:
        return

    if not event.is_group:
        return

    if event.action_message:
        return

    if event.user_joined or event.user_added:

        user = await event.get_user()

        joined = await get_user_join(
            user.id
        )

        # SUDAH JOIN = DIEM
        if joined:
            return

        try:

            await bot.edit_permissions(
                event.chat.id,
                user.id,
                send_messages=False
            )

        except Exception as e:

            log.error(
                f"MUTE ERROR: {e}"
            )

        await event.reply(

            WELCOME_NOT_JOINED,

            buttons=[

                [
                    Button.url(
                        "✨ JOIN CHANNEL ✨",
                        url=f"https://t.me/{channel}"
                    )
                ],

                [
                    Button.inline(
                        "✅ UNMUTE ME",
                        data=f"unmute_{user.id}"
                    )
                ]

            ]

        )


# =========================
# MESSAGE CHECK
# =========================

@bot.on(events.NewMessage(incoming=True))
async def mute_on_message(event):

    if event.is_private:
        return

    if not ON_NEW_MSG:
        return

    try:

        joined = await get_user_join(
            event.sender_id
        )

        if joined:
            return

        user = await event.get_sender()

        # FIX ERROR CHANNEL BOT
        if not hasattr(user, "bot"):
            return

        if user.bot:
            return

        await bot.edit_permissions(

            event.chat.id,

            event.sender_id,

            send_messages=False

        )

        await event.reply(

            WELCOME_NOT_JOINED,

            buttons=[

                [
                    Button.url(
                        "✨ JOIN CHANNEL ✨",
                        url=f"https://t.me/{channel}"
                    )
                ],

                [
                    Button.inline(
                        "✅ UNMUTE ME",
                        data=f"unmute_{event.sender_id}"
                    )
                ]

            ]

        )

    except Exception as e:

        log.error(
            f"MESSAGE CHECK ERROR: {e}"
        )


# =========================
# UNMUTE BUTTON
# =========================

@bot.on(
    events.CallbackQuery(
        data=re.compile(
            b"unmute_(.*)"
        )
    )
)
async def unmute_handler(event):

    uid = int(
        event.data_match.group(1).decode()
    )

    if uid != event.sender_id:

        await event.answer(
            "❌ tombol ini bukan buat kamu",
            alert=True
        )

        return

    joined = await get_user_join(uid)

    if not joined:

        await event.answer(
            f"🚫 join @{channel} dulu",
            alert=True
        )

        return

    try:

        await bot.edit_permissions(
            event.chat.id,
            uid,
            send_messages=True
        )

        await event.edit(

            (
                "╭──〔 ✅ VERIFIED 〕──╮\n"
                "┃\n"
                "┃ sekarang kamu bisa\n"
                "┃ mengirim pesan ✨\n"
                "┃\n"
                "╰────────────────╯"
            ),

            buttons=[
                [
                    Button.url(
                        "💌 CHANNEL",
                        url=f"https://t.me/{channel}"
                    )
                ]
            ]

        )

    except Exception as e:

        log.error(
            f"UNMUTE ERROR: {e}"
        )


# =========================
# AUTO DAILY RESET
# =========================

last_day = datetime.now().day


async def auto_daily_reset():

    global last_day

    while True:

        try:

            now = datetime.now()

            if now.day != last_day:

                last_day = now.day

                log.info(
                    "NEW DAY DETECTED"
                )

                await reset_limits()

                log.info(
                    "DAILY RESET DONE"
                )

        except Exception as e:

            log.error(
                f"RESET ERROR: {e}"
            )

        await asyncio.sleep(60)


# =========================
# AUTO MEMORY CLEAN
# =========================

async def auto_gc():

    while True:

        try:

            gc.collect()

        except:
            pass

        await asyncio.sleep(300)


# =========================
# IMPORT MODULES
# =========================

import modules.start
import modules.menfess
import modules.owner
import modules.upload

# =========================
# TASKS
# =========================

bot.loop.create_task(
    auto_daily_reset()
)

bot.loop.create_task(
    auto_gc()
)


# =========================
# START
# =========================

log.info(
    f"BOT STARTED AS @{bot_self.username}"
)


# =========================
# RUN LOOP
# =========================

while True:

    try:

        bot.run_until_disconnected()

    except Exception as e:

        log.error(
            f"BOT CRASHED: {e}"
        )

        log.info(
            "RESTARTING BOT..."
        )

        try:

            os.execv(
                sys.executable,
                [
                    sys.executable
                ] + sys.argv
            )

        except Exception as err:

            log.error(
                f"RESTART FAILED: {err}"
            )
