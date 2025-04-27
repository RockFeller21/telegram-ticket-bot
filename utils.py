from aiogram import Bot

async def check_bot_admin(bot: Bot, channel_id: int):
    try:
        member = await bot.get_chat_member(channel_id, (await bot.me).id)
        return member.is_chat_admin()
    except Exception:
        return False