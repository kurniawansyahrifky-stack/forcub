from telethon import events, Button

from __main__ import bot, is_owner
from database import premium_db

print("OWNER MODULE LOADED")


@bot.on(events.NewMessage(pattern="/panel"))
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
            "╰────────────────────╯"
        ),

        buttons=[

            [
                Button.inline(
                    "📊 STATS",
                    data="stats"
                ),

                Button.inline(
                    "💎 PREMIUM",
                    data="premium"
                )
            ],

            [
                Button.inline(
                    "📢 BROADCAST",
                    data="broadcast"
                ),

                Button.inline(
                    "⚙ SETTINGS",
                    data="settings"
                )
            ]
        ]
    )


@bot.on(events.CallbackQuery(data=b"premium"))
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
            "╰────────────────────╯"
        ),

        buttons=[

            [
                Button.inline(
                    "⬅ BACK",
                    data="back_panel"
                )
            ]
        ]
    )


@bot.on(events.CallbackQuery(data=b"stats"))
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
            "╰──────────────────────╯"
        ),

        buttons=[

            [
                Button.inline(
                    "⬅ BACK",
                    data="back_panel"
                )
            ]
        ]
    )


@bot.on(events.CallbackQuery(data=b"back_panel"))
async def back_panel(event):

    await event.edit(

        (
            "╭──〔 👑 OWNER PANEL 〕──╮\n"
            "┃\n"
            "┃ welcome owner\n"
            "┃ control your bot here\n"
            "┃\n"
            "╰────────────────────╯"
        ),

        buttons=[

            [
                Button.inline(
                    "📊 STATS",
                    data="stats"
                ),

                Button.inline(
                    "💎 PREMIUM",
                    data="premium"
                )
            ],

            [
                Button.inline(
                    "📢 BROADCAST",
                    data="broadcast"
                ),

                Button.inline(
                    "⚙ SETTINGS",
                    data="settings"
                )
            ]
        ]
    )
