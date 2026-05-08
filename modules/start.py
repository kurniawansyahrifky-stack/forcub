from telethon import events, Button
from decouple import config
from __main__ import bot
import os
from database import users_db

# ========================
# CONFIG
# ========================

CHANNEL_1 = config("CHANNEL")
CHANNEL_2 = config("CHANNEL_2", default=None)
CHANNEL_3 = config("CHANNEL_3", default=None)

ADMIN_GROUP = config("ADMIN_GROUP")

START_PHOTO = "photos/start.jpg"
QR_PHOTO = "photos/qr.jpg"

# ========================
# USER PAYMENT MODE
# ========================

waiting_payment = set()

# ========================
# START BUTTONS
# ========================

def get_start_buttons():

    buttons = []

    if CHANNEL_1:

        buttons.append(
            [
                Button.url(
                    "✦ JOIN CHANNEL 1 ✦",
                    url=f"https://t.me/{CHANNEL_1.replace('@', '')}"
                )
            ]
        )

    if CHANNEL_2:

        buttons.append(
            [
                Button.url(
                    "✦ JOIN CHANNEL 2 ✦",
                    url=f"https://t.me/{CHANNEL_2.replace('@', '')}"
                )
            ]
        )

    if CHANNEL_3:

        buttons.append(
            [
                Button.url(
                    "✦ JOIN CHANNEL 3 ✦",
                    url=f"https://t.me/{CHANNEL_3.replace('@', '')}"
                )
            ]
        )

    buttons.append(
        [
            Button.inline(
                "💌 MENFESS",
                data=b"menfess"
            ),

            Button.inline(
                "📨 ANONYMOUS",
                data=b"anonymous_help"
            )
        ]
    )

    buttons.append(
        [
            Button.inline(
                "💎 PREMIUM",
                data=b"premium"
            )
        ]
    )

    return buttons

# ========================
# START CAPTION
# ========================

def start_caption():

    return (

        "╭━〔 ✦ 𝗠𝗘𝗡𝗙𝗘𝗦𝗦 𝗕𝗢𝗧 ✦ 〕━╮\n"
        "┃\n"
        "┃  𝐒𝐞𝐥𝐚𝐦𝐚𝐭 𝐃𝐚𝐭𝐚𝐧𝐠\n"
        "┃  𝐃𝐢 𝐁𝐨𝐭 𝐌𝐞𝐧𝐟𝐞𝐬𝐬 💌\n"
        "┃\n"
        "┃  tempat confess anonim\n"
        "┃  cari teman • sahabat • partner\n"
        "┃  tanpa ketahuan identitas ✨\n"
        "┃\n"
        "┃  wajib join channel\n"
        "┃  sebelum menggunakan bot\n"
        "┃\n"
        "┃  tersedia premium access\n"
        "┃  fitur lebih fast & exclusive\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━╯"

    )

# ========================
# START
# ========================

@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):

    user = await users_db.find_one(
        {
            "user_id": event.sender_id
        }
    )

    if not user:

        await users_db.insert_one(
            {
                "user_id": event.sender_id
            }
        )

    await bot.send_file(
        event.chat_id,
        START_PHOTO,
        caption=start_caption(),
        buttons=get_start_buttons()
    )

# ========================
# ANONYMOUS MENU
# ========================

