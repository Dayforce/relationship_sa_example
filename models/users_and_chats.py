from typing import Optional
from sqlalchemy import Table, Integer, ForeignKey, Column, BigInteger, String, insert, select, update
from sqlalchemy.orm import relationship, selectinload, backref
from database import create_db_session
from models.chat_stat import ChatStat
from models.admin import Admin
from db_base import Base

users_and_chats = Table(
    'users_and_chats', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('chat_id', Integer, ForeignKey('chats.id')),
)


class Chat(Base):
    __tablename__ = "chats"
    id = Column(BigInteger, primary_key=True, index=True)
    chat_stat_id = Column(Integer, ForeignKey('chat_stats.id'))
    telegram_id = Column(BigInteger, unique=True)
    title = Column(String(64))

    # Relationship many-to-many
    users = relationship(
        'User', secondary=users_and_chats,
        back_populates='chats', lazy=True
    )

    # Relationship one to many
    admins = relationship('Admin', back_populates='chat', lazy=True)

    # Relationship one-to-one
    chat_stat = relationship('ChatStat', backref=backref('chat', uselist=False))

    @classmethod
    async def add_chat(cls, telegram_id: int, title: str) -> 'Chat':
        session = await create_db_session()
        async with session() as db_session:
            sql = insert(cls).values(telegram_id=telegram_id,
                                     title=title,
                                     ).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    @classmethod
    async def get_chat(cls, chat_id: int) -> Optional['Chat']:
        db_session = await create_db_session()
        async with db_session() as db_session:
            sql = select(cls).where(cls.telegram_id == chat_id).options(selectinload(Chat.users),
                                                                        selectinload(Chat.chat_stat),
                                                                        selectinload(Chat.admins))
            request = await db_session.execute(sql)
            chat: cls = request.scalar_one_or_none()
        return chat

    async def update_chat_stat(self, chat_stat: ChatStat):
        db_session = await create_db_session()
        async with db_session() as db_session:
            chat = await Chat.get_chat(chat_id=self.telegram_id)
            chat.chat_stat = chat_stat
            db_session.add(chat)
            await db_session.commit()

    async def add_chat_admin(self, admin: Admin):
        db_session = await create_db_session()
        async with db_session() as db_session:
            chat = await Chat.get_chat(chat_id=self.telegram_id)
            chat.admins.append(admin)
            await db_session.commit()


    def __repr__(self):
        return f'{self.telegram_id}'


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String(64))

    # Relationship many-to-many
    chats = relationship(
        'Chat', secondary=users_and_chats,
        back_populates='users', lazy=True
    )

    @classmethod
    async def add_user(cls,
                       telegram_id: int,
                       username: str,
                       chat_id: int
                       ) -> 'User':
        session = await create_db_session()
        async with session() as db_session:
            sql = insert(cls).values(telegram_id=telegram_id,
                                     username=username,
                                     ).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            user = await User.get_user_by_id(user_id=telegram_id)
            chat = await Chat.get_chat(chat_id=chat_id)
            chat.users.append(user)

            db_session.add(chat)
            await db_session.execute(users_and_chats.insert().values(
                user_id=user.id, chat_id=chat.id))

            await db_session.commit()
            return user

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> Optional['User']:
        db_session = await create_db_session()
        async with db_session() as db_session:
            sql = select(cls).where(cls.telegram_id == user_id).options(selectinload(User.chats))
            request = await db_session.execute(sql)
            chat: cls = request.scalar_one_or_none()
        return chat

    def __repr__(self):
        return f'{self.telegram_id}'
