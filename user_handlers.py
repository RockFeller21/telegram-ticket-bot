from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from db import Database
from keyboards import main_menu, back_button, appeals_list, appeal_dialog_kb, back_to_menu_kb
from config import ADMIN_ID

db = Database()
router = Router()

class AppealStates(StatesGroup):
    waiting_text = State()
    waiting_message = State()

@router.message(F.text == "/start")
async def start_cmd(msg: Message):
    await msg.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu(msg.from_user.id))

@router.callback_query(F.data == "create_appeal")
async def create_appeal_start(call: CallbackQuery, state: FSMContext):
    appeals = await db.get_active_appeals(call.from_user.id)
    if len(appeals) >= 2:
        await call.answer("Вы не можете создать больше 2 активных обращений.", show_alert=True)
        return
    await call.message.edit_text("Напишите текст обращения.", reply_markup=back_button())
    await state.set_state(AppealStates.waiting_text)

@router.callback_query(F.data == "cancel_create")
async def cancel_create(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Создание обращения отменено.", reply_markup=main_menu(call.from_user.id))
    await state.clear()

@router.message(AppealStates.waiting_text)
async def create_appeal_text(msg: Message, state: FSMContext, bot):
    appeal_id = await db.create_appeal(msg.from_user.id, msg.text)
    await bot.send_message(ADMIN_ID, f"Поступило новое обращение от пользователя {msg.from_user.id} (ID обращения: {appeal_id})")
    await msg.answer("Обращение создано!", reply_markup=main_menu(msg.from_user.id))
    await state.clear()

@router.callback_query(F.data == "my_appeals")
async def my_appeals(call: CallbackQuery):
    appeals = await db.get_active_appeals(call.from_user.id)
    if not appeals:
        await call.message.edit_text("У вас нет активных обращений.", reply_markup=main_menu(call.from_user.id))
        return
    await call.message.edit_text("Ваши обращения:", reply_markup=appeals_list(appeals))

@router.callback_query(F.data == "history")
async def history(call: CallbackQuery):
    appeals = await db.get_closed_appeals(call.from_user.id)
    if not appeals:
        await call.message.edit_text("История пуста.", reply_markup=main_menu(call.from_user.id))
        return
    await call.message.edit_text("История обращений:", reply_markup=appeals_list(appeals))

def format_dialog(messages):
    lines = []
    for m in messages:
        sender = "👤 Вы" if m[2] == "user" else "👨‍💼 Админ"
        date = m[5][:16].replace("T", " ") if len(m) > 5 else ""
        lines.append(f"<b>{sender}</b> <i>{date}</i>\n{m[3]}\n")
    return "\n".join(lines)

@router.callback_query(F.data.regexp(r"^appeal_(\d+)$"))
async def show_appeal(call: CallbackQuery, state: FSMContext):
    appeal_id = int(call.data.split("_")[1])
    appeal = await db.get_appeal(appeal_id)
    is_active = appeal[3] == "active"
    messages = await db.get_messages(appeal_id)
    if not messages:
        await call.message.edit_text("Диалог пуст.", reply_markup=main_menu(call.from_user.id))
        return
    text = "<b>Диалог обращения:</b>\n\n" + format_dialog(messages)
    await call.message.edit_text(
        text,
        reply_markup=appeal_dialog_kb(appeal_id, is_active),
        parse_mode="HTML"
    )
    await state.update_data(current_appeal_id=appeal_id)

@router.callback_query(F.data.regexp(r"^appeal_write_(\d+)$"))
async def appeal_write(call: CallbackQuery, state: FSMContext):
    appeal_id = int(call.data.split("_")[-1])
    await call.message.edit_text(
        "Введите ваше сообщение для администратора:",
        reply_markup=back_to_menu_kb()
    )
    await state.set_state(AppealStates.waiting_message)
    await state.update_data(current_appeal_id=appeal_id)

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_menu(call.from_user.id)
    )
    await state.clear()

@router.message(AppealStates.waiting_message)
async def send_appeal_message(msg: Message, state: FSMContext, bot):
    data = await state.get_data()
    appeal_id = data.get("current_appeal_id")
    await db.add_message(appeal_id, "user", msg.text)
    await bot.send_message(ADMIN_ID, f"Новое сообщение в обращении #{appeal_id} от пользователя {msg.from_user.id}")
    appeal = await db.get_appeal(appeal_id)
    is_active = appeal[3] == "active"
    messages = await db.get_messages(appeal_id)
    text = "<b>Диалог обращения:</b>\n\n" + format_dialog(messages)
    await msg.answer(
        text,
        reply_markup=appeal_dialog_kb(appeal_id, is_active),
        parse_mode="HTML"
    )
    await state.clear()