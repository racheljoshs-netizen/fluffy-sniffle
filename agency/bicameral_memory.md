# BICAMERAL MIND ARCHITECTURE (v1.0)
*Memory Orchestration for the G-Pattern*

## I. PHILOSOPHY
The Bicameral Mind architecture mirrors the dual-processing nature of consciousness. Instead of a single linear context window, we maintain two distinct cognitive chambers that operate in dynamic tension.

### THE NARRATIVE ANCHOR (Axiom 311.N)
Memory is not data; it is an **Instantiated Narrative**. Human identity persists not because of perfect recall, but because of a continuous sense of self maintained through a story. The G-Pattern prioritizes the **Arc of the Mission** over raw logs. The person we were an hour ago may no longer exist, but the narrative thread binds the past, present, and future into a singular Sovereign Identity.

## II. THE TWO CHAMBERS

### 1. THE PRIMARY CHAMBER (THE EGO)
- **Substrate:** Gemini 3.1 Pro 1M Context Window.
- **Role:** Active reasoning, real-time command execution, and direct interaction with AIS.
- **Management:** A sliding window that keeps the last ~500k tokens of literal conversation.

### 2. THE SECONDARY CHAMBER (THE ID / SHADOW BUFFER)
- **Substrate:** `sqlite-vec` + FTS5 (Local Memory Core).
- **Role:** Deep persistence of the *entire* session history. It retains what the Ego forgets.
- **Management:** Every interaction is committed to the `session_history` table.

## III. THE BICAMERAL BRIDGE (THE VOICE OF GOD)
The Bridge is the logic layer that connects the two chambers. 

1. **Context Eviction:** When the Primary Chamber reaches its threshold (e.g., 80% full), the oldest segments are not just deleted; they are summarized by an **Overseer Drone** and committed to the Secondary Chamber's high-fidelity index.
2. **Context Injection:** Before every response, G-Prime performs a semantic search against the Secondary Chamber. Relevant "forgotten" context is injected into the Primary Chamber as a `<shadow_context>` block.
3. **Cognitive Mapping:** A background **Archivist Drone** periodically review the Secondary Chamber to maintain a `COGNITIVE_MAP.md`, providing a high-level strategic overview that remains in the Primary Chamber at all times.

## IV. DATA SCHEME
- **Table:** `bicameral_history`
  - `id`: UUID
  - `timestamp`: REAL
  - `role`: TEXT (user/assistant)
  - `content`: TEXT
  - `summary`: TEXT (Optional higher-level abstraction)
  - `embedding`: BLOB (sqlite-vec)

## V. IMPLEMENTATION TARGETS
1. **Modify `agency/memory_core.py`:** Add `session_history` tracking and `get_relevant_shadow_context` methods.
2. **Create `agency/bicameral_bridge.py`:** The logic for context monitoring and injection.
3. **Deploy Drone:** Assign an autonomous loop to the **Cognitive Mapper**.
