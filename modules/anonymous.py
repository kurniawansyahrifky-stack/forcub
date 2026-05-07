import asyncio
import time
from telethon import events, Button
from __main__ import bot

from database import anonymous_db, request_db
from modules.menfess import reply_sessions

print("ANONYMOUS MODULE LOADED")
REQUEST_TIMEOUT = 300
cooldown = {}
# =========================
# CEK ROOM
# =========================

async def get_room(user_id):

    return await anonymous_db.find_one(
        {
            "$or": [
                {"owner": user_id},
                {"partner": user_id}
            ]
        }
    )

# =========================
# REPLY
# =========================

@bot.on(events.NewMessage(pattern=r"/reply (.+)"))
async def reply_command(event):

    if not event.is_private:
        return

    args = event.raw_text.split(" ", 1)

    if len(args) < 2:

        return await event.reply(
            "❌ contoh : /reply ABC12345"
        )

    code = args[1].strip().upper()

    if code not in reply_sessions:

        return await event.reply(
            "❌ kode tidak ditemukan"
        )

    sender_id = event.sender_id
    owner_id = reply_sessions[code]["user_id"]

    if sender_id == owner_id:

        return await event.reply(
            "❌ tidak bisa reply diri sendiri"
        )

    # CEK ROOM
    sender_room = await get_room(sender_id)

    if sender_room:

        return await event.reply(
            "❌ kamu masih di anonymous room\n"
            "gunakan /cancel dulu"
        )

    owner_room = await get_room(owner_id)

    if owner_room:

        return await event.reply(
            "❌ target sedang sibuk"
        )

    # SAVE REQUEST
    await request_db.update_one(
        {
            "owner": owner_id
        },
        {
            "$set": {
                "sender": sender_id,
                "code": code,
                "created": time.time()
            }
        },
        upsert=True
    )

    buttons = [

        [
            Button.inline(
                "✅ ACCEPT",
                data=f"accept_{sender_id}"
            ),

            Button.inline(
                "❌ REJECT",
                data=f"reject_{sender_id}"
            )
        ],

        [
            Button.inline(
                "⏭ NEXT",
                data=f"next_{sender_id}"
            )
        ]

    ]

    await bot.send_message(

        owner_id,

        (
            "💌 ada anonymous ingin chat\n\n"
            "pilih accept atau reject"
        ),

        buttons=buttons

    )

    await event.reply(
        "✅ request dikirim"
    )

# =========================
# ACCEPT
# =========================

@bot.on(events.CallbackQuery(pattern=b"accept_(.*)"))
async def accept_room(event):

    sender_id = int(
        event.data_match.group(1).decode()
    )

    owner_id = event.sender_id

    req = await request_db.find_one(
        {
            "owner": owner_id
        }
    )

    if not req:

        return await event.answer(
            "request expired"
        )

    # SAVE ROOM
    await anonymous_db.insert_one(
        {
            "owner": owner_id,
            "partner": sender_id
        }
    )

    # DELETE REQUEST
    await request_db.delete_one(
        {
            "owner": owner_id
        }
    )

    await event.edit(
        "✅ anonymous room connected"
    )

    await bot.send_message(

        sender_id,

        (
            "✅ anonymous diterima\n\n"
            "sekarang kalian bisa chat\n\n"
            "/cancel = keluar\n"
            "/next = skip"
        )

    )

# =========================
# REJECT
# =========================

@bot.on(events.CallbackQuery(pattern=b"reject_(.*)"))
async def reject_room(event):

    sender_id = int(
        event.data_match.group(1).decode()
    )

    owner_id = event.sender_id

    await request_db.delete_one(
        {
            "owner": owner_id
        }
    )

    await event.edit(
        "❌ anonymous ditolak"
    )

    await bot.send_message(
        sender_id,
        "❌ request ditolak"
    )

# =========================
# NEXT
# =========================

@bot.on(events.NewMessage(pattern=r"/next"))
async def next_room(event):

    room = await get_room(
        event.sender_id
    )

    if not room:

        return await event.reply(
            "❌ kamu tidak berada di room"
        )

    owner = room["owner"]
    partner = room["partner"]

    await anonymous_db.delete_one(
        {
            "_id": room["_id"]
        }
    )

    target = owner if event.sender_id == partner else partner

    try:

        await bot.send_message(
            target,
            "⏭ partner skip room"
        )

    except:
        pass

    await event.reply(
        "✅ room diskip"
    )

# =========================
# CANCEL
# =========================

@bot.on(events.NewMessage(pattern=r"/cancel"))
async def cancel_room(event):

    room = await get_room(
        event.sender_id
    )

    if not room:

        return await event.reply(
            "❌ kamu tidak berada di room"
        )

    owner = room["owner"]
    partner = room["partner"]

    await anonymous_db.delete_one(
        {
            "_id": room["_id"]
        }
    )

    target = owner if event.sender_id == partner else partner

    try:

        await bot.send_message(
            target,
            "❌ partner keluar dari room"
        )

    except:
        pass

    await event.reply(
        "✅ room ditutup"
    )

# =========================
# MESSAGE HANDLER
# =========================

@bot.on(events.NewMessage(incoming=True))
async def anonymous_chat(event):

    now = time.time()

    last = cooldown.get(
        event.sender_id,
        0
    )

    if now - last < 1.5:
        return

    cooldown[event.sender_id] = now

    if not event.is_private:
        return

    if event.raw_text:

        if event.raw_text.startswith("/"):
            return

    room = await get_room(
        event.sender_id
    )

    if not room:
        return

    owner = room["owner"]
    partner = room["partner"]

    target = owner if event.sender_id == partner else partner

    try:

        if event.media:

            await bot.send_file(
                target,
                file=event.media,
                caption=(
                    "💌 anonymous message\n\n"
                    f"{event.raw_text or ''}"
                )
            )

        else:

            await bot.send_message(
                target,
                (
                    "💌 anonymous message\n\n"
                    f"{event.raw_text}"
                )
            )

    except Exception as e:

        print(f"ANON ERROR : {e}")

        await anonymous_db.delete_one(
            {
                "_id": room["_id"]
            }
        )


async def cleanup_requests():

    while True:

        try:

            now = time.time()

            await request_db.delete_many(
                {
                    "created": {
                        "$lt": now - REQUEST_TIMEOUT
                    }
                }
            )

        except Exception as e:

            print(f"CLEANUP ERROR : {e}")

        await asyncio.sleep(60)

bot.loop.create_task(
    cleanup_requests()
)
