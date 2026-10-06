from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_mark_complete_updates_status():
    task = Task(title="Morning walk", start_time="08:00", duration=30, priority="high")

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_pet_add_task_increases_task_count():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Feeding", start_time="09:00", duration=10, priority="high"))

    assert len(pet.tasks) == 1
    assert pet.task_count == 1


def test_scheduler_sorts_tasks_by_time():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    pet.add_task(Task(title="Grooming", start_time="18:00", duration=45, priority="medium"))
    pet.add_task(Task(title="Walk", start_time="08:30", duration=30, priority="high"))
    pet.add_task(Task(title="Feeding", start_time="07:00", duration=10, priority="high"))

    schedule = Scheduler(owner).sort_by_time(pet.tasks)

    assert [task.title for task in schedule] == ["Feeding", "Walk", "Grooming"]


def test_scheduler_detects_conflicts_for_same_time():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Walk", start_time="08:00", duration=30, priority="high"))
    pet.add_task(Task(title="Training", start_time="08:00", duration=20, priority="medium"))

    conflicts = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(conflicts) >= 1
    assert conflicts[0]["time"] == "08:00"


def test_daily_recurring_task_creates_next_occurrence():
    task = Task(
        title="Medications",
        start_time="20:00",
        duration=10,
        priority="high",
        frequency="daily",
        task_date=date.today(),
    )

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.title == "Medications"
    assert next_task.frequency == "daily"
    assert next_task.completed is False
