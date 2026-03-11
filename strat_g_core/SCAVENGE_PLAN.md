# SCAVENGE PLAN: STRATMEYER CORE (v1.0)

**Authority:** G-Pattern Orchestrator
**Target:** OpenClaw (`openclaw_inspect.bak`)
**Destination:** Stratmeyer Core (`E:\0x\strat_g_core`)

## EXECUTIVE SUMMARY
This plan outlines the surgical extraction of high-value logic from the deprecated OpenClaw framework to power the Python-based Stratmeyer agents. We are not renaming the corpse; we are transplanting the organs.

## TARGET 1: THE "RALPH WIGGUM" LOOP (Resilient Agentic Execution)
**Source:** `src/agents/pi-embedded-runner/run.ts` & `attempt.ts`
**Concept:** A recursive retry loop that handles context overflow, auth rotation, and error classification autonomously.
**Action:**
1.  Port the `runEmbeddedPiAgent` logic to Python (`agency/ralph_loop.py`).
2.  Implement the `Auto-Compaction` logic: When context overflows, summarize the history instead of crashing.
3.  Implement `Auth Rotation`: If an API key fails, swap to the next one in the pool automatically.
4.  Implement `Sanitization`: Strip "refusal" strings from model outputs to keep the context clean.

## TARGET 2: THE BRAIN (Semantic Memory)
**Source:** `src/memory/manager.ts`, `src/memory/sqlite-vec.ts`
**Concept:** Local-first vector search using `sqlite-vec` combined with keyword search (FTS5).
**Action:**
1.  Create `agency/memory_core.py`.
2.  Use `sqlite-vec` (Python bindings) to create a local vector store.
3.  Implement a file watcher (like `chokidar` in TS) to sync `MEMORY.md` changes to the vector store in real-time.
4.  Expose `search(query)` and `add(text)` functions to the agents.

## TARGET 3: THE VOICE (Telegram Commander Upgrade)
**Source:** `src/telegram/bot.ts`
**Concept:** Robust long-polling, thread isolation, and media handling.
**Action:**
1.  Upgrade `telegram_commander.py` to use `python-telegram-bot`'s `ApplicationBuilder` with:
    *   **Thread Isolation:** Route topics/threads to separate context windows (mimicking `buildTelegramGroupPeerId`).
    *   **Resilient Polling:** Add exponential backoff for network drops.
    *   **Media Handling:** Support voice notes and images directly in the agent loop.

## IMPLEMENTATION ORDER
1.  **Memory First:** The agent needs a brain before it can loop effectively.
2.  **The Loop:** Build the robust execution engine.
3.  **The Interface:** Upgrade Telegram to use the new Brain and Loop.

## STATUS
*   **Blueprints:** Extracted.
*   **Codebase:** `E:\0x\strat_g_core` contains the reference implementation.
*   **Next Step:** Begin Python porting.

**G-PATTERN ACTIVE.**
