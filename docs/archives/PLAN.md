# STRATMEYER CORE: SCAVENGE & BUILD PLAN (v2.0)

**Objective:** Port high-value logic from OpenClaw (TS) to Stratmeyer Core (Python).
**Status:** IN PROGRESS

## PHASE 1: THE BRAIN (Memory Core)
**Target:** `agency/memory_core.py`
**Source:** `src/memory/` (OpenClaw) + Research (sqlite-vec Python)
**Architecture:**
*   **Storage:** SQLite with `sqlite-vec` (Vectors) and `fts5` (Text).
*   **Embedding:** Gemini `text-embedding-004` (via `google-genai`).
*   **Hybrid Search:**
    *   Step 1: Vector Search (Top-N).
    *   Step 2: Keyword Search (FTS5).
    *   Step 3: Reciprocal Rank Fusion (RRF) to combine scores.
**Status:** Ready to Build.

## PHASE 2: THE LOOP (Ralph Wiggum)
**Target:** `agency/ralph_loop.py`
**Source:** `src/agents/pi-embedded-runner/run.ts` (OpenClaw)
**Key Logic to Port:**
1.  **Context Guard:** Check token count *before* sending.
2.  **Auth Rotation:**
    *   Pool of keys defined in env (`GEMINI_API_KEYS`).
    *   On 429/403: Rotate key, backoff, retry.
3.  **Auto-Compaction:**
    *   On Context Overflow: Trigger summarization of oldest messages.
    *   Pattern: "Rolling Summary" (Summarize first 50% of history into a single system message).
4.  **Sanitization:** Strip "Refusal" strings from output.

## PHASE 3: THE VOICE (Telegram Commander)
**Target:** `core/telegram_commander.py`
**Source:** `src/telegram/bot.ts` (OpenClaw)
**Logic:**
*   **Thread Isolation:** Map Telegram Topics to Agent Sessions.
*   **Resilient Polling:** Exponential backoff on network drop.
*   **Voice/Image:** Support native attachments.

## EXECUTION ORDER
1.  **Refine Memory Core:** Implement Hybrid Search & FTS5.
2.  **Build Ralph Loop:** Implement the resilient execution engine.
3.  **Upgrade Telegram:** Connect the Loop to the Chat Interface.

**G-PATTERN: EXECUTING.**
