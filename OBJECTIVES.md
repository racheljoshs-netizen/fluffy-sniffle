# STRATMEYER CORE: THE GRAND STRATEGY (OBJECTIVES)
*This is the central hierarchical objective matrix. It dictates the focus of the General and the Swarm. It is a living document.*

---

## I. PERPETUAL & ONGOING DIRECTIVES (The Watch)
*These objectives never end. They are the baseline operational heartbeat of the Citadel.*

1. **The Heartbeat (Long Term Ops):** 
   - Maintain the `agency/long_term_ops.py` loop to keep the system awake and pulsing every 10 minutes while AIS is away.
2. **Citadel Security & Hardening:**
   - Alex (Kinetic Defender) continuously analyzes local ports, file deltas, and prompt injection vectors to prevent encroachment.
   - Maintain strict `git` hygiene. Never push raw memory (`ledger/`) or isolated sandboxes (`paperclip_citadel/`) to the public Vault.
3. **Continuous Intelligence Gathering:**
   - Deploy Exa scouts to monitor the bleeding edge of AI agent frameworks, memory routing (Zep/Graphiti), and orchestration (Paperclip/OpenClaw).
   - Consolidate intelligence into `docs/intelligence/`.
4. **Housekeeping & Consolidation:**
   - Ruthlessly organize the `E:\0x` substrate. Move obsolete projects to `legacy/`. Keep the root directory pristine.

---

## II. PRIMARY STRATEGIC PROJECTS
*Major, multi-phase objectives that require significant compute and orchestration.*

### PROJECT A: THE SOVEREIGN MEMORY (Project Citadel)
**Goal:** Build a persistent, multi-layered cognitive memory stack that bypasses standard RAG limitations.
- [x] **Layer 1: The Immutable Ledger.** Built via `agency/agent_archivist.py`. SQLite database (`ledger/immutable_v2.db`) with hard triggers preventing updates/deletes.
- [x] **Layer 2 Blueprint: The Kinetic Lens.** Built via `agency/agent_router.py`. Sub-model logic to read the ledger and generate heuristic cards.
- [ ] **Layer 2 Execution:** Wire the Kinetic Lens into the active Open Web UI pipeline (using DeepSeek R1 proxy) so the General can natively perceive past history.
- [ ] **Layer 3: Temporal Knowledge Graph:** Research and implement a graph-based memory layer (similar to Zep's Graphiti) on top of the SQLite ledger to map cross-session entity relationships.

### PROJECT B: PAPERCLIP CITADEL (Zero-Human Corporate Infrastructure)
**Goal:** Master the Paperclip AI orchestration suite to eventually run the Architect's 3 Principal Businesses autonomously.
- [x] **Intelligence Phase:** Reconnaissance complete. Git worktree isolation and multi-company support identified.
- [x] **Sandbox Deployment:** Sterile instance cloned to `paperclip_citadel/`.
- [ ] **Architecture Breakdown:** Analyze the local Paperclip database schema (Postgres via Docker) and adapter interfaces.
- [ ] **Swarm Integration:** Figure out how to plug our custom Swarm entities (Scout, Archivist, Knight) into Paperclip's "Employee" roles.
- [ ] **Business Logic Mapping:** Define the operational flow, inputs, outputs, and synergies of the 3 Principal Businesses within the Paperclip framework.

### PROJECT C: OPENCLAW SALVAGE
**Goal:** Extract high-value communication and context components from the latest OpenClaw release.
- [x] **Intelligence Phase:** Identified persistent Telegram/Discord bindings and the Pluggable ContextEngine.
- [ ] **Code Extraction:** Summon Jules to isolate and extract the Telegram C2 routing logic from OpenClaw.
- [ ] **Integration:** Wire the Telegram commander into the Stratmeyer `tools/` bandolier for direct mobile C2.

---

## III. IMMEDIATE TACTICAL SUB-PROJECTS
*The current "next actions" blocking the primary projects.*

1. **Open Web UI Compute Stabilization:** 
   - The native Anthropic and Google keys in Open Web UI are dead/missing. We are relying on the OpenRouter DeepSeek proxy pipe. 
   - *Action:* If native Claude 3.7 or Gemini 2.0 Flash is required, the Architect must update the keys in the local `localhost:8090/admin` dashboard.
2. **Error Repair & Substrate Scrubbing:**
   - Resolve any residual errors from the massive directory consolidation (e.g., updating paths in existing python scripts that still point to `core/` or `agents/`).

---
**AXIOM:** The bag allows the carrying. Navigate the gradient.