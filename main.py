"""PawPal+ demo entry point.

Builds a sample owner, a couple of pets, and some tasks, then generates
and prints each pet's schedule for the day using the Scheduler class.
"""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

# Create an owner with a daily time budget (in minutes) and preferences
# used as scheduling tiebreakers.
owner = Owner(
    name="Jordan",
    time_available=90,
    preferred_categories=["walk"],
    preferred_times_of_day=["morning"],
)

# Create two pets and register them with the owner.
mochi = Pet(name="Mochi", species="cat", age=2)
biscuit = Pet(name="Biscuit", species="dog", age=4)
owner.add_pet(mochi)
owner.add_pet(biscuit)

# Add tasks out of time order on purpose, to prove sort_by_time() actually
# reorders them rather than just reflecting insertion order.
mochi.add_task(Task(
    category="grooming", duration=15, priority="low",
    name="Evening brushing", time_of_day="18:00",
))
mochi.add_task(Task(
    category="other", duration=10, priority="low",
    name="Late night litter check", time_of_day="23:00",
))
mochi.add_task(Task(
    category="feeding", duration=10, priority="high",
    name="Morning feeding", time_of_day="08:00",
))
mochi.add_task(Task(
    category="enrichment", duration=20, priority="medium",
    name="Midday play", time_of_day="12:00",
))
mochi.add_task(Task(
    category="grooming", duration=15, priority="low",
    name="Weekly nail trim", frequency="weekly", time_of_day="",
))
biscuit.add_task(Task(
    category="enrichment", duration=20, priority="medium",
    name="Afternoon puzzle toy", time_of_day="13:00",
))
biscuit.add_task(Task(
    category="walk", duration=25, priority="medium",
    name="Evening walk", time_of_day="19:00",
))
biscuit.add_task(Task(
    category="walk", duration=30, priority="high",
    name="Morning walk", time_of_day="07:30",
))
biscuit.add_task(Task(
    category="meds", duration=5, priority="high",
    name="Meds", time_of_day="09:00",
))
# Overlaps with Mochi's "Morning feeding" (08:00-08:10) on purpose, to demonstrate
# detect_conflicts().
biscuit.add_task(Task(
    category="walk", duration=10, priority="medium",
    name="Overlapping morning check-in", time_of_day="08:05",
))

# Mark a couple of tasks complete so filter_tasks() has something
# of each status to show.
mochi.get_tasks()[0].mark_complete()   # Evening brushing
biscuit.get_tasks()[3].mark_complete() # Meds

# 1. Generate and print today's combined schedule across all of the owner's pets.
scheduler = Scheduler(owner=owner)
scheduler.generate_plan()
scheduler.display_schedule()

# 2. Show completed vs. incomplete tasks using filter_tasks().
print("\nCompleted tasks:")
for task in scheduler.filter_tasks(is_completed=True):
    print(f"  {task.name}")

print("\nIncomplete tasks:")
for task in scheduler.filter_tasks(is_completed=False):
    print(f"  {task.name}")

print(f"\n{biscuit.name}'s tasks:")
for task in scheduler.filter_tasks(pet=biscuit):
    print(f"  {task.name}")

# 3. Show sort_by_time() applied to just one pet's own tasks.
print(f"\n{mochi.name}'s tasks sorted by time of day (flexible tasks last):")
for task in scheduler.sort_by_time(mochi.get_tasks()):
    time_label = task.time_of_day if task.time_of_day else "Anytime"
    print(f"  {time_label}: {task.name}")

# 4. Test that completing a recurring task reschedules it (Pet.complete_task() +
# Task.reschedule()) rather than just marking it done.
print("\nRescheduling test:")
recurring_task = mochi.get_tasks()[2]  # "Morning feeding", frequency="daily"
print(f"  Before: {recurring_task.name}, is_completed={recurring_task.is_completed}, due_date={recurring_task.due_date}")

today = date.today()
mochi.complete_task(recurring_task, today)

print(f"  After:  {recurring_task.name}, is_completed={recurring_task.is_completed}, due_date={recurring_task.due_date}")
print(f"  {mochi.name} now has {mochi.task_count()} task(s):")
for task in mochi.get_tasks():
    print(f"    - {task.name} (is_completed={task.is_completed}, due_date={task.due_date})")

# 5. Test detect_conflicts() across every pet's tasks.
print("\nConflict check:")
all_tasks = [task for pet in owner.get_list_of_pets() for task in pet.get_tasks()]
conflicts = scheduler.detect_conflicts(all_tasks)
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")
