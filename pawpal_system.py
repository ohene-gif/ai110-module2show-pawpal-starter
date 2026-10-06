from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any


PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3}


def time_to_minutes(time_value: str) -> int:
    """Convert a HH:MM time string into minutes since midnight."""
    try:
        hours, minutes = map(int, time_value.split(":"))
        return hours * 60 + minutes
    except ValueError as exc:  # pragma: no cover - defensive check
        raise ValueError(f"Invalid time value: {time_value!r}") from exc


@dataclass
class Task:
    """A single pet-care activity with timing, priority, and optional recurrence."""

    title: str
    start_time: str
    duration: int = 30
    priority: str = "medium"
    frequency: str = "none"
    completed: bool = False
    description: str = ""
    pet_name: str | None = None
    task_date: date | None = None

    def __post_init__(self):
        if self.priority.lower() not in PRIORITY_LEVELS:
            raise ValueError("Priority must be one of: low, medium, high")
        if self.frequency.lower() not in {"none", "daily", "weekly"}:
            raise ValueError("Frequency must be: none, daily, or weekly")
        if self.task_date is None:
            self.task_date = date.today()
        self.priority = self.priority.lower()
        self.frequency = self.frequency.lower()
        self.start_time = self._normalize_time(self.start_time)

    @staticmethod
    def _normalize_time(value: str) -> str:
        """Ensure the time is stored in HH:MM format."""
        if ":" not in value:
            raise ValueError("Time must be in HH:MM format.")
        hours, minutes = map(int, value.split(":"))
        if not 0 <= hours <= 23 or not 0 <= minutes <= 59:
            raise ValueError("Time must be between 00:00 and 23:59.")
        return f"{hours:02d}:{minutes:02d}"

    def mark_complete(self) -> "Task | None":
        """Mark the task complete and create the next recurring task if needed."""
        self.completed = True
        if self.frequency == "none":
            return None
        return self.create_next_occurrence()

    def create_next_occurrence(self) -> "Task | None":
        """Return the next scheduled instance for a recurring task."""
        if self.frequency == "none":
            return None
        next_date = self.task_date + timedelta(days=1 if self.frequency == "daily" else 7)
        return Task(
            title=self.title,
            start_time=self.start_time,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            description=self.description,
            pet_name=self.pet_name,
            task_date=next_date,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the task to a dictionary for JSON storage."""
        return {
            "title": self.title,
            "start_time": self.start_time,
            "duration": self.duration,
            "priority": self.priority,
            "frequency": self.frequency,
            "completed": self.completed,
            "description": self.description,
            "pet_name": self.pet_name,
            "task_date": self.task_date.isoformat() if self.task_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create a Task from saved JSON data."""
        return cls(
            title=data.get("title", "Untitled task"),
            start_time=data.get("start_time", "09:00"),
            duration=int(data.get("duration", 30)),
            priority=data.get("priority", "medium"),
            frequency=data.get("frequency", "none"),
            completed=bool(data.get("completed", False)),
            description=data.get("description", ""),
            pet_name=data.get("pet_name"),
            task_date=date.fromisoformat(data["task_date"]) if data.get("task_date") else date.today(),
        )

    @property
    def time_rank(self) -> int:
        """Return the schedule order for the task by time of day."""
        return time_to_minutes(self.start_time)


@dataclass
class Pet:
    """A pet profile with its own list of care tasks."""

    name: str
    species: str = "dog"
    age: int | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> Task:
        """Add a task to this pet and attach the pet name for scheduling."""
        task.pet_name = self.name
        self.tasks.append(task)
        return task

    @property
    def task_count(self) -> int:
        """Return the total number of tasks assigned to this pet."""
        return len(self.tasks)

    def get_tasks(self, include_completed: bool = False) -> list[Task]:
        """Return tasks, optionally including completed tasks."""
        if include_completed:
            return list(self.tasks)
        return [task for task in self.tasks if not task.completed]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the pet to a dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pet":
        """Create a Pet from saved JSON data."""
        pet = cls(name=data.get("name", "Unnamed pet"), species=data.get("species", "dog"), age=data.get("age"))
        pet.tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        return pet


@dataclass
class Owner:
    """An owner who manages one or more pets and all of their care tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> Pet:
        """Add a pet to the owner's list."""
        self.pets.append(pet)
        return pet

    def get_pet(self, pet_name: str) -> Pet | None:
        """Find a pet by name."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self, include_completed: bool = False) -> list[Task]:
        """Collect all tasks for all pets managed by this owner."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks(include_completed=include_completed))
        return tasks

    def save_to_json(self, file_path: str | Path) -> None:
        """Persist owner data to a JSON file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)

    @classmethod
    def load_from_json(cls, file_path: str | Path) -> "Owner":
        """Load an owner from a JSON file."""
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        owner = cls(name=data.get("name", "Owner"))
        owner.pets = [Pet.from_dict(pet_data) for pet_data in data.get("pets", [])]
        return owner

    def to_dict(self) -> dict[str, Any]:
        """Serialize the owner and pets to JSON-friendly data."""
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
        }


class Scheduler:
    """Coordinate task sorting, filtering, conflict detection, and daily planning."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by start time from earliest to latest."""
        return sorted(tasks, key=lambda task: task.time_rank)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by priority level and then by time."""
        return sorted(
            tasks,
            key=lambda task: (-PRIORITY_LEVELS.get(task.priority, 0), task.time_rank),
        )

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_name: str | None = None,
        include_completed: bool = False,
        priority: str | None = None,
    ) -> list[Task]:
        """Filter tasks by pet name, completion status, or priority."""
        filtered = []
        for task in tasks:
            if task.completed and not include_completed:
                continue
            if pet_name and task.pet_name and task.pet_name.lower() != pet_name.lower():
                continue
            if priority and task.priority.lower() != priority.lower():
                continue
            filtered.append(task)
        return filtered

    def build_daily_plan(self, pet_name: str | None = None) -> list[Task]:
        """Build today's plan, ordered by priority then time."""
        return self.build_plan_for_date(date.today(), pet_name)

    def build_plan_for_date(self, plan_date: date, pet_name: str | None = None) -> list[Task]:
        """Build a plan for one date, ordered by priority then time."""
        tasks = self.owner.get_all_tasks(include_completed=False)
        tasks = [task for task in tasks if task.task_date == plan_date]
        tasks = self.filter_tasks(tasks, pet_name=pet_name, include_completed=False)
        return self.sort_by_priority(tasks)

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete an owner's task and attach its next recurring occurrence."""
        if task.completed:
            return None

        for pet in self.owner.pets:
            if any(owned_task is task for owned_task in pet.tasks):
                next_task = task.mark_complete()
                if next_task is not None:
                    pet.add_task(next_task)
                return next_task

        raise ValueError("The task does not belong to one of this owner's pets.")

    def find_next_available_slot(
        self,
        duration: int,
        start_time: str = "08:00",
        end_time: str = "23:59",
        tasks: list[Task] | None = None,
        plan_date: date | None = None,
    ) -> str | None:
        """Find the earliest minute-sized slot that fits without overlapping tasks."""
        if duration <= 0:
            raise ValueError("Duration must be a positive number of minutes.")

        earliest = time_to_minutes(Task._normalize_time(start_time))
        latest = time_to_minutes(Task._normalize_time(end_time))
        if latest < earliest:
            raise ValueError("End time must be at or after start time.")

        target_date = plan_date or date.today()
        scheduled_tasks = tasks if tasks is not None else self.owner.get_all_tasks()
        busy_intervals = [
            (task.time_rank, task.time_rank + task.duration)
            for task in scheduled_tasks
            if not task.completed and task.task_date == target_date
        ]

        candidate = earliest
        latest_start = latest - duration
        while candidate <= latest_start:
            candidate_end = candidate + duration
            if all(
                candidate_end <= busy_start or candidate >= busy_end
                for busy_start, busy_end in busy_intervals
            ):
                return f"{candidate // 60:02d}:{candidate % 60:02d}"
            candidate += 1
        return None

    def detect_conflicts(self, tasks: list[Task]) -> list[dict[str, Any]]:
        """Find duplicate start times for tasks on the same date across all pets."""
        grouped: dict[tuple[date | None, str], list[Task]] = {}
        for task in tasks:
            if task.completed:
                continue
            key = (task.task_date, task.start_time)
            grouped.setdefault(key, []).append(task)

        conflicts: list[dict[str, Any]] = []
        for (task_date, start_time), matched_tasks in grouped.items():
            if len(matched_tasks) > 1:
                pet_names = sorted({task.pet_name or "Unknown pet" for task in matched_tasks})
                conflicts.append(
                    {
                        "date": task_date.isoformat() if task_date else None,
                        "pet": ", ".join(pet_names),
                        "pets": pet_names,
                        "time": start_time,
                        "tasks": [task.title for task in matched_tasks],
                    }
                )
        return conflicts

    def render_plan(self, pet_name: str | None = None) -> str:
        """Render a human-readable schedule summary for the terminal."""
        plan = self.build_daily_plan(pet_name)
        if not plan:
            return "No tasks scheduled yet."

        lines = ["Today's PawPal+ schedule:"]
        for index, task in enumerate(plan, start=1):
            pet_label = task.pet_name or "Unknown pet"
            lines.append(
                f"{index}. {task.start_time} - {task.title} ({pet_label}) "
                f"[{task.priority}] {task.duration} min"
            )
        return "\n".join(lines)


__all__ = ["Owner", "Pet", "Scheduler", "Task"]