@bot.on(events.CallbackQuery(data=b"anonymous_help"))
async def anonymous_help(event):

    text = (

        "╭━〔 📨 ANONYMOUS MENU 〕━╮\n"
        "┃\n"
        "┃  fitur anonymous:\n"
        "┃\n"
        "┃  ✦ anonymous posting\n"
        "┃  ✦ anonymous reply\n"
        "┃  ✦ anonymous chat\n"
        "┃\n"
        "┃  pilih menu dibawah\n"
        "┃  untuk melanjutkan ✨\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━╯"

    )

    buttons = [

        [
            Button.inline(
                "📝 POSTING",
                data=b"anon_post"
            ),

            Button.inline(
                "💬 REPLY",
                data=b"anon_reply"
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

# ========================
# ANON POST
# ========================

@bot.on(events.CallbackQuery(data=b"anon_post"))
async def anon_post(event):

    text = (

        "╭━〔 📝 ANONYMOUS POST 〕━╮\n"
        "┃\n"
        "┃  cara posting anonymous:\n"
        "┃\n"
        "┃  1. klik tombol mulai\n"
        "┃\n"
        "┃  2. kirim pesan / foto\n"
        "┃     / video yang ingin\n"
        "┃     diposting\n"
        "┃\n"
        "┃  3. bot akan memproses\n"
        "┃     postingan kamu ✨\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━╯"

    )

    buttons = [

        [
            Button.inline(
                "💌 MULAI POSTING",
                data=b"menfess"
            )
        ],

        [
            Button.inline(
                "⬅️ KEMBALI",
                data=b"anonymous_help"
            )
        ]

    ]

    await event.edit(
        text,
        buttons=buttons
    )

# ========================
# ANON REPLY
# ========================

@bot.on(events.CallbackQuery(data=b"anon_reply"))
async def anon_reply(event):

    text = (

        "╭━〔 💬 ANONYMOUS REPLY 〕━╮\n"
        "┃\n"
        "┃  cara reply anonymous:\n"
        "┃\n"
        "┃  1. salin kode reply\n"
        "┃     atau link postingan\n"
        "┃\n"
        "┃  2. kirim command:\n"
        "┃     /reply KODE\n"
        "┃\n"
        "┃  contoh:\n"
        "┃  /reply ABC12345\n"
        "┃\n"
        "┃  3. lalu kirim pesan\n"
        "┃     anonymous kamu ✨\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━╯"

    )

    buttons = [

        [
            Button.inline(
                "💬 MULAI REPLY",
                data=b"reply_help"
            )
        ],

        [
            Button.inline(
                "⬅️ KEMBALI",
                data=b"anonymous_help"
            )
        ]

    ]

    await event.edit(
        text,
        buttons=buttons
    )

# ========================
# REPLY HELP
# ========================

@bot.on(events.CallbackQuery(data=b"reply_help"))
async def reply_help(event):

    await bot.send_message(

        event.sender_id,

        (
            "💬 silahkan kirim command:\n\n"
            "/reply KODE\n\n"
            "contoh:\n"
            "/reply ABC12345"
        )

    )

    await event.answer(
        "cek private chat"
    )

# ========================
# PREMIUM MENU
# ========================

@bot.on(events.CallbackQuery(data=b"premium"))
async def premium_menu(event):

    text = (

        "╭━〔 💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗣𝗔𝗖𝗞𝗔𝗚𝗘 💎 〕━╮\n"
        "┃\n"
        "┃  ✦ Lite   → 3K\n"
        "┃  ✦ Basic  → 5K\n"
        "┃  ✦ Pro    → 10K\n"
        "┃\n"
        "┃  pilih paket premium\n"
        "┃  untuk melanjutkan pembayaran ✨\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"

    )

    buttons = [

        [
            Button.inline(
                "💠 LITE 3K",
                data=b"lite"
            ),

            Button.inline(
                "💠 BASIC 5K",
                data=b"basic"
            )
        ],

        [
            Button.inline(
                "👑 PRO 10K",
                data=b"pro"
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

# ========================
# BACK TO START
# ========================

@bot.on(events.CallbackQuery(data=b"back_start"))
async def back_start(event):

    await bot.send_file(
        event.chat_id,
        START_PHOTO,
        caption=start_caption(),
        buttons=get_start_buttons()
    )

    await event.delete()

# ========================
# PAYMENT HANDLER
# ========================

@bot.on(events.CallbackQuery(data=b"lite"))
@bot.on(events.CallbackQuery(data=b"basic"))
@bot.on(events.CallbackQuery(data=b"pro"))
async def payment_handler(event):

    paket = event.data.decode()

    if paket == "lite":
        harga = "3K"

    elif paket == "basic":
        harga = "5K"

    else:
        harga = "10K"

    waiting_payment.add(event.sender_id)

    caption = (

        f"╭━〔 💳 𝗣𝗔𝗬𝗠𝗘𝗡𝗧 {paket.upper()} 〕━╮\n"
        "┃\n"
        f"┃  Paket : {paket.upper()}\n"
        f"┃  Harga : {harga}\n"
        "┃\n"
        "┃  silahkan transfer\n"
        "┃  sesuai nominal diatas ✨\n"
        "┃\n"
        "┃  setelah transfer\n"
        "┃  kirim bukti pembayaran\n"
        "┃  ke bot ini\n"
        "┃\n"
        "╰━━━━━━━━━━━━━━━━━━╯"

    )

    buttons = [
        [
            Button.inline(
                "⬅️ KEMBALI",
                data=b"premium"
            )
        ]
    ]

    await bot.send_file(
        event.chat_id,
        QR_PHOTO,
        caption=caption,
        buttons=buttons
    )

# ========================
# BUKTI TRANSFER ONLY
# ========================

@bot.on(events.NewMessage(incoming=True))
async def bukti_transfer(event):

    if event.sender_id not in waiting_payment:
        return

    if event.text and event.text.startswith("/"):
        return

    if not (event.photo or event.document):
        return

    sender = await event.get_sender()

    caption = (

        "💎 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡 𝗣𝗥𝗘𝗠𝗜𝗨𝗠\n\n"
        f"👤 User : {sender.first_name}\n"
        f"🆔 ID : `{sender.id}`\n"
        f"📩 Username : @{sender.username if sender.username else '-'}\n\n"
        "silahkan cek bukti transfer."

    )

    await bot.forward_messages(
        ADMIN_GROUP,
        event.message
    )

    await bot.send_message(
        ADMIN_GROUP,
        caption
    )

    waiting_payment.discard(event.sender_id)

    await event.reply(
        "✨ bukti transfer berhasil dikirim\n"
        "silahkan tunggu admin memverifikasi pembayaran."
    )
