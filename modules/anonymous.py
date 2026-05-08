import asyncio
import time
import random
import string

from telethon import events, Button
from __main__ import bot

from database import (
    anonymous_db,
    request_db,
    premium_db
)

from config import (
    ADMIN_GROUP,
    ANON_CHANNEL
)

print("ANONYMOUS MODULE LOADED")

# =========================
# CONFIG
# =========================

REQUEST_TIMEOUT = 300

cooldown = {}

# =========================
# MODE
# =========================

anonymous_post_mode = set()
anonymous_reply_mode = {}

reply_sessions = {}

# =========================
# CLEANUP REPLY
# =========================

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
# PREMIUM CHECK
# =========================

async def get_premium(user_id):

    user = await premium_db.find_one(
        {
            "user_id": user_id
        }
    )

    if not user:
        return None

    return user

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
# MENU ANONYMOUS
# =========================

@bot.on(events.CallbackQuery(data=b"anonymous_help"))
async def anonymous_menu(event):

    text = (

        "╭━〔 📨 ANONYMOUS MENU 〕━╮\n"
        "┃\n"
        "┃  cara menggunakan:\n"
        "┃\n"
        "┃  💌 POST\n"
        "┃  kirim posting anonymous\n"
        "┃  ke channel bot\n"
        "┃\n"
        "┃  📨 REPLY\n"
        "┃  reply anonymous user\n"
        "┃  pakai kode / link post\n"
        "┃\n"
        "┃  setelah connect\n"
        "┃  kalian bisa chat anonim\n"
        "┃  tanpa ketahuan identitas\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━╯"

    )

    buttons = [

        [
            Button.inline(
                "💌 POST",
                data=b"anonymous_post"
            ),

            Button.inline(
                "📨 REPLY",
                data=b"anonymous_reply"
            )
        ],

        [
            Button.inline(
                "⬅️ KEMBALI",
                data=b"back_start"
            )
        ]

    ]

    await event.edit(
        text,
        buttons=buttons
    )

# =========================
# POST MENU
# =========================

@bot.on(events.CallbackQuery(data=b"anonymous_post"))
async def anonymous_post(event):

    anonymous_post_mode.add(
        event.sender_id
    )

    await event.edit(

        (
            "╭━〔 💌 ANONYMOUS POST 〕━╮\n"
            "┃\n"
            "┃  silahkan kirim pesan\n"
            "┃  anonymous sekarang ✨\n"
            "┃\n"
            "┃  support:\n"
            "┃  • text\n"
            "┃  • photo\n"
            "┃  • video\n"
            "┃\n"
            "┃  posting akan masuk\n"
            "┃  ke channel anonymous\n"
            "┃\n"
            "┃  non premium:\n"
            "┃  harus menunggu approve admin\n"
            "┃\n"
            "╰━━━━━━━━━━━━━━━━━━╯"
        ),

        buttons=[

            [
                Button.inline(
                    "⬅️ KEMBALI",
                    data=b"anonymous_help"
                )
            ]

        ]

    )

# =========================
# REPLY MENU
# =========================

@bot.on(events.CallbackQuery(data=b"anonymous_reply"))
async def anonymous_reply(event):

    anonymous_reply_mode[
        event.sender_id
    ] = True

    await event.edit(

        (
            "╭━〔 📨 ANONYMOUS REPLY 〕━╮\n"
            "┃\n"
            "┃  kirim kode reply\n"
            "┃  atau link postingan\n"
            "┃\n"
            "┃  contoh kode:\n"
            "┃  ABC12345\n"
            "┃\n"
            "┃  contoh link:\n"
            "┃  t.me/channel/123\n"
            "┃\n"
            "╰━━━━━━━━━━━━━━━━━━╯"
        ),

        buttons=[

            [
                Button.inline(
                    "⬅️ KEMBALI",
                    data=b"anonymous_help"
                )
            ]

        ]

    )

# =========================
# HANDLE REPLY CODE
# =========================

