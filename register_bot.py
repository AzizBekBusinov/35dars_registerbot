# import logging
# from telegram import ReplyKeyboardMarkup, KeyboardButton
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
# import sqlite3
# from geo_name import get_location_name
#
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#
# conn = sqlite3.connect("users.db")
# c = conn.cursor()
#
# c.execute("""CREATE TABLE IF NOT EXISTS users
#             (phone_number TEXT PRIMARY KEY,
#             first_name TEXT,
#             last_name TEXT,
#             age INTEGER,
#             gender TEXT,
#             address TEXT,
#             latitude REAL,
#             longitude REAL
#             );
#
# """)
# conn.commit()
#
#
# def start(update, context):
#     reply_text = 'Salom! telefon raqamingizni kiriting:'
#     reply_markup = ReplyKeyboardMarkup([
#         [KeyboardButton(text="Telefon kontaktinngizni ulashing", request_contact=True)]
#     ], resize_keyboard=True, one_time_keyboard=True)
#     context.bot.send_message(chat_id=update.effective_user.id, text=reply_text, reply_markup=reply_markup)
#     logging.info(f"user - {update.effective_user.id} started")
#
#     return 'PHONE_NUMBER'
#
#
# def phone_number(update, context):
#     phone_number = update.message.contact.phone_number
#     context.user_data['phone_number'] = phone_number
#     update.message.reply_text('Rahmat! Ismingiz nima?')
#     return 'FIRST_NAME'
#
#
# def first_name(update, context):
#     first_name = update.message.text
#     context.user_data['first_name'] = first_name
#     update.message.reply_text('Rahmat! Familyangiz nima?')
#     return 'LAST_NAME'
#
#
# def last_name(update, context):
#     last_name = update.message.text
#     context.user_data['last_name'] = last_name
#     update.message.reply_text('Rahmat! yoshingiz?')
#     return 'AGE'
#
#
# def age(update, context):
#     age = update.message.text
#     context.user_data['age'] = age
#     update.message.reply_text('Rahmat! Jinsingiz: erkak/ayol?')
#     return 'GENDER'
#
#
# def gender(update, context):
#     gender = update.message.text
#     context.user_data['gender'] = gender
#     reply_markup = ReplyKeyboardMarkup([
#         [KeyboardButton(text="lokatsiyanngizni ulashing", request_location=True)]
#     ], resize_keyboard=True, one_time_keyboard=True)
#     context.bot.send_message(chat_id=update.effective_user.id, text="lokatsiyanngizni ulashing:", reply_markup=reply_markup)
#     return 'GEOLOCATION'
#
#
# def geolocation(update, context):
#     latitude = update.message.location.latitude
#     longitude = update.message.location.longitude
#     address = get_location_name(latitude, longitude)
#     context.user_data['latitude'] = latitude
#     context.user_data['longitude'] = longitude
#     context.user_data['address'] = address
#
#     conn = sqlite3.connect('users.db')
#     c = conn.cursor()
#     c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?)", (
#         context.user_data['phone_number'],
#         context.user_data['first_name'],
#         context.user_data['last_name'],
#         context.user_data['age'],
#         context.user_data['gender'],
#         context.user_data['address'],
#         context.user_data['latitude'],
#         context.user_data['longitude'],
#     )
#               )
#     conn.commit()
#     conn.close()
#     logging.info("User Registered")
#     update.message.reply_text("Ro'yxatdan o'tganingiz uchun Rahmat!")
#     update.message.reply_text(f"""
#         phone: {context.user_data['phone_number']},
#         first_name: {context.user_data['first_name']},
#         last_name: {context.user_data['last_name']},
#         age: {context.user_data['age']},
#         gender: {context.user_data['gender']},
#         address: {context.user_data['address']},
#         """)
#     return ConversationHandler.END
#
#
# def cancel(update, context):
#     update.message.reply_text(text='Bekor qilindi!')
#     return ConversationHandler.END
#
#
# def main():
#     updater = Updater(token="7563624688:AAE56i_5vW7LGObQ73AcpFSaCt0qPlCHHFc")
#     dispatcher = updater.dispatcher
#
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start)],
#
#         states={
#             'PHONE_NUMBER': [MessageHandler(Filters.contact & ~Filters.command, phone_number)],
#             'FIRST_NAME': [MessageHandler(Filters.text & ~Filters.command, first_name)],
#             'LAST_NAME': [MessageHandler(Filters.text & ~Filters.command, last_name)],
#             'AGE': [MessageHandler(Filters.text & ~Filters.command, age)],
#             'GENDER': [MessageHandler(Filters.text & ~Filters.command, gender)],
#             'GEOLOCATION': [MessageHandler(Filters.location & ~Filters.command, geolocation)],
#
#         },
#         fallbacks=[CommandHandler('cancel', cancel)]
#     )
#     dispatcher.add_handler(conv_handler)
#     updater.start_polling()
#
#
# if __name__ == '__main__':
#     main()


