import logging
import re
from decouple import config
from telethon import TelegramClient, events, Button
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.utils import get_display_name
import asyncio
from reset_daily import reset_limits

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

log = logging.getLogger("MENFESS")

log.info("STARTING BOT...")

# CONFIG
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

WELCOME_MSG = (
    "╭──〔 💌 MENFESS AREA 〕──╮\n"
    "┃\n"
    "┃ Hai {mention}\n"
    "┃ Welcome to {title}\n"
    "┃\n"
    "┃ sekarang kamu bisa\n"
    "┃ mengirim menfes anonim ✨\n"
    "┃\n"
    "╰────────────────╯"
)

WELCOME_NOT_JOINED = (
    "╭──〔 🚫 ACCESS DENIED 〕──╮\n"
    "┃\n"
    "┃ Hai {mention}\n"
    "┃ kamu belum join\n"
    "┃ {channel}\n"
    "┃\n"
    "┃ join dulu supaya bisa\n"
    "┃ kirim menfes anonim 💌\n"
    "┃\n"
    "╰────────────────╯"
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

# CLIENT
bot = TelegramClient(
    "menfessbot",
    API_ID,
    API_HASH
).start(
    bot_token=BOT_TOKEN
)

channel = CHANNEL.replace("@", "")

bot_self = bot.loop.run_until_complete(
    bot.get_me()
)

# OWNER CHECK
def is_owner(user_id):

    return user_id in OWNER_IDS


# JOIN CHECK
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


# MEMBER JOIN
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

        chat = await event.get_chat()

        title = chat.title or "Group"

        mention = (
            f"[{get_display_name(user)}]"
            f"(tg://user?id={user.id})"
        )

        joined = await get_user_join(
            user.id
        )

        if joined:

            msg = WELCOME_MSG.format(
                mention=mention,
                title=title,
                channel=f"@{channel}"
            )

            buttons = [
                Button.url(
                    "💌 CHANNEL",
                    url=f"https://t.me/{channel}"
                )
            ]

        else:

            msg = WELCOME_NOT_JOINED.format(
                mention=mention,
                title=title,
                channel=f"@{channel}"
            )

            buttons = [

                Button.url(
                    "✨ JOIN CHANNEL ✨",
                    url=f"https://t.me/{channel}"
                ),

                Button.inline(
                    "✅ UNMUTE ME",
                    data=f"unmute_{user.id}"
                )

            ]

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
            msg,
            buttons=buttons
        )


# MESSAGE CHECK
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

        if user.bot:
            return

        await bot.edit_permissions(
            event.chat.id,
            event.sender_id,
            send_messages=False
        )

        mention = (
            f"[{get_display_name(user)}]"
            f"(tg://user?id={user.id})"
        )

        msg = WELCOME_NOT_JOINED.format(
            mention=mention,
            title=(await event.get_chat()).title,
            channel=f"@{channel}"
        )

        buttons = [

            Button.url(
                "✨ JOIN CHANNEL ✨",
                url=f"https://t.me/{channel}"
            ),

            Button.inline(
                "✅ UNMUTE ME",
                data=f"unmute_{event.sender_id}"
            )

        ]

        await event.reply(
            msg,
            buttons=buttons
        )

    except Exception as e:

        log.error(
            f"MESSAGE CHECK ERROR: {e}"
        )


# UNMUTE BUTTON
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
                Button.url(
                    "💌 CHANNEL",
                    url=f"https://t.me/{channel}"
                )
            ]
        )

    except Exception as e:

        log.error(
            f"UNMUTE ERROR: {e}"
        )


# START
@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):

    await event.reply(
        (
            "╭──〔 💌 MENFESS BOT 〕──╮\n"
            "┃\n"
            "┃ kirim pesan anonim\n"
            "┃ tanpa ketahuan identitas ✨\n"
            "┃\n"
            "┃ sebelum memakai bot\n"
            f"┃ wajib join @{channel}\n"
            "┃ terlebih dahulu\n"
            "┃\n"
            "╰────────────────╯"
        ),

        buttons=[
            [
                Button.url(
                    "✨ JOIN CHANNEL ✨",
                    url=f"https://t.me/{channel}"
                )
            ]
        ]
    )


import asyncio
import modules.menfess
import modules.owner
from reset_daily import reset_limits

bot.loop.create_task(
    reset_limits()
)

log.info(
    f"BOT STARTED AS @{bot_self.username}"
)

bot.run_until_disconnected()
