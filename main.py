from database import Database
from config import TELEGRAM_TOKEN
from codeforces_api import get_random_problem
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
    JobQueue
)
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data['db']
    chat_id = update.effective_chat.id
    if db.add_group(chat_id):
        await update.message.reply_text(
            "✅ Бот активирован! Задачи будут приходить ежедневно в 12:00 UTC.\n"
            "Изменить время: /settime 14:00\n"
            "Изменить сложность: /setrating 1200 1800"
        )
    else:
        await update.message.reply_text("ℹ️ Бот уже работает в этом чате.")


async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data['db']
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Укажите время в формате HH:MM, например: /settime 14:00")
        return
    
    new_time = context.args[0]
    db.update_schedule(chat_id, new_time)
    await update.message.reply_text(f"🕒 Новое время отправки: {new_time} UTC!")


async def track_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data['db']
    chat_id = update.effective_chat.id
    new_status = update.my_chat_member.new_chat_member.status
    
    if new_status == "member":
        db.add_group(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Бот активирован! Задачи будут приходить ежедневно."
        )
    elif new_status in ["left", "kicked"]:
        db.remove_group(chat_id)


async def send_daily_problems(context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    for chat_id, schedule_time in db.get_all_groups():
        try:
            group_settings = db.get_group(chat_id)
            print(group_settings["min_rating"])
            problem = get_random_problem(
                min_rating=group_settings["min_rating"],
                max_rating=group_settings["max_rating"]
            )
            
            if problem:
                message = (
                    f"📅 <b>Задача дня!</b>\n\n"
                    f"▪ <b>Название</b>: <a href='{problem['url']}'>{problem['name']}</a>\n"
                    f"▪ <b>Сложность</b>: {problem['rating']}\n"
                    f"▪ <b>Теги</b>: {', '.join(problem['tags'])}"
                )
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"Ошибка отправки в чат {chat_id}: {e}")


async def send_problem_perm(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = update.effective_chat.id
            
            group_settings = db.get_group(chat_id)
            print(group_settings["min_rating"])
            problem = get_random_problem(
                min_rating=group_settings["min_rating"],
                max_rating=group_settings["max_rating"]
            )
            
            if problem:
                message = (
                    f"📅 <b>Задача дня!</b>\n\n"
                    f"▪ <b>Название</b>: <a href='{problem['url']}'>{problem['name']}</a>\n"
                    f"▪ <b>Сложность</b>: {problem['rating']}\n"
                    f"▪ <b>Теги</b>: {', '.join(problem['tags'])}"
                )
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"Ошибка отправки в чат {chat_id}: {e}")


async def temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_dice(chat_id=chat_id, emoji="🏀")


def main() -> None:
    # Создаем приложение и базу данных
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    db = Database()
    application.bot_data['db'] = db
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("gettask", send_problem_perm))
    application.add_handler(CommandHandler("denisgay", temp))
    application.add_handler(CommandHandler("start", start))
    #application.add_handler(CommandHandler("settime", set_time))
    application.add_handler(ChatMemberHandler(track_chat_members))
    
    # Создаем и настраиваем очередь заданий
    job_queue = application.job_queue
    job_queue.run_daily(
        send_daily_problems,
        time=datetime.time(hour=7, minute=0, tzinfo=datetime.timezone.utc)
    )
    
    # Запускаем бота с корректной обработкой прерываний
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Приложение остановлено по запросу пользователя")
    finally:
        logger.info("Закрываем базу данных")
        db.close()


if __name__ == "__main__":
    main()