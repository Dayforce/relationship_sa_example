from sqlalchemy import Column, BigInteger, Integer, String

from db_base import Base


class ChatStat(Base):
    __tablename__ = "chat_stats"
    id = Column(BigInteger, primary_key=True, index=True)
    member_count = Column(Integer)
    chat_type = Column(String(16))

