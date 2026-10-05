import aiohttp
from typing import Optional


CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


async def get_currencies():
    """Markaziy bankdan barcha valyuta kurslarini olish."""

    timeout = aiohttp.ClientTimeout(total=15)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers=headers
    ) as session:

        async with session.get(CBU_URL) as response:

            if response.status != 200:
                raise Exception(
                    f"Markaziy bank API xatosi: {response.status}"
                )

            data = await response.json()

            if not isinstance(data, list):
                raise Exception(
                    "Markaziy bank noto'g'ri ma'lumot qaytardi."
                )

            return data


async def get_currency(code: str) -> Optional[dict]:
    """Berilgan valyutani topish."""

    currencies = await get_currencies()

    code = code.upper().strip()

    for currency in currencies:
        if currency.get("Ccy") == code:
            return currency

    return None


def format_number(number: float) -> str:
    """Sonni chiroyli formatlash."""

    return f"{number:,.2f}".replace(",", " ")


async def get_usd_message() -> str:
    """USD kursini chiqarish."""

    usd = await get_currency("USD")

    if not usd:
        return "❌ USD kursi topilmadi."

    rate = float(usd["Rate"])
    nominal = int(usd["Nominal"])
    diff = float(usd.get("Diff", 0))
    date = usd["Date"]

    # 1 USD kursi
    one_unit_rate = rate / nominal

    if diff > 0:
        diff_text = f"🟢 +{format_number(diff)} so'm"
    elif diff < 0:
        diff_text = f"🔴 {format_number(diff)} so'm"
    else:
        diff_text = "⚪ 0.00 so'm"

    return (
        "🇺🇸 <b>AQSH dollari (USD)</b>\n\n"
        f"💵 <b>1 USD = {format_number(one_unit_rate)} UZS</b>\n"
        f"📊 O'zgarish: {diff_text}\n"
        f"📅 Kurs sanasi: <b>{date}</b>\n\n"
        "🏦 Manba: O'zbekiston Respublikasi Markaziy banki"
    )


async def get_currency_message(code: str) -> str:
    """Istalgan valyuta kursini chiqarish."""

    currency = await get_currency(code)

    if not currency:
        return f"❌ {code} kursi topilmadi."

    rate = float(currency["Rate"])
    nominal = int(currency["Nominal"])
    diff = float(currency.get("Diff", 0))
    date = currency["Date"]

    # Markaziy bank Rate qiymati Nominal dona uchun.
    # Masalan:
    # 100 RUB = 14 700 UZS
    # 1 RUB = 147 UZS
    one_unit_rate = rate / nominal

    if diff > 0:
        diff_text = f"🟢 +{format_number(diff)} so'm"
    elif diff < 0:
        diff_text = f"🔴 {format_number(diff)} so'm"
    else:
        diff_text = "⚪ 0.00 so'm"

    return (
        f"💱 <b>{currency.get('CcyNm_UZ', code)}</b>\n\n"
        f"💰 <b>1 {code} = "
        f"{format_number(one_unit_rate)} UZS</b>\n"
        f"📊 O'zgarish: {diff_text}\n"
        f"📅 Kurs sanasi: <b>{date}</b>\n\n"
        "🏦 Manba: O'zbekiston Respublikasi Markaziy banki"
    )
