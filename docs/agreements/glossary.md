# Glossary

Use these terms consistently in Issues, PRs, skills, scripts, and documentation.

| Term | Definition |
|---|---|
| Agentic Development | The operating layer that makes stateless agent work durable, traceable, and verifiable on top of an existing SDLC. |
| ADLC | Agentic Development Lifecycle: onboarding, collection, agreement, planning, execution, verification, and learning as one loop. |
| Landing | Writing information to a commit, Issue, PR, or check so it survives the current session. |
| Ledger | The connected GitHub record of intent, process, result, and evidence. |
| Ledger completeness | The rule that every change, however small, travels through the agent and GitHub record path; silent human changes are ledger gaps. |
| Three Merges | The agreement, license, and completion merges that concentrate human judgment in durable events. |
| Agreement merge | Human merge of reviewed requirements, decisions, non-goals, or vocabulary that defines what to build. |
| License merge | Human merge of measured setup evidence after one end-to-end trial proves unattended delegation can traverse the repository; it is an autonomy license, distinct from the MIT software license. |
| Completion merge | Human merge of a Task PR after its executable acceptance criteria, required checks, evidence, and design review are satisfied. |
| Minimum receptacle | Phase 0α: the thin repository structure needed to receive distilled project knowledge. |
| Measured setup | Phase 0β: Codex guidance, skills, agents, commands, and automation filled from agreements and verified by running them. |
| Work order | The requester-owned Task Issue body containing objective, context, acceptance criteria, boundaries, ownership, verification, and routing. |
| Plan comment | The authoritative working plan added to the Task Issue before implementation. Session plans and PR copies are caches. |
| Revised-plan comment | A new Task Issue comment that records a material plan change without rewriting the prior plan. |
| Test-first work order | A work order whose acceptance criteria already exist as executable tests or observable checks before implementation starts. |
| Issue graph | Epics, Tasks, sub-issue relations, and blockers used as planning data. |
| Tracking graph | The Issue graph plus origin `#N` references and PR `Closes #N` links, enabling diagnosis from plan, code, or search. |
| Frontier | Open, ready Task Issues whose blockers are all resolved; the set is mechanically calculated. |
| Rolling wave | Keeping distant work coarse and detailing only the next executable wave when information is freshest. |
| Single writer | The constraint that concurrent Tasks do not modify overlapping owned paths. |
| Evidence | A command result, check, diff, or observed behavior mapped to an acceptance criterion; an agent statement is not evidence. |
| Four-part diagnosis | Locating a mismatch in the work order, plan comment, PR diff, or Evidence/checks. |
| Risk gate | The exception that stops a `risk:high` Task after its plan comment until an authorized human approves it. |
| Orphaned Task | A Task with a durable start but no outcome and no live owner session. |
| Resume comment | A durable ownership-transfer record that states the derived current state and next action after interruption. |
| Retro candidate | A recorded first occurrence of project or agent-system friction that becomes a system-change candidate when repeated. |
| Retro | A project-local PR that changes guidance, skills, templates, tests, or gates so a repeated failure is prevented. |
| Upstream | A voluntary proposal that returns project-agnostic learning to the template; the template owner decides adoption. |
| Characterization test | A test that freezes an existing codebase's current behavior before delegated feature change. |
| Reference, do not paste | Keep sensitive or controlled data in its governed source and place only the minimum access-controlled reference in the ledger. |
