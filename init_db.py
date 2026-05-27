from chat_db import init_chat_messages_table
from database import engine
from models import Base
from user_db import init_users_table

Base.metadata.create_all(bind=engine)
init_users_table()
init_chat_messages_table()

print("数据库表创建成功")