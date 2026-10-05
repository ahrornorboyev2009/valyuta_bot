import aiohttp
from typing import Optional

CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


async def get_currencies():
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(CBU_URL) as response:
            response.raise_for_status()
            return await response.json()


async def get_currency(code: str) -> Optional[dict]:
    currencies = await get_currencies()

    code = code.upper()

    for currency in currencies:
        if currency.get("Ccy") == code:
            return currency

    return None


def format_number(number: float) -> str:
    return f"{number:,.2f}".replace(",", " ")


async def get_usd_message() -> str:
    usd = await get_currency("USD")

    if not usd:
        return "❌ USD kursini olishda xatolik yuz berdi."

    rate = float(usd["Rate"])
    nominal = int(usd["Nominal"])
    diff = float(usd["Diff"])
    date = usd["Date"]

    if nominal == 1:
        rate_text = format_number(rate)
        nominal_text = "1 USD"
    else:
        rate_text = format_number(rate / nominal)
        nominal_text = f"{nominal} USD"

    if diff > 0:
        diff_text = f"🟢 +{format_number(diff)} so'm"
    elif diff < 0:
        diff_text = f"🔴 {format_number(diff)} so'm"
    else:
        diff_text = "⚪ 0.00 so'm"

    return (
        "🇺🇸 <b>USD — AQSH dollari</b>\n\n"
        f"💵 <b>{nominal_text} = {rate_text} UZS</b>\n"
        f"📊 O'zgarish: {diff_text}\n"
        f"📅 Sana: <b>{date}</b>\n\n"
        "🏦 Manba: O'zbekiston Respublikasi Markaziy banki"
    )


async def get_currency_message(code: str) -> str:
    currency = await get_currency(code)

    if not currency:
        return f"❌ {code} kursi topilmadi."

    rate = float(currency["Rate"])
    nominal = int(currency["Nominal"])
    diff = float(currency["Diff"])
    date = currency["Date"]

    one_unit_rate = rate / nominal

    if diff > 0:
        diff_text = f"🟢 +{format_number(diff)} so'm"
    elif diff < 0:
        diff_text = f"🔴 {format_number(diff)} so'm"
    else:
        diff_text = "⚪ 0.00 so'm"

    return (
        f"💱 <b>{currency['Ccy']} — valyuta kursi</b>\n\n"
        f"💰 <b>1 {currency['Ccy']} = "
        f"{format_number(one_unit_rate)} UZS</b>\n"
        f"📊 O'zgarish: {diff_text}\n"
        f"📅 Sana: <b>{date}</b>\n\n"
        "🏦 Manba: O'zbekiston Respublikasi Markaziy banki"
    )
