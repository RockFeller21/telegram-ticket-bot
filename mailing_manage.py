from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from db import get_mailings, update_mailing, delete_mailing, update_last_sent
from keyboards import mailing_manage_kb, back_to_menu_kb
from config import ADMIN_ID
import time

router = Router()

@router.callback_query(F.data == "manage_mailings")
async def manage_mailings_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return
    mailings = await get_mailings()
    if not mailings:
        await callback.message.answer("Нет активных рассылок.", reply_markup=back_to_menu_kb())
        await callback.answer()
        return
    for m in mailings:
        status = "Включена" if m[4] else "Отключена"
        interval_str = f"{int(m[2])} сек."
        await callback.message.answer(
            f"ID: <code>{m[0]}</code>\n"
            f"Текст: <i>{m[1]}</i>\n"
            f"Интервал: <b>{interval_str}</b>\n"
            f"Канал: <code>{m[3]}</code>\n"
            f"Статус: <b>{status}</b>",
            reply_markup=mailing_manage_kb(m[0], m[4]),
            parse_mode="HTML"
        )
    await callback.answer()

@router.callback_query(F.data.startswith("toggle:"))
async def toggle_mailing(call: CallbackQuery):
    mailing_id = int(call.data.split(":")[1])
    mailings = await get_mailings()
    for m in mailings:
        if m[0] == mailing_id:
            new_status = 0 if m[4] else 1
            await update_mailing(mailing_id, enabled=new_status)
            interval_str = f"{int(m[2])} сек."
            await call.answer("Статус изменён!")
            await call.message.edit_text(
                f"ID: <code>{m[0]}</code>\n"
                f"Текст: <i>{m[1]}</i>\n"
                f"Интервал: <b>{interval_str}</b>\n"
                f"Канал: <code>{m[3]}</code>\n"
                f"Статус: <b>{'Включена' if new_status else 'Отключена'}</b>",
                reply_markup=mailing_manage_kb(m[0], new_status),
                parse_mode="HTML"
            )
            return

@router.callback_query(F.data.startswith("delete:"))
async def delete_mailing_cb(call: CallbackQuery):
    mailing_id = int(call.data.split(":")[1])
    await delete_mailing(mailing_id)
    await call.answer("Удалено!")
    await call.message.edit_text("Рассылка удалена.", reply_markup=back_to_menu_kb())

@router.callback_query(F.data.startswith("edit_text:"))
async def edit_text_start(call: CallbackQuery, state: FSMContext):
    mailing_id = int(call.data.split(":")[1])
    await state.update_data(edit_id=mailing_id)
    await call.message.answer("Введите новый текст рассылки:", reply_markup=back_to_menu_kb())
    await state.set_state("edit_text")

@router.message(StateFilter("edit_text"))
async def edit_text_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mailing_id = data.get("edit_id")
    await update_mailing(mailing_id, text=message.text)
    await message.answer("Текст рассылки обновлён.", reply_markup=back_to_menu_kb())
    await state.clear()

@router.callback_query(F.data.startswith("edit_interval:"))
async def edit_interval_start(call: CallbackQuery, state: FSMContext):
    mailing_id = int(call.data.split(":")[1])
    await state.update_data(edit_id=mailing_id)
    await call.message.answer("Введите новый интервал в секундах (например, 60, 300, 1800):", reply_markup=back_to_menu_kb())
    await state.set_state("edit_interval")

@router.message(StateFilter("edit_interval"))
async def edit_interval_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mailing_id = data.get("edit_id")
    try:
        interval = int(message.text)
        if interval < 1:
            raise ValueError
        await update_mailing(mailing_id, interval=interval)
        await update_last_sent(mailing_id, time.time())
        await message.answer(f"Интервал обновлён. Теперь рассылка будет отправляться каждые {interval} секунд.", reply_markup=back_to_menu_kb())
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите целое число секунд (например, 60, 300, 1800).", reply_markup=back_to_menu_kb())

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: types.CallbackQuery):
    from keyboards import admin_main_kb
    await callback.message.edit_text(
        "<b>👋 Добро пожаловать в админ-панель рассылок!</b>\n\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML"
    )
    await callback.answer()