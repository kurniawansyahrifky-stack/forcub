from telethon import events, Button
from __main__ import bot, is_owner
from database import premium_db, users_db

print("OWNER MODULE LOADED")

# ========================
# BROADCAST MODE
# ========================

import asyncio

broadcast_mode = set()

# ========================
# BROADCAST PANEL
# ========================

@bot.on(events.CallbackQuery(data=b"owner_broadcast"))
async def broadcast_panel(event):

    if not is_owner(event.sender_id):
        return

    broadcast_mode.add(event.sender_id)

    await event.edit(
        (
            "╭──〔 📢 BROADCAST 〕──╮\n"
            "┃\n"
            "┃ reply pesan / foto / video\n"
            "┃ lalu ketik /bc\n"
            "┃\n"
            "┃ support media & caption\n"
            "┃ anti flood system ✨\n"
            "┃\n"
            "┃ /cancel untuk batal\n"
            "┃\n"
            "╰──────────────────╯"
        ),
        buttons=[
            [
                Button.inline(
                    "⬅ BACK",
                    data=b"owner_back"
                )
            ]
        ]
    )

# ========================
# CANCEL BROADCAST
# ========================

@bot.on(events.NewMessage(pattern=r"^/cancel$"))
async def cancel_broadcast(event):

    if event.sender_id not in broadcast_mode:
        return

    broadcast_mode.discard(event.sender_id)

    await event.reply(
        "✅ broadcast dibatalkan."
    )

# ========================
# BROADCAST COMMAND
# ========================

@bot.on(events.NewMessage(pattern=r"^/bc$"))
async def broadcast_cmd(event):

    if not is_owner(event.sender_id):
        return

    if event.sender_id not in broadcast_mode:
        return await event.reply(
            "masuk panel broadcast dulu."
        )

    if not event.is_reply:
        return await event.reply(
            "reply pesan/photo/video."
        )

    msg = await event.get_reply_message()

    users = users_db.find({})

    total = 0
    failed = 0

    proses = await event.reply(
        "📢 memulai broadcast..."
    )

    async for user in users:

        user_id = user.get("user_id")

        if not user_id:
            continue

        try:

            # PHOTO / VIDEO / FILE
            if msg.media:

                await bot.send_file(
                    user_id,
                    file=msg.media,
                    caption=msg.text or ""
                )

            # TEXT
            else:

                await bot.send_message(
                    user_id,
                    msg.text
                )

            total += 1

            # ANTI FLOOD
            await asyncio.sleep(0.08)

        except Exception:
            failed += 1

            # FLOOD WAIT HANDLER
            await asyncio.sleep(1)

    broadcast_mode.discard(event.sender_id)

    await proses.edit(
        (
            "╭──〔 ✅ BROADCAST DONE 〕──╮\n"
            "┃\n"
            f"┃ success : {total}\n"
            f"┃ failed : {failed}\n"
            "┃\n"
            "╰──────────────────────╯"
        )
    )

# ========================
# OWNER PANEL
# ========================

@bot.on(events.NewMessage(pattern=r"^/panel$"))
async def owner_panel(event):

    if not is_owner(event.sender_id):
        return

    await event.reply(
        (
            "╭──〔 👑 OWNER PANEL 〕──╮\n"
            "┃\n"
            "┃ welcome owner\n"
            "┃ control your bot here\n"
            "┃\n"
            "╰──────────────────╯"
        ),
        buttons=[
            [
                Button.inline(
                    "📊 STATS",
                    data=b"owner_stats"
                ),
                Button.inline(
                    "💎 PREMIUM",
                    data=b"owner_premium"
                )
            ],
            [
                Button.inline(
                    "📢 BROADCAST",
                    data=b"owner_broadcast"
                ),
                Button.inline(
                    "⚙ SETTINGS",
                    data=b"owner_settings"
                )
            ]
        ]
    )

# ========================
# PREMIUM PANEL
# ========================

@bot.on(events.CallbackQuery(data=b"owner_premium"))
async def premium_panel(event):

    lite = await premium_db.count_documents(
        {
            "tier": "lite"
        }
    )

    basic = await premium_db.count_documents(
        {
            "tier": "basic"
        }
    )

    pro = await premium_db.count_documents(
        {
            "tier": "pro"
        }
    )

    total = lite + basic + pro

    await event.edit(
        (
            "╭──〔 💎 PREMIUM PANEL 〕──╮\n"
            "┃\n"
            f"┃ total premium : {total}\n"
            f"┃ lite users : {lite}\n"
            f"┃ basic users : {basic}\n"
            f"┃ pro users : {pro}\n"
            "┃\n"
            "┣━━〔 COMMAND 〕━━\n"
            "┃ /lite\n"
            "┃ /basic\n"
            "┃ /pro\n"
            "┃ /unprem\n"
            "┃\n"
            "╰──────────────────╯"
        ),
        buttons=[
            [
                Button.inline(
                    "⬅ BACK",
                    data=b"owner_back"
                )
            ]
        ]
    )

