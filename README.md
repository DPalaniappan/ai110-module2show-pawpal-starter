# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```

Today's Schedule for Jordan's pets:
  07:30 — Biscuit: Morning walk (30 min) [priority: high]
  08:00 — Mochi: Morning feeding (10 min) [priority: high]
  13:00 — Biscuit: Afternoon puzzle toy (20 min) [priority: medium]
  18:00 — Mochi: Evening brushing (15 min) [priority: low]
Jordan's plan: 4 task(s) scheduled, 75 of 90 minutes used.

```
### Confidence Level

★★★★★ — All **21tests pass**. 

Pytests

```
tests/test_pawpal.py::test_mark_complete_changes_task_status PASSED                                                                                                                                         [  4%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                                                                                                                                         [  9%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED                                                                                                                                  [ 14%]
tests/test_pawpal.py::test_complete_daily_task_creates_task_for_following_day PASSED                                                                                                                        [ 19%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_times PASSED                                                                                                                                  [ 23%]
tests/test_pawpal.py::test_detect_conflicts_ignores_non_overlapping_times PASSED                                                                                                                            [ 28%]
tests/test_pawpal.py::test_generate_plan_excludes_completed_tasks PASSED                                                                                                                                    [ 33%]
tests/test_pawpal.py::test_generate_plan_schedules_across_multiple_pets PASSED                                                                                                                              [ 38%]
tests/test_pawpal.py::test_sort_by_priority_orders_high_before_low PASSED                                                                                                                                   [ 42%]
tests/test_pawpal.py::test_complete_weekly_task_creates_task_one_week_later PASSED                                                                                                                          [ 47%]
tests/test_pawpal.py::test_complete_as_needed_task_does_not_reschedule PASSED                                                                                                                               [ 52%]
tests/test_pawpal.py::test_sort_by_priority_tie_break_prefers_matching_time_and_category PASSED                                                                                                             [ 57%]
tests/test_pawpal.py::test_generate_plan_skips_task_that_does_not_fit PASSED                                                                                                                                [ 61%]
tests/test_pawpal.py::test_generate_plan_schedules_task_that_exactly_fills_remaining_time PASSED                                                                                                            [ 66%]
tests/test_pawpal.py::test_add_pet_rejects_duplicate_name_case_insensitive PASSED                                                                                                                           [ 71%]
tests/test_pawpal.py::test_owner_rejects_non_positive_time_available PASSED                                                                                                                                 [ 76%]
tests/test_pawpal.py::test_pet_rejects_empty_name PASSED                                                                                                                                                    [ 80%]
tests/test_pawpal.py::test_owner_rejects_empty_name PASSED                                                                                                                                                  [ 85%]
tests/test_pawpal.py::test_remove_task_raises_when_task_not_assigned PASSED                                                                                                                                 [ 90%]
tests/test_pawpal.py::test_remove_pet_raises_when_pet_not_assigned PASSED                                                                                                                                   [ 95%]
tests/test_pawpal.py::test_generate_plan_with_no_pets_returns_empty_plan PASSED                                                                                                                             [100%]

=============================================================================================== 21 passed in 0.05s ===============================================================================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time(tasks)` | `sort_by_priority()` orders all of the owner's tasks by combined priority + recurrence urgency (`Scheduler.user_task_priority()`), breaking ties by whether the task matches the owner's preferred time of day / category. `sort_by_time(tasks)` takes any list of tasks and orders them by `Task.task_window()` start time, placing flexible/any-time tasks last. `generate_plan()` runs both in sequence: priority first (to decide what fits the time budget), then time (to order the final schedule). |
| Filtering | `Scheduler.filter_tasks(tasks=None, is_completed=None, pet=None)` | A single general-purpose filter: pass `pet=` to narrow to one pet's tasks, `is_completed=True/False` to narrow by completion status, or `tasks=` to filter a list you already have — any combination works, and leaving an argument as `None` skips that filter. |
| Conflict handling | `Scheduler.detect_conflicts(tasks)` | Lightweight pairwise check: compares every pair of *incomplete* tasks' `Task.task_window()` ranges and returns a warning string for each pair whose windows overlap. Completed tasks and flexible/any-time tasks (`task_window()` returns `None`) are skipped, since neither can have a real scheduling conflict. |
| Recurring tasks | `Task.reschedule(new_date)`, `Pet.complete_task(task, today)` | `Task.reschedule(new_date)` returns a fresh, incomplete copy of a task due on `new_date + Task.RECURRENCE_DELTAS[frequency]` (1 day for "daily", 7 days for "weekly"), or `None` for a one-off ("as_needed") task. `Pet.complete_task(task, today)` is the entry point: it marks the task complete, then calls `reschedule()` and adds the next occurrence to the pet's task list if one comes back. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
