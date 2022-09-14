from typing import Optional
from sqlalchemy import Column, BigInteger, String, insert, select, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database import create_db_session
from db_base import Base


class Admin(Base):
    __tablename__ = "admins"
    id = Column(BigInteger, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String(64))
    chat = relationship('Chat', back_populates='admins', lazy=True)

    @classmethod
    async def add_admin(cls,
                        telegram_id: int,
                        chat_id: int,
                        username: str,
                        ) -> 'Admin':
        session = await create_db_session()
        async with session() as db_session:
            sql = insert(cls).values(telegram_id=telegram_id,
                                     chat_id=chat_id,
                                     username=username,
                                     ).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    @classmethod
    async def get_admin(cls, user_id: int) -> Optional['Admin']:
        db_session = await create_db_session()
        async with db_session() as db_session:
            sql = select(cls).where(cls.telegram_id == user_id)
            request = await db_session.execute(sql)
            admin: cls = request.scalar_one_or_none()
        return admin

    def __repr__(self):
        return f'{self.telegram_id}'
