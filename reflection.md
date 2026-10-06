# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design included four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`. The `Owner` manages one or more pets, the `Pet` stores its associated care tasks, the `Task` represents each job with details like time, duration, priority, and frequency, and the `Scheduler` organizes those tasks into a daily plan.

**b. Design changes**

I adjusted the design slightly during implementation by adding JSON serialization methods to `Owner` and `Pet`, and by expanding `Task` with recurrence support. This was useful because the project required a simple persistence flow and recurring scheduling logic, which were not obvious in the initial starter design.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler mainly considers time, priority, pet assignment, and completion state. I gave priority the strongest weight because urgent tasks should appear earlier in the schedule, while time ordering keeps the plan organized for the day.

**b. Tradeoffs**

One tradeoff is that the current conflict detection only checks for exact time matches between tasks, not overlapping time ranges. This is reasonable for a lightweight pet-care planner because it keeps the logic easy to understand and avoids overcomplicating the scheduler while still catching the most obvious scheduling problems.

---

## 3. AI Collaboration

**a. How you used AI**

I used GitHub Copilot to brainstorm the class responsibilities, implement and connect the scheduler, explain the UML source, and compare the project against the assignment requirements. The most useful features were code generation and editing for implementation, plus debugging help that used actual test output to identify what an assertion was checking. In this project work, I used one ongoing chat rather than separate chats for each phase. Keeping the context together made it easier to connect design, code, and documentation, but separate chats could have made each phase more focused and easier to review.

**b. Judgment and verification**

I did not accept every AI-generated suggestion as-is. An initial conflict test checked whether `"08:00"` was contained in the conflict dictionary. When the test failed, I had to check the returned data structure and changed the assertion to compare the dictionary's `"time"` value with `"08:00"`. I verified the correction by running pytest and confirming that the tests passed.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion, pet task counting, time sorting, conflict detection, and daily recurring tasks. These behaviors are important because they directly reflect the app’s scheduling and planning reliability.

**b. Confidence**

I feel moderately confident in the scheduler because the core tests pass and the CLI demo output behaves correctly. If I had more time, I would test overlapping time ranges, multiple pets at once, and edge cases like invalid times and empty task lists.

---

## 5. Reflection

**a. What went well**

The strongest part of the project was turning the starter UI into a working pet-care planner with a clean backend and real scheduling logic.

**b. What you would improve**

I would next improve the scheduler to handle task overlaps with duration-aware conflict detection and add a richer explanation for why a task was selected.

**c. Key takeaway**

The biggest lesson was that being the lead architect means owning the design decisions and checking that the implementation matches the actual requirements, even when AI helps produce code quickly. Building and testing the backend before connecting the UI made the system easier to reason about. AI accelerated implementation, but I still needed to review its suggestions and verify behavior with tests and the running demo.
