from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import modules.openAI as OAI
import json, tracemalloc, os
tracemalloc.start()
load_dotenv()

bot_token = os.getenv('TELEGRAM_TOKEN')

async def update_user_context(user, role, msg):
    with open('data/history_user.json', encoding='utf-8') as json_file:
        history = json.load(json_file)
    ac_dict = ({"role": role, "content": msg})
    if not isinstance(history, dict):
        history = {}
    if "user" not in history:
        history["user"] = {}
    if str(user) not in history["user"]:
        history["user"][str(user)] = []
    history["user"][str(user)].append(ac_dict)
    with open('data/history_user.json', 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    return history


# commands
## start message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Привет! Я рад, что ты обратился ко мне за помощью. Я готов помочь тебе в решении задач и ответить на твои вопросы. Давай работать вместе и достигать поставленных целей!"
    
    await update.message.reply_html(text)

## help message
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Я - искусственный интеллект, который способен выполнять некоторые задачи и отвечать на вопросы.\nВот некоторые мои команды:\n /start – начать пользоваться ботом;\n /help – просмотр команд;\n /u 'сообщение' – попросить ответ игнорируя контекст."
    
    await update.message.reply_text(text, parse_mode="Markdown")

## message without context
async def you(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message.text[2:].lstrip()
    
    res = await OAI.gpt_try(update.message.from_user.id, msg)
    # res = await Notion.notion_gpt(update.message.from_user.id, msg)
    # await update.message.reply_text(res, parse_mode="Markdown")
    await update.message.reply_text(res, parse_mode="html")

## default messages with context (bot can be restarted)
### unsafe function (temporarily)
async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message.text
    await update_user_context(update.message.from_user.id, "user", msg)
    with open('data/history_user.json', encoding='utf-8') as json_file:
        history = json.load(json_file)
    context = history['user'][str(update.message.from_user.id)]
    context = context[-15:]

    res = await OAI.gpt_try_context(update.message.from_user.id, msg, context)
    await update_user_context(update.message.from_user.id, "assistant", res)
    await update.message.reply_text(res, parse_mode="Markdown")

# main app
def main() -> None:
    app = Application.builder().token(bot_token).build()
    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("u", you))
    
    # messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))
    # Запуск бота
    print("Launch!")
    app.run_polling()

if __name__ == "__main__":
    main()