# AI Interactions Log

## Agent Workflow

**What task did you give the agent?**
I asked the AI to help me build the PawPal backend and UI, then help me check the assignment requirements and help me fix the remaining non-pytest gaps. The later work focused on cross-pet conflicts, recurring task completion, and an advanced next-available-slot feature.

**What did the agent do?**
It implemented the `Owner`, `Pet`, `Task`, and `Scheduler` classes; connected the Streamlit UI; added a CLI demo and initial tests; and updated the final UML and documentation. In the final non-pytest pass, it added date-aware daily plans, cross-pet same-time conflict warnings, recurring-task completion through the scheduler and UI, and a duration-aware next-available-slot search.

Files changed during the agent-assisted work: `pawpal_system.py`, `app.py`, `main.py`, `tests/test_pawpal.py`, `diagrams/uml_final.mmd`, `README.md`, `reflection.md`, and `ai_interactions.md`.

**What did you have to verify or fix manually?**
I reviewed whether the UML arrows matched the actual object references and checked that the scheduler reports a same-time conflict between different pets, adds a recurring task to its pet after completion, excludes future-dated tasks from today's plan, and finds an open slot that respects task durations. I also reviewed the AI code in the py files in general. I also checked the CLI output and Python compilation. After the latest scheduler changes, pytest was rerun and all five tests passed.

---

## Prompt Comparison

Both models addressed the same PawPal scheduling problem: find the earliest available slot of a requested duration without overlapping incomplete tasks on the selected date.

| | Option A | Option B |
|---|----------|----------|
| **Model / tool used** | GitHub Copilot | ChatGPT, GPT-6.1 |
| **Prompt** | "Explain and implement a clear scheduler method for finding the earliest available slot of a requested duration. Consider task start times, durations, dates, completion status, and overlap." | "Find the earliest fitting same-day slot across all pets; ignore completed tasks and other dates, allow adjacent tasks, enforce earliest/latest boundaries, and explain the algorithm, validation, edge cases, and complexity." |
| **Response summary** | Check candidate start times minute by minute against occupied task intervals; return the first fit or no result if none fits. | Sort occupied intervals and scan gaps, advancing the candidate past blockers; return the earliest fit or None. It gives complexity of O(N + K log K). |
| **What was useful** | The minute-by-minute approach is direct and matches the current implementation. | Sorting and scanning intervals avoids checking every minute and gives a clear performance analysis. It also explicitly covers invalid input, adjacent tasks, and midnight boundaries. |
| **Problems noticed** | Rechecking all task intervals at each candidate minute is less efficient as the schedule grows. | The proposed implementation is more detailed and requires careful boundary validation; the midnight restriction must be explicit. |
| **Decision** | Kept in the current implementation because the one-day search is small and the straightforward logic is easy to follow. | Its sorted-interval approach is a useful future optimization if schedules or search windows grow. |

**Which approach did you use in your final implementation and why?**
The current scheduler uses Copilot's simpler minute-by-minute approach because the search is limited to one day and the logic is easy to understand. ChatGPT's sort-and-scan response is more efficient for a larger schedule, so it is a reasonable future optimization.
