from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Создать рассылку", callback_data="create_mailing"),
                InlineKeyboardButton(text="📋 Управление рассылками", callback_data="manage_mailings")
            ]
        ]
    )

def mailing_manage_kb(mailing_id, enabled):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Изменить текст", callback_data=f"edit_text:{mailing_id}"),
                InlineKeyboardButton(text="⏱ Изменить интервал", callback_data=f"edit_interval:{mailing_id}")
            ],
            [
                InlineKeyboardButton(text="📢 Изменить канал", callback_data=f"edit_channel:{mailing_id}")
            ],
            [
                InlineKeyboardButton(text="✅ Вкл" if not enabled else "🚫 Выкл", callback_data=f"toggle:{mailing_id}"),
                InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{mailing_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Вернуться", callback_data="back_to_menu")
            ]
        ]
    )

def back_to_menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Вернуться", callback_data="back_to_menu")]
        ]
    )