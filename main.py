import asyncio
from database import engine
from db_base import Base
from models.admin import Admin
from models.chat_stat import ChatStat
from models.users_and_chats import Chat, User


async def test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Many-to-many
    chat = await Chat.add_chat(telegram_id=1242141, title="Test")
    await User.add_user(telegram_id=2432, username='test', chat_id=chat.telegram_id)
    user = await User.get_user_by_id(user_id=2432)
    chat = await Chat.get_chat(chat_id=chat.telegram_id)
    print(user.chats[0].title)
    print(chat.users[0].telegram_id)

    # One-to-one
    await chat.update_chat_stat(chat_stat=ChatStat(member_count=5, chat_type='channel'))
    chat = await Chat.get_chat(chat_id=chat.telegram_id)
    print(chat.chat_stat.member_count)

    # One-to-many
    admin = await Admin.add_admin(telegram_id=32, username='admin1', chat_id=chat.id)
    admin = await Admin.get_admin(user_id=admin.telegram_id)
    chat = await Chat.get_chat(chat_id=chat.telegram_id)
    await chat.add_chat_admin(admin=admin)
    print(chat.admins[0].username)
    print(admin.chat.title)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
