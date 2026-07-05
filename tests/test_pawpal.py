import os
import sys
from datetime import date, timedelta

import pytest

# Make sure pawpal_system.py (at the project root) is importable regardless
# of the directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status():
    """Task Completion: calling mark_complete() should flip is_completed to True."""
    task = Task(category="walk", duration=20, priority="high", name="Morning walk")
    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet should increase that pet's task count."""
    pet = Pet(name="Mochi", species="cat", age=2)
    assert pet.task_count() == 0

    task = Task(category="feeding", duration=10, priority="medium", name="Feeding")
    pet.add_task(task)

    assert pet.task_count() == 1


def test_sort_by_time_returns_chronological_order():
    """Sorting Correctness: sort_by_time() should order tasks by start time,
    with flexible/any-time tasks placed last regardless of input order."""
    owner = Owner(name="Dana", time_available=120)
    scheduler = Scheduler(owner=owner)

    afternoon_task = Task(category="walk", duration=15, priority="medium", name="Walk", time_of_day="14:00")
    morning_task = Task(category="feeding", duration=10, priority="high", name="Breakfast", time_of_day="08:00")
    flexible_task = Task(category="play", duration=20, priority="low", name="Playtime")
    evening_task = Task(category="feeding", duration=10, priority="high", name="Dinner", time_of_day="18:30")

    ordered = scheduler.sort_by_time([afternoon_task, morning_task, flexible_task, evening_task])

    assert ordered == [morning_task, afternoon_task, evening_task, flexible_task]


def test_complete_daily_task_creates_task_for_following_day():
    """Recurrence Logic: completing a daily task should reschedule a fresh,
    incomplete copy of it due the following day, while the original is marked done."""
    pet = Pet(name="Mochi", species="cat", age=2)
    today = date(2026, 7, 4)
    task = Task(
        category="feeding",
        duration=10,
        priority="high",
        name="Breakfast",
        frequency="daily",
        due_date=today,
    )
    pet.add_task(task)

    pet.complete_task(task, today)

    assert task.is_completed is True
    assert pet.task_count() == 2

    new_task = next(t for t in pet.get_tasks() if t is not task)
    assert new_task.is_completed is False
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.name == task.name


def test_detect_conflicts_flags_overlapping_times():
    """Conflict Detection: the Scheduler should flag two tasks scheduled for
    duplicate/overlapping times."""
    owner = Owner(name="Dana", time_available=120)
    scheduler = Scheduler(owner=owner)

    walk = Task(category="walk", duration=30, priority="medium", name="Walk", time_of_day="09:00")
    vet_visit = Task(category="other", duration=30, priority="high", name="Vet visit", time_of_day="09:00")

    warnings = scheduler.detect_conflicts([walk, vet_visit])

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Vet visit" in warnings[0]


def test_detect_conflicts_ignores_non_overlapping_times():
    """Conflict Detection: tasks with distinct, non-overlapping windows should
    not be flagged."""
    owner = Owner(name="Dana", time_available=120)
    scheduler = Scheduler(owner=owner)

    walk = Task(category="walk", duration=30, priority="medium", name="Walk", time_of_day="09:00")
    feeding = Task(category="feeding", duration=10, priority="high", name="Breakfast", time_of_day="10:00")

    warnings = scheduler.detect_conflicts([walk, feeding])

    assert warnings == []


def test_generate_plan_excludes_completed_tasks():
    """Regression: a completed task (left in pet.tasks after being rescheduled)
    should not be re-scheduled or consume time budget in a later plan."""
    owner = Owner(name="Dana", time_available=60)
    pet = Pet(name="Mochi", species="cat", age=2)
    owner.add_pet(pet)

    today = date(2026, 7, 4)
    task = Task(
        category="feeding",
        duration=10,
        priority="high",
        name="Breakfast",
        frequency="daily",
        due_date=today,
    )
    pet.add_task(task)
    pet.complete_task(task, today)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan()

    scheduled_tasks = [t for _, t in plan["scheduled_tasks"]]
    assert task not in scheduled_tasks
    assert all(not t.is_completed for t in scheduled_tasks)


def test_generate_plan_schedules_across_multiple_pets():
    """Happy path: generate_plan() should schedule tasks from every pet the
    owner has, each paired back up with its own pet."""
    owner = Owner(name="Dana", time_available=60)
    mochi = Pet(name="Mochi", species="cat", age=2)
    rex = Pet(name="Rex", species="dog", age=4)
    owner.add_pet(mochi)
    owner.add_pet(rex)

    feed_mochi = Task(category="feeding", duration=20, priority="high", name="Feed Mochi", time_of_day="08:00")
    walk_rex = Task(category="walk", duration=20, priority="high", name="Walk Rex", time_of_day="09:00")
    mochi.add_task(feed_mochi)
    rex.add_task(walk_rex)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan()

    assert (mochi, feed_mochi) in plan["scheduled_tasks"]
    assert (rex, walk_rex) in plan["scheduled_tasks"]


def test_sort_by_priority_orders_high_before_low():
    """Happy path: a high-priority daily task should sort ahead of a
    low-priority as-needed task."""
    owner = Owner(name="Dana", time_available=60)
    pet = Pet(name="Mochi", species="cat", age=2)
    owner.add_pet(pet)

    low_task = Task(category="play", duration=10, priority="low", name="Play", frequency="as_needed")
    high_task = Task(category="feeding", duration=10, priority="high", name="Feed", frequency="daily")
    pet.add_task(low_task)
    pet.add_task(high_task)

    scheduler = Scheduler(owner=owner)
    ordered = scheduler.sort_by_priority()

    assert ordered.index(high_task) < ordered.index(low_task)


