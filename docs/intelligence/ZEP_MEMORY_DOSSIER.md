# ZEP & CONTEXT ENGINEERING DOSSIER
**Date:** March 2026
**Target:** State-of-the-Art Memory Architectures

## 1. THE LIMITS OF TRADITIONAL RAG
Recent research (Q1 2026) confirms that simple RAG (vectorizing past interactions and retrieving them) fails for autonomous agents. It suffers from "Context Rot"—diluting attention with noisy, irrelevant historical vectors.

## 2. THE NEW STANDARD: TEMPORAL GRAPHS & SUB-AGENTS
*   **Zep (Graphiti Engine):** The current benchmark leader (beating MemGPT). It does not just store vectors; it builds a "Temporal Knowledge Graph." It maps the relationships between entities across time.
*   **Context Engineering Pillars:** Write, Select, Compress, Isolate. 
*   **Sub-Agent Isolation:** Both Cursor and Claude Code have adopted the "Orchestrator-Worker" pattern. A Lead Agent (G-Prime) delegates to Sub-Agents that run in *completely isolated context windows*. They do not inherit the Lead's messy log; they start clean, execute, and return only the synthesized result.

## 3. APPLICATION TO THE CITADEL
*   Our `Kinetic Lens` blueprint perfectly matches the "Compress & Isolate" pillar. The worker agent (DeepSeek) reads the raw ledger and returns only a compressed heuristic card to G-Prime.
*   Next Evolution: We must explore implementing a Temporal Knowledge Graph (like Zep's Graphiti) over our SQLite Immutable Ledger to map relationships between the people, projects, and entities we encounter.