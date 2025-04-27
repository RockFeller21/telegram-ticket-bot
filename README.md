# Telegram Support Bot

A ready-to-use Telegram bot for handling user appeals, support requests, and feedback.  
All messages and appeals are stored in SQLite.  
Admin receives notifications about new appeals and messages.

Готовый Telegram-бот для обработки обращений пользователей, поддержки и обратной связи.  
Все обращения и сообщения хранятся в базе данных SQLite.  
Администратор получает уведомления о новых обращениях и сообщениях.

---

## 🇬🇧 English

## Features

- Users can create up to 2 active appeals at a time
- Dialog with admin for each appeal (chat history)
- Admin panel for managing and replying to appeals
- All data stored in SQLite (`appeals.db`)
- Customizable texts and buttons

---

## Installation

1. **Clone the repository or download the code archive.**

2. **Install dependencies:**
   ```
   pip install aiogram aiosqlite
   ```

3. **Open `config.py` and fill in your bot token and admin ID:**
   ```python
   API_TOKEN = 'YOUR_BOT_TOKEN'      # Paste your bot token here
   ADMIN_ID = 123456789              # Your Telegram user ID
   ```

4. **Run the bot:**
   ```
   python bot.py
   ```

---

## Usage

- 📝 **Create Appeal** — send a new appeal (max 2 active appeals per user)
- 📂 **My Appeals** — view and continue dialog on active appeals
- 📜 **Appeal History** — view closed appeals
- 🛠 **Admin Panel** — admin can view, reply, and close appeals

All texts and buttons can be changed in `user_handlers.py`, `admin_handlers.py`, and `keyboards.py`.

---

## 🇷🇺 Русский

## Возможности

- Пользователь может иметь не более 2 активных обращений одновременно
- Диалог с администратором по каждому обращению (история переписки)
- Админ-панель для просмотра, ответа и закрытия обращений
- Все данные хранятся в SQLite (`appeals.db`)
- Все тексты и кнопки можно изменить

---

## Установка

1. **Склонируйте репозиторий или скачайте архив с кодом.**

2. **Установите зависимости:**
   ```
   pip install aiogram aiosqlite
   ```

3. **Откройте `config.py` и укажите ваш токен бота и ID администратора:**
   ```python
   API_TOKEN = 'ВАШ_ТОКЕН_БОТА'      # Вставьте сюда токен вашего бота
   ADMIN_ID = 123456789              # Ваш Telegram user ID
   ```

4. **Запустите бота:**
   ```
   python bot.py
   ```

---

## Использование

- 📝 **Создать обращение** — отправить новое обращение (максимум 2 активных обращения)
- 📂 **Мои обращения** — посмотреть и продолжить диалог по активным обращениям
- 📜 **История обращений** — посмотреть закрытые обращения
- 🛠 **Админ-панель** — админ может просматривать, отвечать и закрывать обращения

Все тексты и кнопки можно изменить в файлах `user_handlers.py`, `admin_handlers.py`, `keyboards.py`.

---

## Лицензия

MIT
