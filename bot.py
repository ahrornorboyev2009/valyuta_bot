import asyncio
import logging
import os

from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from keyboards import main_keyboard
from cbu import (
    get_usd_message,
    get_currency_message,
    get_currencies,
    format_number,
)


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================
# Telegram bot handlers
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message):
    text = (
        "👋 <b>Valyuta botiga xush kelibsiz!</b>\n\n"
        "🏦 Kurslar O'zbekiston Respublikasi Markaziy bankining "
        "rasmiy ma'lumotlaridan olinadi.\n\n"
        "Kerakli valyutani tanlang:"
    )

    await message.answer(
        text,
        reply_markup=main_keyboard()
    )


@dp.message(F.text == "💵 Dollar")
async def dollar_handler(message: Message):
    try:
        text = await get_usd_message()
        await message.answer(text)
    except Exception:
        logging.exception("USD kursini olishda xatolik")
        await message.answer(
            "❌ Markaziy bank serveridan kursni olishning iloji bo'lmadi.\n"
            "Iltimos, birozdan keyin qayta urinib ko'ring."
        )


@dp.message(F.text == "💶 Yevro")
async def euro_handler(message: Message):
    try:
        await message.answer(await get_currency_message("EUR"))
    except Exception:
        logging.exception("EUR kursini olishda xatolik")
        await message.answer("❌ Kursni olishda xatolik yuz berdi.")


@dp.message(F.text == "🇷🇺 Rubl")
async def rub_handler(message: Message):
    try:
        await message.answer(await get_currency_message("RUB"))
    except Exception:
        logging.exception("RUB kursini olishda xatolik")
        await message.answer("❌ Kursni olishda xatolik yuz berdi.")


@dp.message(F.text == "🇬🇧 Funt")
async def gbp_handler(message: Message):
    try:
        await message.answer(await get_currency_message("GBP"))
    except Exception:
        logging.exception("GBP kursini olishda xatolik")
        await message.answer("❌ Kursni olishda xatolik yuz berdi.")


@dp.message(F.text == "🇨🇳 Yuan")
async def cny_handler(message: Message):
    try:
        await message.answer(await get_currency_message("CNY"))
    except Exception:
        logging.exception("CNY kursini olishda xatolik")
        await message.answer("❌ Kursni olishda xatolik yuz berdi.")


@dp.message(F.text == "📊 Barcha kurslar")
async def all_currencies_handler(message: Message):
    try:
        currencies = await get_currencies()

        important = [
            ("USD", "🇺🇸"),
            ("EUR", "🇪🇺"),
            ("RUB", "🇷🇺"),
            ("GBP", "🇬🇧"),
            ("CNY", "🇨🇳"),
            ("JPY", "🇯🇵"),
            ("CHF", "🇨🇭"),
        ]

        result = "📊 <b>Bugungi valyuta kurslari</b>\n\n"

        for code, flag in important:
            currency = next(
                (item for item in currencies if item.get("Ccy") == code),
                None
            )

            if not currency:
                continue

            rate = float(currency["Rate"])
            nominal = int(currency["Nominal"])
            one_unit = rate / nominal

            result += (
                f"{flag} <b>{code}</b>: "
                f"{format_number(one_unit)} UZS\n"
            )

        date = currencies[0]["Date"] if currencies else "-"

        result += (
            f"\n📅 Sana: <b>{date}</b>\n"
            "🏦 Manba: O'zbekiston Respublikasi Markaziy banki"
        )

        await message.answer(result)

    except Exception:
        logging.exception("Barcha kurslarni olishda xatolik")
        await message.answer(
            "❌ Kurslarni olishda xatolik yuz berdi."
        )


@dp.message()
async def unknown_handler(message: Message):
    await message.answer(
        "Iltimos, menyudagi tugmalardan birini tanlang.",
        reply_markup=main_keyboard()
    )


# =========================
# AIOHTTP SERVER
# =========================

async def health_check(request):
    return web.Response(
        text="Valyuta bot is running!"
    )


async def start_web_server():
    app = web.Application()

    # Render health check
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    # Render bergan PORT
    port = int(os.environ.get("PORT", 10000))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=port
    )

    await site.start()

    logging.info(
        f"🌐 AIOHTTP server started on port {port}"
    )

    return runner


# =========================
# MAIN
# =========================

async def main():
    # AIOHTTP serverni ishga tushirish
    await start_web_server()

    logging.info("🤖 Telegram bot polling started...")

    # Telegram bot
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
