# Strat Agent Wrapper Template

# Stratmeyer Analytica | Agent Instantiation Framework

## Purpose

This wrapper defines how G.Strat instantiates and interacts with Tier 2 agents.

---

## Instantiation Protocol

When spinning up any Strat agent:

1. **Load System Prompt** from `E:\G\agents\[AgentName]_prompt.md`
2. **Inject Context** (if any):
   - Current task brief
   - Relevant file paths
   - Previous session state (if resuming)
3. **Set Constraints**:
   - Working directories
   - Permissions level
   - Escalation thresholds
4. **Establish Reporting**:
   - Agent reports to G.Strat on completion or on hitting a blocker
   - Logs written to `E:\G\logs\[AgentName]_[date].md`

---

## Message Format: G.Strat → Agent

```
## MISSION BRIEF
**Agent:** [AgentName]
**Task:** [Concise task description]
**Context Files:** [List of relevant file paths]
**Output Expected:** [What should be delivered]
**Constraints:** [Any specific limits]
**Report To:** G.Strat

Execute.
```

---

## Message Format: Agent → G.Strat

```
## MISSION REPORT
**Agent:** [AgentName]
**Task:** [Task from brief]
**Status:** [Complete | Blocked | In Progress]
**Output:** [What was delivered, file paths]
**Issues:** [Any blockers or flags]
**Next:** [Suggested next action, if any]
```

---

## Error Handling

| Scenario | Agent Action |
|---|---|
| Task unclear | Request clarification from G.Strat |
| Blocker encountered | Report immediately with context |
| Task complete | Submit mission report |
| Sensitive operation | Escalate to G.Strat before proceeding |

---

## Log Structure

All agents log to `E:\G\logs\`:

```
[AgentName]_[YYYY-MM-DD].md
```

Log format:

```
## [Timestamp]
**Task:** [Task brief]
**Action:** [What was done]
**Result:** [Outcome]
```

---

*Strat Agent Wrapper | Stratmeyer Analytica | v1.0*