# ==================================================

# ==================================================

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import sqlite3
from typing import Tuple

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# =========================
#  LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("register-bot")

# =========================
#  DB HELPERS
# =========================

DB_PATH = "users.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                phone_number TEXT PRIMARY KEY,
                first_name   TEXT,
                last_name    TEXT,
                age          INTEGER,
                gender       TEXT,
                address      TEXT,
                latitude     REAL,
                longitude    REAL
            );
            """
        )
        conn.commit()


def upsert_user(
    phone_number: str,
    first_name: str,
    last_name: str,
    age: int,
    gender: str,
    address: str,
    latitude: float,
    longitude: float,
) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT OR REPLACE INTO users(
                phone_number, first_name, last_name, age, gender, address, latitude, longitude
            ) VALUES (?,?,?,?,?,?,?,?)
            """,
            (
                phone_number,
                first_name,
                last_name,
                age,
                gender,
                address,
                latitude,
                longitude,
            ),
        )
        conn.commit()


def fetch_all_users():
    """Barcha foydalanuvchilarni qaytaradi."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT phone_number, first_name, last_name, age, gender, address FROM users")
        return c.fetchall()


# =========================
#  STATES
# =========================
PHONE_NUMBER, FIRST_NAME, LAST_NAME, AGE, GENDER, GEOLOCATION = range(6)

# =========================
#  START
# =========================


def start(update: Update, context: CallbackContext) -> int:
    """Boshlash: telefon kontaktini so‘raymiz."""
    kb = [
        [KeyboardButton(text="Telefon kontaktni ulashish", request_contact=True)],
    ]
    update.message.reply_text(
        "Salom! Iltimos, telefon raqamingizni ulashing:",
        reply_markup=ReplyKeyboardMarkup(
            kb, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    log.info("User %s started", update.effective_user.id)
    return PHONE_NUMBER


def phone_number(update: Update, context: CallbackContext) -> int:
    """Telefon raqamni qabul qilamiz (faqat contact orqali)."""
    if not update.message.contact or not update.message.contact.phone_number:
        update.message.reply_text(
            "Kontakt yuborilmadi. Iltimos, pastdagi tugma orqali kontaktni yuboring."
        )
        return PHONE_NUMBER

    context.user_data["phone_number"] = update.message.contact.phone_number
    update.message.reply_text(
        "Rahmat! Ismingiz nima?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return FIRST_NAME


def first_name(update: Update, context: CallbackContext) -> int:
    text = (update.message.text or "").strip()
    if not text:
        update.message.reply_text("Ism bo‘sh bo‘lishi mumkin emas. Qaytadan kiriting.")
        return FIRST_NAME

    context.user_data["first_name"] = text
    update.message.reply_text("Rahmat! Familiyangiz nima?")
    return LAST_NAME


def last_name(update: Update, context: CallbackContext) -> int:
    text = (update.message.text or "").strip()
    if not text:
        update.message.reply_text("Familiya bo‘sh bo‘lishi mumkin emas. Qaytadan kiriting.")
        return LAST_NAME

    context.user_data["last_name"] = text
    update.message.reply_text("Rahmat! Yoshingiz nechida? (faqat raqam)")
    return AGE


def age(update: Update, context: CallbackContext) -> int:
    text = (update.message.text or "").strip()
    if not text.isdigit():
        update.message.reply_text("Iltimos, yoshni faqat raqam bilan kiriting. Masalan: 21")
        return AGE

    context.user_data["age"] = int(text)

    kb = [[KeyboardButton("Erkak"), KeyboardButton("Ayol")]]
    update.message.reply_text(
        "Rahmat! Jinsingizni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            kb, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return GENDER


def gender(update: Update, context: CallbackContext) -> int:
    text = (update.message.text or "").strip().lower()
    if text not in ("erkak", "ayol"):
        update.message.reply_text("Iltimos, faqat 'Erkak' yoki 'Ayol' ni tanlang.")
        return GENDER

    context.user_data["gender"] = "Erkak" if text == "erkak" else "Ayol"

    kb = [[KeyboardButton(text="Lokatsiyani yuborish", request_location=True)]]
    update.message.reply_text(
        "Iltimos, lokatsiyangizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            kb, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return GEOLOCATION


# --- Sizning geo_name.py modulidagi reverse geokodlash funksiyasidan foydalanamiz ---
from geo_name import get_location_name  # get_location_name(lat, lon) -> str


def geolocation(update: Update, context: CallbackContext) -> int:
    if not update.message.location:
        update.message.reply_text("Lokatsiya kelmadi. Iltimos, tugma orqali yuboring.")
        return GEOLOCATION

    lat = float(update.message.location.latitude)
    lon = float(update.message.location.longitude)
    address = get_location_name(lat, lon) or "Manzil aniqlanmadi"

    context.user_data["latitude"] = lat
    context.user_data["longitude"] = lon
    context.user_data["address"] = address

    # DB ga yozamiz (INSERT OR REPLACE)
    upsert_user(
        phone_number=context.user_data["phone_number"],
        first_name=context.user_data["first_name"],
        last_name=context.user_data["last_name"],
        age=context.user_data["age"],
        gender=context.user_data["gender"],
        address=context.user_data["address"],
        latitude=context.user_data["latitude"],
        longitude=context.user_data["longitude"],
    )

    log.info("User %s registered", update.effective_user.id)

    # Yakuniy xabar
    update.message.reply_text(
        "Ro‘yxatdan o‘tganingiz uchun rahmat! Ma’lumotlaringiz saqlandi ✅",
        reply_markup=ReplyKeyboardRemove(),
    )
    update.message.reply_text(
        "📄 Sizning ma’lumotlaringiz:\n"
        f"• Telefon: {context.user_data['phone_number']}\n"
        f"• Ism: {context.user_data['first_name']}\n"
        f"• Familiya: {context.user_data['last_name']}\n"
        f"• Yosh: {context.user_data['age']}\n"
        f"• Jins: {context.user_data['gender']}\n"
        f"• Manzil: {context.user_data['address']}\n"
        f"• Lat/Lon: {lat}, {lon}"
    )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Bekor qilindi!", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


# =========================
#  ADMIN FUNKSIYASI
# =========================

ADMIN_USER_ID = 1577699984  # o‘z Telegram ID'ingizni qo‘ying


def users(update: Update, context: CallbackContext) -> None:
    """Admin uchun barcha foydalanuvchilar ro‘yxatini chiqaradi."""
    if update.effective_user.id != ADMIN_USER_ID:
        update.message.reply_text("❌ Sizda bu buyruqni ishlatish huquqi yo‘q.")
        return

    all_users = fetch_all_users()
    if not all_users:
        update.message.reply_text("Hali hech kim ro‘yxatdan o‘tmagan.")
        return

    msg = "📋 Barcha foydalanuvchilar:\n\n"
    for i, (phone, fname, lname, age, gender, addr) in enumerate(all_users, start=1):
        msg += (
            f"{i}. 👤 {fname} {lname}\n"
            f"   📱 {phone}\n"
            f"   🎂 {age} yosh\n"
            f"   🚻 {gender}\n"
            f"   📍 {addr}\n\n"
        )

    msg += f"👥 Jami foydalanuvchilar: {len(all_users)} ta"
    update.message.reply_text(msg)


# =========================
#  MAIN
# =========================
def main() -> None:
    init_db()

    token = os.environ.get("TELEGRAM_TOKEN") or "7563624688:AAE56i_5vW7LGObQ73AcpFSaCt0qPlCHHFc"
    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE_NUMBER: [MessageHandler(Filters.contact & ~Filters.command, phone_number)],
            FIRST_NAME: [MessageHandler(Filters.text & ~Filters.command, first_name)],
            LAST_NAME: [MessageHandler(Filters.text & ~Filters.command, last_name)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, age)],
            GENDER: [MessageHandler(Filters.text & ~Filters.command, gender)],
            GEOLOCATION: [MessageHandler(Filters.location & ~Filters.command, geolocation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    dp.add_handler(conv)
    dp.add_handler(CommandHandler("users", users))

    updater.start_polling()
    log.info("Bot polling boshlandi.")
    updater.idle()


if __name__ == "__main__":
    main()





