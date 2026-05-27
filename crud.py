from database import SessionLocal
from models import Message

# 保存消息
def save_message(role, content):

    db = SessionLocal()

    message = Message(
        role=role,
        content=content
    )

    db.add(message)
    db.commit()

    db.close()

# 获取聊天记录
def get_messages():

    db = SessionLocal()

    messages = db.query(Message).all()

    db.close()

    return messages