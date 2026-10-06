# PawPal+

PawPal+ is a pet care planning assistant that helps an owner organize daily care tasks for one or more pets. The system models pets, tasks, and owners in Python and generates a schedule based on time, priority, frequency, and conflict warnings.

## Features

- Owner, pet, and task tracking in a modular Python backend
- Task scheduling with time-based and priority-based ordering
- Filtering by pet name, completion status, and priority level
- Conflict warnings when tasks for any pets share a start time on the same date
- Recurring daily and weekly task support
- Next-available-slot search that accounts for task durations
- Streamlit UI for adding pets and tasks and generating a schedule
- JSON persistence for owners and pets

## Architecture

The core logic is implemented in `pawpal_system.py`, and the UI lives in `app.py`.

The UML diagram is stored in `diagrams/uml_final.mmd`.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
streamlit run app.py
```

## Sample CLI output

```text
Today's PawPal+ schedule:
1. 07:00 - Feeding (Mochi) [high] 10 min
2. 08:00 - Morning walk (Mochi) [high] 30 min
3. 08:00 - Vet check-in (Luna) [high] 20 min
4. 20:00 - Medication (Luna) [high] 10 min
5. 09:00 - Playtime (Luna) [medium] 25 min
6. 18:00 - Brush fur (Mochi) [medium] 20 min

Conflict warnings:
- Luna, Mochi have tasks at 08:00: Morning walk, Vet check-in

Next available 15-minute slot after 07:00: 07:10
```

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by clock time |
| Priority sorting | `Scheduler.sort_by_priority()` | Orders tasks by priority first, then time |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet, completed state, or priority |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns when tasks for any pets share a start time on the same date |
| Recurring tasks | `Scheduler.mark_task_complete()` / `Task.create_next_occurrence()` | Completing a daily or weekly task adds its next occurrence to that pet |
| Next available slot | `Scheduler.find_next_available_slot()` | Finds the earliest duration-sized opening without overlapping scheduled tasks |
| Persistence | `Owner.save_to_json()` / `Owner.load_from_json()` | Saves the roster to disk |

## Data Persistence

The app keeps the current owner and pet data in Streamlit session state while the app session is open. To retain that data between runs, use **Save JSON** in the sidebar; this calls `Owner.save_to_json()` and writes the owner, pets, and tasks to `pawpal_data.json` beside `app.py`. On a later run, choose **Load JSON** to restore that file through `Owner.load_from_json()`. The persistence implementation is in `pawpal_system.py`, and the sidebar controls are in `app.py`.

## UI Feedback and Formatting

The task table shows each task's pet, time, date, priority, duration, recurrence, and open/complete status. The Streamlit UI uses `st.success` for completed actions, `st.warning` for conflicts or missing data, and `st.error` for invalid task input. The app also keeps the `Owner` object in `st.session_state` while the current session is active.

## Testing PawPal+

The tests cover task completion, adding a task to a pet, sorting tasks by time, detecting same-time conflicts, and creating the next daily occurrence.

```bash
.venv\Scripts\python.exe -m pytest
```

Sample successful test run:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1
rootdir: C:\Users\1ohen\OneDrive\Documents\GitHub\PawPal Project\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 5 items

tests\test_pawpal.py .....                                               [100%]

============================== 5 passed in 0.03s ==============================
```

**Confidence level:** ★★★★☆ (4/5). All five tests pass, though additional edge-case tests would increase confidence.

## Demo walkthrough

1. Open the app and enter the owner name, then add one or more pets.
2. Add care tasks with a time, duration, priority, and optional daily or weekly recurrence.
3. Review task dates and statuses; mark a recurring task complete to add its next occurrence.
4. Review same-start-time conflict warnings, including conflicts between different pets.
5. Use Find next available slot to locate a duration-sized opening across the owner's schedule.
6. Generate the priority-aware schedule for the selected pet.
7. Use **Save JSON** to save the current roster, then **Load JSON** to restore it in a later app session.

## Stretch features included

- Priority-aware scheduling
- Recurring daily and weekly tasks
- Next-available-slot search
- JSON save/load persistence between app runs
- Streamlit session-state retention and success, warning, and error feedback
- AI agent workflow and prompt comparison documented in `ai_interactions.md`
