import asyncio
import json
import logging
from typing import Any, Dict

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, PreCheckoutQuery

from bot.service.generate_song import generate_song
from bot.dto.song.generate import SongSunoDTO
from bot.infrastructure.database.use_cases.add_song import add_songs
from bot.infrastructure.database.use_cases.promo import redeem_promocode_bonus
from bot.service.cache import get_temp_song, remove_temp_song
from bot.utils.enums import TelegramStarsPaymentStatus, UpdateSong
from ..filters import AdminFilter


logger = logging.getLogger(__name__)

router = Router()


@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    logger.info("Received stars pre-checkout query: %s", query.id)
    await query.answer(True)


def _parse_payload(payload: str | None) -> Dict[str, Any]:
    if not payload:
        return {}
    try:
        data = json.loads(payload)
        if isinstance(data, dict):
            return data
    except (TypeError, ValueError):
        logger.warning("Failed to parse stars payment payload: %s", payload)
    return {}


@router.pre_checkout_query()
async def handle_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message, db_container, cache, dialog_bg_factory):
    successful_payment = message.successful_payment
    logger.info(
        "Stars payment succeeded: user=%s provider_charge=%s telegram_charge=%s",
        message.from_user.id,
        successful_payment.provider_payment_charge_id,
        successful_payment.telegram_payment_charge_id,
    )
    payload_data = _parse_payload(successful_payment.invoice_payload)

    payment_id = payload_data.get("payment_id")
    product_id = payload_data.get("product_id")

    payment = await db_container.telegram_stars_payment.get(payment_id) if payment_id else None
    if payment:
        if product_id is None and payment.meta:
            product_id = payment.meta.get("product_id")
        payment.invoice_payload = successful_payment.invoice_payload
        payment.currency = successful_payment.currency
        payment.amount = successful_payment.total_amount
        payment.status = TelegramStarsPaymentStatus.SUCCEEDED
        payment.provider_payment_charge_id = successful_payment.provider_payment_charge_id
        payment.telegram_payment_charge_id = successful_payment.telegram_payment_charge_id
        meta = payment.meta or {}
        meta.update(payload_data)
        meta["successful_payment"] = successful_payment.model_dump()
        payment.meta = meta
    else:
        payment = await db_container.telegram_stars_payment.create(
            telegram_id=message.from_user.id,
            invoice_payload=successful_payment.invoice_payload,
            currency=successful_payment.currency,
            amount=successful_payment.total_amount,
            status=TelegramStarsPaymentStatus.SUCCEEDED,
            provider_payment_charge_id=successful_payment.provider_payment_charge_id,
            telegram_payment_charge_id=successful_payment.telegram_payment_charge_id,
            meta={"product_id": product_id, "successful_payment": successful_payment.model_dump()},
        )

    if product_id is None:
        await db_container.session.commit()
        await message.answer(
            "Спасибо за оплату! Мы получили платеж, но не смогли определить товар. Свяжитесь с поддержкой, пожалуйста."
        )
        return

    product = await db_container.product.get(product_id)
    if not product:
        await db_container.session.commit()
        logger.warning("Product %s not found for stars payment %s", product_id, payment_id)
        await message.answer("Платеж получен, но товар не найден. Напишите, пожалуйста, в поддержку.")
        return

    await add_songs(db_container, message.from_user.id, product.count_songs, reason=UpdateSong.BUY)
    await redeem_promocode_bonus(db_container, message.from_user.id)
    await db_container.session.commit()

    user = await db_container.user_service.user_repo.get(message.from_user.id)
    await message.answer("Спасибо за оплату! 🎉")
    await message.answer(
        f"Твой баланс песен обновлен: {user.aviable_songs}",
        message_effect_id="5104841245755180586",
    )

    song = await get_temp_song(cache, message.from_user.id)
    if song:
        logger.info("Found cached song for user %s after stars payment", message.from_user.id)
        song = json.loads(song)
        song = SongSunoDTO(
            title_song=song.get("title_song"),
            style_song=song.get("style_song"),
            text_song=song.get("text_song"),
            gender_voice=song.get("gender_voice"),
        )
        
        await generate_song(
            dialog_bg_factory,
            message.from_user.id,
            message.bot,
            song,
            db_container,
            cache,
        )
        await remove_temp_song(cache, message.from_user.id)
    else:
        logger.info("No cached song found for user %s after stars payment", message.from_user.id)


@router.message(Command("refund"), AdminFilter())
async def cmd_refund(message: Message, bot: Bot, command: CommandObject, db_container):
    transaction_id = (command.args or "").strip()
    if not transaction_id:
        await message.answer(text="Не указан ID транзакции")
        return

    logger.info(
        "Refund command received: user=%s transaction_id=%s", message.from_user.id, transaction_id
    )

    payments = await db_container.telegram_stars_payment.get_all(
        telegram_payment_charge_id=transaction_id,
        telegram_id=message.from_user.id,
    )
    payment = payments[0] if payments else None

    if not payment:
        await message.answer("Платеж не найден")
        return

    if payment.status != TelegramStarsPaymentStatus.SUCCEEDED:
        await message.answer("Этот платеж не был успешно завершен и не может быть возвращен")
        return

    product_id = None
    if payment.meta:
        product_id = payment.meta.get("product_id")

    if product_id is None:
        await message.answer("Для этого платежа не удалось определить товар")
        return

    product = await db_container.product.get(product_id)
    if not product:
        await message.answer("Товар, оплаченный в этой транзакции, не найден")
        return

    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id,
        )
    except TelegramBadRequest as e:
        error_text = "Не удалось вернуть платеж"
        if "CHARGE_ALREADY_REFUNDED" in e.message:
            error_text = "Этот платеж уже был возвращен"
        await message.answer(error_text)
        return

    await add_songs(db_container, message.from_user.id, -product.count_songs, reason=UpdateSong.REFUND)
    payment.status = TelegramStarsPaymentStatus.FAILED
    await db_container.session.commit()

    logger.info(
        "Refund completed: user=%s transaction_id=%s product_id=%s",
        message.from_user.id,
        transaction_id,
        product_id,
    )

    user = await db_container.user_service.user_repo.get(message.from_user.id)
    await message.answer("Успешно выполнен возврат")
    await message.answer(f"Ваш текущий баланс песен: {user.aviable_songs}")