@bot.on(events.NewMessage(incoming=True))
async def handle_reply_code(event):

    if not event.is_private:
        return

    if event.sender_id not in anonymous_reply_mode:
        return

    code = (
        event.raw_text or ""
    ).strip().upper()

    anonymous_reply_mode.pop(
        event.sender_id,
        None
    )

    if "T.ME/" in code:

        try:

            code = code.split("/")[-1]

        except:
            pass

    if code not in reply_sessions:

        return await event.reply(
            "❌ kode reply tidak ditemukan"
        )

    sender_id = event.sender_id

    owner_id = reply_sessions[
        code
    ]["user_id"]

    if sender_id == owner_id:

        return await event.reply(
            "❌ tidak bisa reply diri sendiri"
        )

    sender_room = await get_room(
        sender_id
    )

    if sender_room:

        return await event.reply(
            "❌ kamu masih di anonymous room"
        )

    owner_room = await get_room(
        owner_id
    )

    if owner_room:

        return await event.reply(
            "❌ target sedang sibuk"
        )

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
        "✅ request anonymous dikirim"
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

    await anonymous_db.insert_one(

        {
            "owner": owner_id,
            "partner": sender_id
        }

    )

    await request_db.delete_one(
        {
            "owner": owner_id
        }
    )

    await event.edit(
        "✅ anonymous connected"
    )

    await bot.send_message(

        sender_id,

        (
            "✅ anonymous diterima\n\n"
            "/next = skip\n"
            "/cancel = keluar"
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
# ANONYMOUS POST
# =========================

@bot.on(events.NewMessage(incoming=True))
async def anonymous_post_handler(event):

    if not event.is_private:
        return

    if event.sender_id not in anonymous_post_mode:
        return

    if event.raw_text:

        if event.raw_text.startswith("/"):
            return

    anonymous_post_mode.discard(
        event.sender_id
    )

    sender = await event.get_sender()

    premium = await get_premium(
        event.sender_id
    )

    now = time.time()

    # =========================
    # COOLDOWN
    # =========================

    if premium:

        if event.sender_id in cooldown:

            delay = now - cooldown[event.sender_id]

            if delay < 5:

                return await event.reply(
                    "❌ tunggu 5 detik"
                )

        cooldown[event.sender_id] = now

    else:

        if event.sender_id in cooldown:

            delay = now - cooldown[event.sender_id]

            if delay < 15:

                return await event.reply(
                    "❌ tunggu 15 detik"
                )

        cooldown[event.sender_id] = now

    try:

        reply_code = generate_code()

        reply_sessions[reply_code] = {
            "user_id": event.sender_id,
            "time": time.time()
        }

        caption = (
            f"{event.raw_text or ''}\n\n"
            f"↩️ reply code:\n"
            f"`{reply_code}`"
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

            if event.media:

                await bot.send_file(
                    ANON_CHANNEL,
                    file=event.media,
                    caption=caption
                )

            else:

                await bot.send_message(
                    ANON_CHANNEL,
                    caption
                )

            if premium["tier"] != "pro":

                await premium_db.update_one(
                    {
                        "user_id": event.sender_id
                    },
                    {
                        "$inc": {
                            "limit": -1
                        }
                    }
                )

            return await event.reply(
                "✅ anonymous berhasil dipost otomatis"
            )

        # =========================
        # FREE USER NEED APPROVE
        # =========================

        admin_caption = (
            f"{event.raw_text or ''}\n\n"
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
                            data=f"approveanon_{event.sender_id}_{reply_code}"
                        ),

                        Button.inline(
                            "❌ REJECT",
                            data=f"rejectanon_{event.sender_id}"
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
                            data=f"approveanon_{event.sender_id}_{reply_code}"
                        ),

                        Button.inline(
                            "❌ REJECT",
                            data=f"rejectanon_{event.sender_id}"
                        )
                    ]

                ]

            )

        await event.reply(
            "✅ anonymous dikirim ke admin"
        )

    except Exception as e:

        print(f"POST ERROR : {e}")

        await event.reply(
            f"❌ gagal post anonymous\n\n{e}"
        )

# =========================
# APPROVE ANON
# =========================

@bot.on(events.CallbackQuery(pattern=b"approveanon_(.*)_(.*)"))
async def approve_anon(event):

    uid = int(
        event.data_match.group(1).decode()
    )

    code = event.data_match.group(2).decode()

    try:

        msg = await event.get_message()

        raw = msg.raw_text or ""

        anon_text = raw.split(
            "\n\nCODE :",
            1
        )[0]

        caption = (
            f"{anon_text}\n\n"
            f"↩️ reply code:\n"
            f"`{code}`"
        )

        if msg.media:

            await bot.send_file(
                ANON_CHANNEL,
                file=msg.media,
                caption=caption
            )

        else:

            await bot.send_message(
                ANON_CHANNEL,
                caption
            )

        await event.edit(
            "✅ anonymous approved"
        )

        await bot.send_message(
            uid,
            "✅ anonymous berhasil dipost"
        )

    except Exception as e:

        print(f"APPROVE ERROR : {e}")

# =========================
# REJECT ANON
# =========================

@bot.on(events.CallbackQuery(pattern=b"rejectanon_(.*)"))
async def reject_anon(event):

    uid = int(
        event.data_match.group(1).decode()
    )

    await event.edit(
        "❌ anonymous rejected"
    )

    await bot.send_message(
        uid,
        "❌ anonymous ditolak admin"
    )

# =========================
# MESSAGE HANDLER
# =========================

@bot.on(events.NewMessage(incoming=True))
async def anonymous_chat(event):

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

# =========================
# CLEANUP REQUEST
# =========================

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
