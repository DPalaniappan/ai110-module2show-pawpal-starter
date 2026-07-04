"""PawPal+ demo entry point.

Builds a sample owner, a couple of pets, and some tasks, then generates
and prints each pet's schedule for the day using the Scheduler class.
"""

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

# Add tasks (at least three, with different times of day) to the pets.
mochi.add_task(Task(
    category="feeding", duration=10, priority="high",
    name="Morning feeding", time_of_day="08:00",
))
mochi.add_task(Task(
    category="grooming", duration=15, priority="low",
    name="Evening brushing", time_of_day="18:00",
))
biscuit.add_task(Task(
    category="walk", duration=30, priority="high",
    name="Morning walk", time_of_day="07:30",
))
biscuit.add_task(Task(
    category="enrichment", duration=20, priority="medium",
    name="Afternoon puzzle toy", time_of_day="13:00",
))

# 1. Generate and print today's combined schedule across all of the owner's pets.
scheduler = Scheduler(owner=owner)
scheduler.generate_plan()
scheduler.display_schedule()
