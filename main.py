import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
import time

from config import API_TOKEN, ADMIN_ID
from db import init_db, add_mailing, get_mailings, update_last_sent
from keyboards import admin_main_kb, back_to_menu_kb
from utils import check_bot_admin
from mailing_manage import router as mailing_router

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class MailingState(StatesGroup):
    text = State()
    interval = State()
    channel = State()

@dp.message(Command("start"))
async def admin_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 <b>Нет доступа.</b>", parse_mode="HTML")
        return
    await message.answer(
        "<b>👋 Добро пожаловать в админ-панель рассылок!</b>\n\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "<b>👋 Добро пожаловать в админ-панель рассылок!</b>\n\n"
        "Выберите действие с помощью кнопок ниже:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "create_mailing")
async def create_mailing_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return
    await callback.message.answer(
        "✍️ <b>Напишите текст рассылки:</b>",
        parse_mode="HTML",
        reply_markup=back_to_menu_kb()
    )
    await state.set_state(MailingState.text)
    await callback.answer()

@dp.message(MailingState.text)
async def mailing_text(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(text=message.text)
    await message.answer(
        "⏱ <b>С каким интервалом отправлять сообщение?</b>\n"
        "Пожалуйста, введите целое число секунд (например, 60, 300, 1800).",
        parse_mode="HTML",
        reply_markup=back_to_menu_kb()
    )
    await state.set_state(MailingState.interval)

@dp.message(MailingState.interval)
async def mailing_interval(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        interval = int(message.text)
        if interval < 1:
            raise ValueError
        await state.update_data(interval=interval)
        await message.answer(
            "📢 <b>Укажите ID канала</b> (например, <code>-1001234567890</code>):",
            parse_mode="HTML",
            reply_markup=back_to_menu_kb()
        )
        await state.set_state(MailingState.channel)
    except ValueError:
        await message.answer(
            "❗️ <b>Ошибка:</b> Пожалуйста, введите целое число секунд (например, 60, 300, 1800).\n"
            "Операция отменена. Вы вернулись в главное меню.",
            parse_mode="HTML",
            reply_markup=admin_main_kb()
        )
        await state.clear()

@dp.message(MailingState.channel)
async def mailing_channel(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        channel_id = int(message.text)
    except ValueError:
        await message.answer(
            "❗️ <b>Ошибка:</b> ID должен быть числом!\nОперация отменена.",
            parse_mode="HTML",
            reply_markup=admin_main_kb()
        )
        await state.clear()
        return

    try:
        test_msg = await bot.send_message(channel_id, "🤖 Проверка прав бота. Это сообщение будет удалено.")
        await bot.delete_message(channel_id, test_msg.message_id)
    except Exception as e:
        await message.answer(
            "⚠️ <b>Бот не может отправить сообщение в этот канал!</b>\n"
            "Проверьте, что бот добавлен в канал и обладает правами администратора.",
            parse_mode="HTML",
            reply_markup=admin_main_kb()
        )
        await state.clear()
        return

    data = await state.get_data()
    await add_mailing(data['text'], data['interval'], channel_id)
    await message.answer(
        "✅ <b>Рассылка успешно создана!</b> 🎉\n\n"
        "Вы можете управлять рассылками через меню.",
        reply_markup=admin_main_kb(),
        parse_mode="HTML"
    )
    await state.clear()

async def mailing_worker():
    while True:
        mailings = await get_mailings()
        now = time.time()
        for m in mailings:
            mailing_id = m[0]
            text = m[1]
            interval = m[2]
            channel_id = m[3]
            enabled = m[4]
            last_sent = m[5] if len(m) > 5 else 0

            if not enabled:
                continue

            if now - (last_sent or 0) >= interval:
                try:
                    await bot.send_message(channel_id, text)
                    await update_last_sent(mailing_id, now)
                except Exception as e:
                    print(f"Ошибка отправки в канал {channel_id}: {e}")

        await asyncio.sleep(2)

async def main():
    await init_db()
    dp.include_router(mailing_router)
    asyncio.create_task(mailing_worker())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())