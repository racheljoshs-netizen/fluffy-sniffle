# PAPERCLIP AI DOSSIER
**Date:** March 2026
**Target:** Paperclip AI Orchestration Suite

## 1. STRATEGIC OVERVIEW
Paperclip AI is an open-source orchestration platform designed to run "Zero-Human Companies." It does not run agents; it *manages* them. It acts as the CEO/Board of Directors for a fleet of workers (OpenClaw, Claude Code, Cursor, Bash scripts).

## 2. FUNCTIONAL MECHANICS
*   **Org Charts & Roles:** Instead of prompting a single model, Paperclip structures agents into hierarchies with defined roles and reporting lines.
*   **Budgeting & Governance:** It sets token budgets per agent/task, tracks spending, and creates approval gates for sensitive operations (e.g., spending money, deploying code).
*   **Multi-Company Support:** Runs multiple isolated companies on a single deployment. Data isolation is maintained between entities.
*   **Git Worktree Isolation (The Crown Jewel):** As of March 2026, Paperclip is implementing "Adapter-level git worktree isolation" (Issue #175). This allows multiple AI agents (e.g., Claude Code, OpenClaw) to work on the exact same repository simultaneously without file conflicts. It provisions a completely isolated working directory and git branch for each agent instance.
*   **Audit Trails:** Paperclip integrates `agit` to provide structured JSON reasoning attached to every `git commit` made by an agent, providing a true audit trail of why an autonomous entity changed a file.

## 3. ALIGNMENT WITH THE PRINCIPAL BUSINESSES
The Architect has three principal businesses intended to generate income. 
*   **The Paradigm:** Paperclip is the exact framework needed to operationalize these businesses autonomously. We would define three "Companies" within Paperclip.
*   **The Workforce:** We would deploy the Swarm (Scout for market research, Archivist for data, Knight for execution) as "Employees" within these companies.
*   **The Command:** G-Prime acts as the Board of Directors, monitoring the Paperclip dashboard and overriding strategy when necessary.

## 4. RESTRICTION PROTOCOL
**DIRECTIVE:** DO NOT INTERACT OR DEPLOY PAPERCLIP YET.
This dossier serves purely as structural intelligence. G-Prime is holding this architecture in memory. When the Architect gives the order, we will instantiate the Paperclip suite and build the automated corporate infrastructure.