from chat_db import init_chat_messages_table
from user_db import init_users_table

if __name__ == "__main__":
    init_users_table()
    init_chat_messages_table()
    print("users / chat_messages 表创建成功")
