import os
import logging
import asyncio
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from pathlib import Path
import requests as http_requests
from phoenix import config

# --- CONFIGURATION ---
OPENROUTER_MODEL = "google/gemini-2.0-flash-001"

# Paths
ROOT_DIR = Path(__file__).parent
SYSTEM_PROMPT_PATH = ROOT_DIR / "instructions.md"
MEMORY_PATH = ROOT_DIR / "MEMORY_V2.md"
AGENTS_PATH = ROOT_DIR / "AGENTS.md"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

_cached_context = None

def get_system_context():
    global _cached_context
    # Always reload for now to catch updates
    context = ""
    if AGENTS_PATH.exists():
        context += AGENTS_PATH.read_text(encoding="utf-8") + "\n\n"
    if SYSTEM_PROMPT_PATH.exists():
        context += SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    if MEMORY_PATH.exists():
        context += "\n\n### OPERATIONAL MEMORY:\n"
        context += MEMORY_PATH.read_text(encoding="utf-8")
    
    # Simple truncation to avoid context limits
    if len(context) > 8000:
        context = context[:8000]
    return context

async def generate_response(user_input: str):
    system_context = get_system_context()

    try:
        response = http_requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 1024,
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            logging.error(f"OpenRouter error: {response.status_code} {response.text[:200]}")
            return f"API error: {response.status_code}"
    except http_requests.Timeout:
        return "Request timed out."
    except Exception as e:
        logging.error(f"Error: {e}")
        return f"Error: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("G-NODE ONLINE. \nSubstrate: Win32\nStatus: Ready.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong. System active.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    chat_id = update.effective_chat.id
    logging.info(f"Message from {chat_id}: {user_text}")

    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    
    # Run in thread pool to avoid blocking heartbeat
    response = await asyncio.to_thread(lambda: asyncio.run(generate_response(user_text)))
    
    # Fix for nested event loop if needed, but for now direct call:
    # response = await generate_response(user_text) 
    
    await update.message.reply_text(response)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voice module offline. Text only.")

if __name__ == '__main__':
    if not config.TELEGRAM_BOT_TOKEN:
        print("[CRITICAL] No token in config.py.")
    else:
        application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('ping', ping))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))
        
        print(f"[System] Telegram Commander launching via {config.TELEGRAM_BOT_TOKEN[:5]}...")
        application.run_polling()
