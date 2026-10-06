from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task(title="Morning walk", start_time="08:00", duration=30, priority="high"))
    mochi.add_task(Task(title="Feeding", start_time="07:00", duration=10, priority="high"))
    mochi.add_task(Task(title="Brush fur", start_time="18:00", duration=20, priority="medium"))
    luna.add_task(Task(title="Playtime", start_time="09:00", duration=25, priority="medium"))
    luna.add_task(Task(title="Vet check-in", start_time="08:00", duration=20, priority="high"))
    luna.add_task(Task(title="Medication", start_time="20:00", duration=10, priority="high", frequency="daily", task_date=date.today()))

    scheduler = Scheduler(owner)
    print(scheduler.render_plan())

    conflicts = scheduler.detect_conflicts(owner.get_all_tasks())
    if conflicts:
        print("\nConflict warnings:")
        for conflict in conflicts:
            print(f"- {conflict['pet']} have tasks at {conflict['time']}: {', '.join(conflict['tasks'])}")

    available_slot = scheduler.find_next_available_slot(duration=15, start_time="07:00")
    print(f"\nNext available 15-minute slot after 07:00: {available_slot or 'none today'}")


if __name__ == "__main__":
    main()
