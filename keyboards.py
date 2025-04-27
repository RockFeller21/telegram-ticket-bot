from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID

def main_menu(user_id):
    kb = [
        [InlineKeyboardButton(text="📝 Создать обращение", callback_data="create_appeal")],
        [InlineKeyboardButton(text="📂 Мои обращения", callback_data="my_appeals")],
        [InlineKeyboardButton(text="📜 История обращений", callback_data="history")]
    ]
    if user_id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="🛠 Админ-панель", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data="cancel_create")]
    ])

def appeals_list(appeals, prefix="appeal_"):
    kb = []
    for a in appeals:
        kb.append([
            InlineKeyboardButton(
                text=f"💬 Обращение #{a[0]} | {a[3].capitalize()}",
                callback_data=f"{prefix}{a[0]}"
            )
        ])
    kb.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_dialog_nav(appeal_id, is_active=True):
    kb = []
    row = []
    if is_active:
        row.append(InlineKeyboardButton(text="✉️ Написать сообщение", callback_data=f"admin_reply_{appeal_id}"))
    row.append(InlineKeyboardButton(text="✅ Закрыть обращение", callback_data=f"admin_close_{appeal_id}"))
    kb.append(row)
    kb.append([
        InlineKeyboardButton(text="⬅️ К списку", callback_data="admin_panel"),
        InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_appeals_list(appeals):
    kb = []
    for a in appeals:
        kb.append([
            InlineKeyboardButton(
                text=f"👤 Пользователь {a[1]} | №{a[0]}",
                callback_data=f"admin_appeal_{a[0]}"
            )
        ])
    kb.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def appeal_dialog_kb(appeal_id, is_active=True):
    kb = []
    row = []
    if is_active:
        row.append(InlineKeyboardButton(text="✉️ Написать сообщение", callback_data=f"appeal_write_{appeal_id}"))
    kb.append(row)
    kb.append([
        InlineKeyboardButton(text="⬅️ К списку", callback_data="my_appeals"),
        InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_to_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu")]
    ])

def view_answer_button(appeal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Посмотреть", callback_data=f"appeal_{appeal_id}")]
    ])