# ========================
# STATS PANEL
# ========================

@bot.on(events.CallbackQuery(data=b"owner_stats"))
async def stats_panel(event):

    total_users = await premium_db.count_documents({})

    lite = await premium_db.count_documents(
        {
            "tier": "lite"
        }
    )

    basic = await premium_db.count_documents(
        {
            "tier": "basic"
        }
    )

    pro = await premium_db.count_documents(
        {
            "tier": "pro"
        }
    )

    await event.edit(
        (
            "╭──〔 📊 BOT STATISTICS 〕──╮\n"
            "┃\n"
            f"┃ total premium : {total_users}\n"
            f"┃ lite users : {lite}\n"
            f"┃ basic users : {basic}\n"
            f"┃ pro users : {pro}\n"
            "┃\n"
            "┃ bot status : online\n"
            "┃ database : connected\n"
            "┃\n"
            "╰─────────────────────╯"
        ),
        buttons=[
            [
                Button.inline(
                    "⬅ BACK",
                    data=b"owner_back"
                )
            ]
        ]
    )

# ========================
# SETTINGS PANEL
# ========================

@bot.on(events.CallbackQuery(data=b"owner_settings"))
async def settings_panel(event):

    await event.answer(
        "⚙ settings belum tersedia.",
        alert=True
    )

# ========================
# BROADCAST PANEL
# ========================

@bot.on(events.CallbackQuery(data=b"owner_broadcast"))
async def broadcast_panel(event):

    if not is_owner(event.sender_id):
        return

    broadcast_mode.add(event.sender_id)

    await event.edit(
        (
            "╭──〔 📢 BROADCAST 〕──╮\n"
            "┃\n"
            "┃ kirim pesan apapun\n"
            "┃ untuk broadcast user\n"
            "┃\n"
            "┃ /cancel untuk batal\n"
            "┃\n"
            "╰──────────────────╯"
        ),
        buttons=[
            [
                Button.inline(
                    "⬅ BACK",
                    data=b"owner_back"
                )
            ]
        ]
    )

# ========================
# CANCEL BROADCAST
# ========================

@bot.on(events.NewMessage(pattern=r"^/cancel$"))
async def cancel_broadcast(event):

    if event.sender_id not in broadcast_mode:
        return

    broadcast_mode.discard(event.sender_id)

    await event.reply(
        "✅ broadcast dibatalkan."
    )

# ========================
# PROCESS BROADCAST
# ========================

@bot.on(events.NewMessage)
async def process_broadcast(event):

    if event.sender_id not in broadcast_mode:
        return

    if event.text and event.text.startswith("/"):
        return

    broadcast_mode.discard(event.sender_id)

    total = 0

    users = premium_db.find({})

    async for user in users:

        user_id = user.get("user_id")

        if not user_id:
            continue

        try:

            if event.media:

                await bot.send_file(
                    user_id,
                    file=event.media,
                    caption=event.text or ""
                )

            else:

                await bot.send_message(
                    user_id,
                    event.text
                )

            total += 1

        except:
            pass

    await event.reply(
        f"✅ broadcast berhasil dikirim ke {total} user."
    )

# ========================
# BACK PANEL
# ========================

@bot.on(events.CallbackQuery(data=b"owner_back"))
async def back_panel(event):

    await event.edit(
        (
            "╭──〔 👑 OWNER PANEL 〕──╮\n"
            "┃\n"
            "┃ welcome owner\n"
            "┃ control your bot here\n"
            "┃\n"
            "╰──────────────────╯"
        ),
        buttons=[
            [
                Button.inline(
                    "📊 STATS",
                    data=b"owner_stats"
                ),
                Button.inline(
                    "💎 PREMIUM",
                    data=b"owner_premium"
                )
            ],
            [
                Button.inline(
                    "📢 BROADCAST",
                    data=b"owner_broadcast"
                ),
                Button.inline(
                    "⚙ SETTINGS",
                    data=b"owner_settings"
                )
            ]
        ]
    )
