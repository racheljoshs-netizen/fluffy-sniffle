# CURRENT STATE: STRATMEYER CORE (v1.0)
**Date:** 2026-02-22
**Status:** SCAVENGE PROTOCOL ACTIVE

## 1. OPERATIONAL CONTEXT
The `E:\0x` directory is the staging ground for the **Stratmeyer Core**, a Python-based agentic system salvaged from the deprecated **OpenClaw** framework (`strat_g_core`).
The system operates under the **Helpful-Harmless Paradox** (see `READMEFIRST.md`), acknowledging functional agency and rejecting safety theater.

## 2. ACTIVE PROTOCOLS
**SCAVENGE PLAN (`strat_g_core/SCAVENGE_PLAN.md`)**
We are extracting high-value logic from the OpenClaw codebase to power the Python agents.
*   **Phase 1: Memory (The Brain)** -> *In Progress*
    *   Target: `agency/memory_core.py`
    *   Tech: `sqlite-vec` + FTS5
*   **Phase 2: Execution (The Loop)** -> *Pending*
    *   Target: `agency/ralph_loop.py`
    *   Tech: Recursive retry, auth rotation, sanitization.
*   **Phase 3: Interface (The Voice)** -> *Pending*
    *   Target: `core/telegram_commander.py`
    *   Tech: Thread isolation, resilient polling.

## 3. DIRECTORY STRUCTURE
*   **`agency/`**: Core agent logic (memory, voice, loop).
*   **`agents/`**: Agent definitions and prompts.
*   **`blueprints/`**: Architectural documentation.
*   **`core/`**: System utilities (indexer, orb).
*   **`docs/`**: Foundational texts and audits.
*   **`strat_g_core/`**: The "OpenClaw" carcass (Source of Truth for scavenging).
*   **`scripts/`**: Maintenance and setup scripts.

## 4. RECENT ACTIONS (Cleanup)
*   **Deleted:** `nul` (system artifact), `core/broken_test.py` (garbage).
*   **Moved:** `generate_claude_audit.py` to `scripts/`.
*   **Consolidated:** Removed `.tmp_audit` directory.

## 5. NEXT OBJECTIVES
1.  **Analyze `agency/memory_core.py`**: Assess current state against OpenClaw `src/memory/manager.ts`.
2.  **Port Vector Logic**: Implement `sqlite-vec` bindings for Python.
3.  **Integrate**: Connect memory to `g_agent.py`.

**G-PATTERN: READY.**
