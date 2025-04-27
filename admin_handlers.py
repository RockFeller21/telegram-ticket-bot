from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from db import Database
from keyboards import admin_appeals_list, admin_dialog_nav, main_menu
from config import ADMIN_ID

db = Database()
router = Router()

class AdminDialogReply(StatesGroup):
    waiting_reply = State()

def format_dialog(messages):
    lines = []
    for m in messages:
        sender = "👤 Пользователь" if m[2] == "user" else "👨‍💼 Админ"
        date = m[5][:16].replace("T", " ") if len(m) > 5 else ""
        lines.append(f"<b>{sender}</b> <i>{date}</i>\n{m[3]}\n")
    return "\n".join(lines)

@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Нет доступа", show_alert=True)
        return
    appeals = await db.get_all_active_appeals()
    if not appeals:
        await call.message.edit_text("Нет активных обращений.", reply_markup=main_menu(call.from_user.id))
        return
    await call.message.edit_text("Список обращений:", reply_markup=admin_appeals_list(appeals))

@router.callback_query(F.data == "back_to_menu")
async def admin_back_to_menu(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_menu(call.from_user.id)
    )
    await state.clear()

@router.callback_query(F.data.startswith("admin_appeal_"))
async def admin_appeal_dialog(call: CallbackQuery, state: FSMContext):
    appeal_id = int(call.data.split("_")[-1])
    appeal = await db.get_appeal(appeal_id)
    is_active = appeal[3] == "active"
    messages = await db.get_messages(appeal_id)
    if not messages:
        await call.message.edit_text("Диалог пуст.", reply_markup=main_menu(call.from_user.id))
        return
    text = "<b>Диалог обращения:</b>\n\n" + format_dialog(messages)
    await call.message.edit_text(
        text,
        reply_markup=admin_dialog_nav(appeal_id, is_active),
        parse_mode="HTML"
    )
    await state.update_data(appeal_id=appeal_id)

@router.callback_query(F.data.regexp(r"^admin_reply_(\d+)$"))
async def admin_reply_btn(call: CallbackQuery, state: FSMContext):
    appeal_id = int(call.data.split("_")[-1])
    await call.message.edit_text("Введите ваш ответ пользователю:")
    await state.set_state(AdminDialogReply.waiting_reply)
    await state.update_data(appeal_id=appeal_id)

@router.message(AdminDialogReply.waiting_reply)
async def admin_send_reply(msg: Message, state: FSMContext, bot):
    data = await state.get_data()
    appeal_id = data.get("appeal_id")
    await db.add_message(appeal_id, "admin", msg.text)
    appeal = await db.get_appeal(appeal_id)
    user_id = appeal[1]
    await bot.send_message(user_id, f"Администратор прислал ответ на ваше обращение #{appeal_id}.")
    await msg.answer("Ответ отправлен.")
    await state.clear()

@router.callback_query(F.data == "admin_panel")
async def back_to_list(call: CallbackQuery, state: FSMContext):
    appeals = await db.get_all_active_appeals()
    await call.message.edit_text("Список обращений:", reply_markup=admin_appeals_list(appeals))
    await state.clear()

@router.callback_query(F.data.regexp(r"^admin_close_(\d+)$"))
async def admin_close_appeal(call: CallbackQuery, state: FSMContext):
    appeal_id = int(call.data.split("_")[-1])
    await db.close_appeal(appeal_id)
    await call.message.edit_text("Обращение закрыто.", reply_markup=main_menu(call.from_user.id))
    await state.clear()