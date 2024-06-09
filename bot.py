import asyncio
from pyrogram import Client, filters
from pyrogram.errors import BotBlocked, UserDeactivated
from sqlalchemy.orm import Session
from database import SessionLocal, User, StatusEnum
from datetime import datetime, timedelta

api_id = "your_api_id"
api_hash = "your_api_hash"
bot_token = "your_bot_token"

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


def get_user(session, user_id):
    return session.query(User).filter(User.id == user_id).first()


def create_user(session, user_id):
    db_user = User(id=user_id)
    session.add(db_user)
    session.commit()
    return db_user


def update_user_status(session, user, status):
    user.status = status
    user.status_updated_at = datetime.utcnow()
    session.commit()


@app.on_message(filters.private)
async def handle_message(client, message):
    user_id = message.from_user.id
    session = SessionLocal()
    user = get_user(session, user_id)

    if not user:
        user = create_user(session, user_id)
        asyncio.create_task(schedule_messages(client, user_id))
    else:
        # Проверка триггера на отмену
        if "Триггер1" in message.text:
            update_user_status(session, user, StatusEnum.dead)

        # Проверка на слова "прекрасно" или "ожидать"
        if any(word in message.text.lower() for word in ["прекрасно", "ожидать"]):
            update_user_status(session, user, StatusEnum.finished)

    session.close()


async def schedule_messages(client, user_id):
    session = SessionLocal()
    user = get_user(session, user_id)

    msg_1_time = timedelta(minutes=6)
    msg_2_time = timedelta(minutes=39)
    msg_3_time = timedelta(days=1, hours=2)

    try:
        await asyncio.sleep(msg_1_time.total_seconds())
        user = get_user(session, user_id)
        if user.status != StatusEnum.alive:
            return
        await client.send_message(user_id, "Текст1")
        user.msg_1_sent_at = datetime.utcnow()
        session.commit()

        await asyncio.sleep((msg_2_time - msg_1_time).total_seconds())
        user = get_user(session, user_id)
        if user.status != StatusEnum.alive:
            return
        await client.send_message(user_id, "Текст2")
        user.msg_2_sent_at = datetime.utcnow()
        session.commit()

        await asyncio.sleep((msg_3_time - msg_2_time).total_seconds())
        user = get_user(session, user_id)
        if user.status != StatusEnum.alive:
            return
        await client.send_message(user_id, "Текст3")
        user.msg_3_sent_at = datetime.utcnow()
        session.commit()

        update_user_status(session, user, StatusEnum.finished)
    except (BotBlocked, UserDeactivated):
        update_user_status(session, user, StatusEnum.dead)
    finally:
        session.close()


app.run()