def test_complete_weekly_task_creates_task_one_week_later():
    """Happy path: completing a weekly task should reschedule a fresh copy
    of it due 7 days later."""
    pet = Pet(name="Mochi", species="cat", age=2)
    today = date(2026, 7, 4)
    task = Task(
        category="grooming",
        duration=30,
        priority="medium",
        name="Brush coat",
        frequency="weekly",
        due_date=today,
    )
    pet.add_task(task)

    pet.complete_task(task, today)

    new_task = next(t for t in pet.get_tasks() if t is not task)
    assert new_task.due_date == today + timedelta(days=7)
    assert new_task.is_completed is False


def test_complete_as_needed_task_does_not_reschedule():
    """Happy path: completing a one-off ("as_needed") task should not add a
    new occurrence."""
    pet = Pet(name="Mochi", species="cat", age=2)
    today = date(2026, 7, 4)
    task = Task(
        category="vet",
        duration=30,
        priority="medium",
        name="Vet checkup",
        frequency="as_needed",
        due_date=today,
    )
    pet.add_task(task)

    pet.complete_task(task, today)

    assert task.is_completed is True
    assert pet.task_count() == 1


def test_sort_by_priority_tie_break_prefers_matching_time_and_category():
    """Happy path: among equally-prioritized tasks, one matching the owner's
    preferred time-of-day and category should sort ahead of one that
    matches neither."""
    owner = Owner(
        name="Dana",
        time_available=60,
        preferred_categories=["walk"],
        preferred_times_of_day=["morning"],
    )
    pet = Pet(name="Rex", species="dog", age=4)
    owner.add_pet(pet)

    non_matching_task = Task(category="feeding", duration=10, priority="medium", name="Feed", time_of_day="20:00")
    matching_task = Task(category="walk", duration=10, priority="medium", name="Walk", time_of_day="08:00")
    pet.add_task(non_matching_task)
    pet.add_task(matching_task)

    scheduler = Scheduler(owner=owner)
    ordered = scheduler.sort_by_priority()

    assert ordered[0] is matching_task
    assert ordered[1] is non_matching_task


def test_generate_plan_skips_task_that_does_not_fit():
    """Edge case: a task that doesn't fit in the remaining time budget should
    land in skipped_tasks, and the totals should reflect only what fit."""
    owner = Owner(name="Dana", time_available=15)
    pet = Pet(name="Mochi", species="cat", age=2)
    owner.add_pet(pet)

    small_task = Task(category="feeding", duration=10, priority="high", name="Feed", time_of_day="08:00")
    big_task = Task(category="walk", duration=30, priority="medium", name="Walk", time_of_day="09:00")
    pet.add_task(small_task)
    pet.add_task(big_task)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan()

    assert small_task in [t for _, t in plan["scheduled_tasks"]]
    assert big_task in [t for _, t in plan["skipped_tasks"]]
    assert plan["time_used"] == 10
    assert plan["time_remaining"] == 5


def test_generate_plan_schedules_task_that_exactly_fills_remaining_time():
    """Edge case: a task whose duration exactly equals the remaining time
    budget should still be scheduled (boundary of the <= check)."""
    owner = Owner(name="Dana", time_available=20)
    pet = Pet(name="Mochi", species="cat", age=2)
    owner.add_pet(pet)

    task = Task(category="feeding", duration=20, priority="high", name="Feed", time_of_day="08:00")
    pet.add_task(task)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan()

    assert task in [t for _, t in plan["scheduled_tasks"]]
    assert plan["time_remaining"] == 0


def test_add_pet_rejects_duplicate_name_case_insensitive():
    """Edge case: adding a pet whose name matches an existing pet's name,
    ignoring case and surrounding whitespace, should raise."""
    owner = Owner(name="Dana", time_available=60)
    owner.add_pet(Pet(name="Rex", species="dog", age=3))

    with pytest.raises(ValueError):
        owner.add_pet(Pet(name="  rex ", species="dog", age=1))


def test_owner_rejects_non_positive_time_available():
    """Edge case: an owner cannot be created with zero or negative available time."""
    with pytest.raises(ValueError):
        Owner(name="Dana", time_available=0)


def test_pet_rejects_empty_name():
    """Edge case: a pet cannot be created with a blank name."""
    with pytest.raises(ValueError):
        Pet(name="   ", species="dog", age=1)


def test_owner_rejects_empty_name():
    """Edge case: an owner cannot be created with a blank name."""
    with pytest.raises(ValueError):
        Owner(name="   ", time_available=30)


def test_remove_task_raises_when_task_not_assigned():
    """Edge case: removing a task that was never added to the pet should raise."""
    pet = Pet(name="Mochi", species="cat", age=2)
    stray_task = Task(category="feeding", duration=10, priority="high", name="Feed")

    with pytest.raises(ValueError):
        pet.remove_task(stray_task)


def test_remove_pet_raises_when_pet_not_assigned():
    """Edge case: removing a pet that was never added to the owner should raise."""
    owner = Owner(name="Dana", time_available=60)
    stray_pet = Pet(name="Ghost", species="cat", age=1)

    with pytest.raises(ValueError):
        owner.remove_pet(stray_pet)


def test_generate_plan_with_no_pets_returns_empty_plan():
    """Edge case: an owner with no pets should produce an empty plan that
    uses none of the available time."""
    owner = Owner(name="Dana", time_available=60)
    scheduler = Scheduler(owner=owner)

    plan = scheduler.generate_plan()

    assert plan["scheduled_tasks"] == []
    assert plan["skipped_tasks"] == []
    assert plan["time_used"] == 0
    assert plan["time_remaining"] == 60
