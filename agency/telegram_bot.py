import os
import logging
import asyncio
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from agency.ralph_loop import RalphLoop, AgentConfig
from agency.memory_core import MemoryCore
from agency.open_web_ui import OpenWebUIClient

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWUI_CLIENT = OpenWebUIClient(api_key="sk-dbc2a93237a34ce990db894a1d7cdc57") # From memory

# Logging
logging.basicConfig(
    format='%(asctime)s - [TELEGRAM] - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Global State: ChatID -> RalphLoop Instance
active_agents = {}
memory_core = MemoryCore() # Shared Brain

def get_agent(chat_id: int) -> RalphLoop:
    """Retrieves or creates a RalphLoop for this chat."""
    if chat_id not in active_agents:
        logging.info(f"Spawning new agent for {chat_id}")
        config = AgentConfig(
            system_instruction="You are G, a resilient operational intelligence. Speak directly. Use your memory.",
            model_name="models/gemini-3.1-pro-preview" # COGNITION ENGINE
        )
        active_agents[chat_id] = RalphLoop(config, memory_core=memory_core)
    return active_agents[chat_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""G-NODE ONLINE.
Protocol: Ralph Loop
Memory: Hybrid (Ollama/Gemini)
Agents: Open Web UI Connected
Status: Ready.""")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Commands:
/start - Reboot
/clear - Wipe Context
/summon <agent> <task> - Call Open Web UI
/research <topic> - Delegate Research""")

async def research_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /research <topic>")
        return
    
    await update.message.reply_text(f"📡 Summoning Research Swarm for: '{query}'...")
    
    try:
        # Run in thread to avoid blocking
        resp = await asyncio.to_thread(OWUI_CLIENT.summon_researcher, query)
        
        if "Error" in resp and "Connection refused" in resp:
             await update.message.reply_text("⚠️ Open Web UI is offline. Cannot summon researcher.\nEnsure it is running at localhost:3000.")
        else:
             await update.message.reply_text(f"🔬 RESEARCH REPORT:\n\n{resp}")
             
             # Auto-archive to memory
             if memory_core:
                 doc_path = f"E:/0x/agency/research/{query[:20].replace(' ','_')}.md"
                 os.makedirs(os.path.dirname(doc_path), exist_ok=True)
                 with open(doc_path, "w", encoding="utf-8") as f:
                     f.write(f"# Research: {query}\n\n{resp}")
                 memory_core.add_document(doc_path, f"# Research: {query}\n\n{resp}")
                 await update.message.reply_text("💾 Report archived to Memory Core.")
                 
    except Exception as e:
        await update.message.reply_text(f"❌ Research Request Failed: {e}")

async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_agents:
        del active_agents[chat_id]
    await update.message.reply_text("Memory Context Wiped.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    chat_id = update.effective_chat.id
    agent = get_agent(chat_id)
    
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)
    
    # Run loop in thread (it's synchronous because of google-generativeai blocking calls)
    response = await asyncio.to_thread(agent.run, user_text)
    
    # Split long messages if needed (Telegram limit is 4096)
    if len(response) > 4000:
        for x in range(0, len(response), 4000):
            await update.message.reply_text(response[x:x+4000])
    else:
        await update.message.reply_text(response)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Future: Download file -> Whisper/Gemini Audio -> Text -> Agent
    await update.message.reply_text("Voice received. Processing module pending (Phase 3.1).")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("[CRITICAL] TELEGRAM_BOT_TOKEN not found in env.")
    else:
        print(f"[System] G-Node launching via {TELEGRAM_TOKEN[:5]}...")
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Handlers
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', help_command))
        application.add_handler(CommandHandler('clear', clear_context))
        application.add_handler(CommandHandler('research', research_command))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))
        
        application.run_polling()
