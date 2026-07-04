"""PawPal+ class skeletons.

Structure mirrors diagrams/uml.mmd: Owner, Pet, Task, Scheduler.
No logic implemented yet — stubs only.
"""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import ClassVar

@dataclass
class Task:
    category: str
    duration: int        # minutes
    priority: str        # high / medium / low
    name: str = ""       # custom label; only required when category is "other"
    frequency: str = "daily"        # daily / weekly / as_needed
    time_of_day: str = ""           # HH:MM (e.g. "08:30"), or "" for flexible/any time
    is_completed: bool = False
    due_date: date | None = None

    PRIORITY_VALUES: ClassVar[dict[str, int]] = {"high": 1, "medium": 2, "low": 3}
    # Buckets of minutes-of-distance-from-noon (12:00), closest to farthest.
    TIME_OF_DAY_RANGES: ClassVar[dict[str, tuple[int, int]]] = {
        "afternoon": (0, 179),
        "morning": (180, 359),
        "evening": (360, 539),
        "night": (540, 720),
    }
    # Recurrence urgency score (lower = more important).
    FREQUENCY_VALUES: ClassVar[dict[str, int]] = {"daily": 1, "weekly": 2, "as_needed": 3}
    # How far to push due_date out for each recurring frequency; frequencies absent
    # from this map (e.g. "as_needed") don't recur.
    RECURRENCE_DELTAS: ClassVar[dict[str, timedelta]] = {
        "daily": timedelta(days=1),
        "weekly": timedelta(days=7),
    }

    def __post_init__(self):
        """Validate that a task name was actually provided."""
        if not self.name or not self.name.strip():
            raise ValueError("Task name cannot be empty.")

    def reschedule(self, date: date) -> "Task | None":
        """If this task repeats (daily/weekly), return a fresh, incomplete copy of it
        due on new_date. Returns None for a one-off ("as_needed") task."""
        if self.frequency not in self.RECURRENCE_DELTAS:
            return None
        return replace(self, due_date=date + self.RECURRENCE_DELTAS[self.frequency], is_completed=False)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.is_completed = False

    def task_priority(self) -> int:
        """Convert this task's priority string into a number where 1 is highest and 3 is lowest."""
        return self.PRIORITY_VALUES[self.priority]

    def frequency_priority(self) -> int:
        """Score this task's recurrence frequency, where 1 is most urgent (daily) and 3 is least (as_needed)."""
        return self.FREQUENCY_VALUES.get(self.frequency, self.FREQUENCY_VALUES["as_needed"])

    def task_window(self) -> tuple[int, int] | None:
        """Parse time_of_day ("HH:MM") into minutes since midnight and return (start, start + duration).
        Returns None for a flexible/any-time task (time_of_day == "")."""
        if not self.time_of_day:
            return None
        hours, minutes = self.time_of_day.split(":")
        start = int(hours) * 60 + int(minutes)
        return (start, start + self.duration)

    def time_period(self) -> str:
        """Classify time_of_day as morning/afternoon/evening/night based on its
        absolute minute distance from noon (12:00), using TIME_OF_DAY_RANGES.
        Returns "none" for a flexible/any-time task (time_of_day == "")."""
        window = self.task_window()
        if window is None:
            return "none"
        start_minutes, _ = window
        distance_from_noon = abs(start_minutes - 720)
        for period, (low, high) in self.TIME_OF_DAY_RANGES.items():
            if low <= distance_from_noon <= high:
                return period
        raise ValueError(f"time_of_day '{self.time_of_day}' does not fall into any known range.")


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        """Validate that a pet name and species were actually provided."""
        if not self.name or not self.name.strip():
            raise ValueError("Pet name cannot be empty.")
        if not self.species or not self.species.strip():
            raise ValueError("Pet species cannot be empty.")

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove the given task from this pet; raises ValueError if it isn't assigned."""
        if task not in self.tasks:
            raise ValueError(f"Task '{task.name}' is not assigned to this pet.")
        self.tasks.remove(task)

    def complete_task(self, task: Task, today: date) -> None:
        """Mark a task complete, then reschedule it, adding the next occurrence to this
        pet's tasks if it recurs."""
        task.mark_complete()
        next_task = task.reschedule(today)
        if next_task is not None:
            self.add_task(next_task)

    def get_tasks(self) -> list[Task]:
        """Return the list of tasks assigned to this pet."""
        return self.tasks

    def task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return len(self.tasks)


@dataclass
class Owner:
    name: str
    time_available: int
    pets: list[Pet] = field(default_factory=list)
    preferred_categories: list[str] = field(default_factory=list)
    preferred_times_of_day: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate that name and time_available were actually provided."""
        if not self.name or not self.name.strip():
            raise ValueError("Owner name cannot be empty.")
        if self.time_available is None or self.time_available <= 0:
            raise ValueError("Owner time_available must be a positive number.")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, rejecting a pet with a duplicate name (case-insensitive)."""
        if any(existing.name.strip().lower() == pet.name.strip().lower() for existing in self.pets):
            raise ValueError(f"A pet named '{pet.name}' already exists for this owner.")
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove the given pet from this owner; raises ValueError if it isn't assigned."""
        if pet not in self.pets:
            raise ValueError(f"Pet '{pet.name}' does not belong to this owner.")
        self.pets.remove(pet)

    def get_list_of_pets(self) -> list[Pet]:
        """Return the list of pets belonging to this owner."""
        return self.pets


@dataclass
class Scheduler:
    owner: Owner
    scheduled_tasks: list[tuple[Pet, Task]] = field(default_factory=list)
    skipped_tasks: list[tuple[Pet, Task]] = field(default_factory=list)

    def _all_tasks(self) -> list[Task]:
        """Return every task belonging to any of the owner's pets."""
        return [task for pet in self.owner.get_list_of_pets() for task in pet.get_tasks()]

    def user_task_priority(self, task: Task) -> int:
        """Score a task by combining its priority level with its recurrence frequency (lower = more important)."""
        return task.task_priority() + task.frequency_priority()

    def matches_preferred_time(self, task: Task) -> bool:
        """Return True if the task's time period matches one of the owner's preferred times of day."""
        return task.time_period() != "none" and task.time_period() in self.owner.preferred_times_of_day

    def matches_preferred_category(self, task: Task) -> bool:
        """Return True if the task's category matches one of the owner's preferred categories."""
        return task.category in self.owner.preferred_categories

    def sort_by_priority(self) -> list[Task]:
        """Return tasks from all of the owner's pets, ordered by combined priority/frequency
        score, breaking ties first by preferred time-of-day match, then by preferred category match."""
        return sorted(
            self._all_tasks(),
            key=lambda task: (
                self.user_task_priority(task),
                not self.matches_preferred_time(task),
                not self.matches_preferred_category(task),
            ),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks ordered by their scheduled start time (via task_window()),
        with flexible/any-time tasks placed last."""
        return sorted(
            tasks,
            key=lambda task: (
                task.task_window() is None,
                task.task_window()[0] if task.task_window() is not None else 0,
            ),
        )

    def filter_tasks(
        self, tasks: list[Task] | None = None, is_completed: bool | None = None, pet: Pet | None = None
    ) -> list[Task]:
        """Return tasks, optionally narrowed to a given list, a single pet, and/or a
        completion status. With tasks left as None, pulls from a pet or the whole
        owner instead. Leaving is_completed as None skips that filter."""
        if tasks is None:
            tasks = pet.get_tasks() if pet is not None else self._all_tasks()
        if is_completed is not None:
            tasks = [task for task in tasks if task.is_completed == is_completed]
        return tasks

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Lightweight conflict check: compare every pair of incomplete tasks' time
        windows (via task_window()) and return a warning message for each pair whose
        windows overlap. Completed tasks (e.g. a rescheduled task's now-done original
        occurrence) and flexible/any-time tasks (task_window() is None) can't conflict."""
        active_tasks = self.filter_tasks(tasks=tasks, is_completed=False)
        warnings = []
        for i, task_a in enumerate(active_tasks):
            window_a = task_a.task_window()
            if window_a is None:
                continue
            start_a, end_a = window_a

            for task_b in active_tasks[i + 1:]:
                window_b = task_b.task_window()
                if window_b is None:
                    continue
                start_b, end_b = window_b

                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"Time conflict: '{task_a.name}' ({task_a.time_of_day}) overlaps "
                        f"with '{task_b.name}' ({task_b.time_of_day})"
                    )

        return warnings

    def generate_plan(self) -> dict:
        """Schedule tasks from all of the owner's pets within the owner's available time,
        skipping tasks that don't fit, then order each group by time of day and pair each
        task back up with its pet."""
        scheduled_tasks = []
        skipped_tasks = []
        time_remaining = self.owner.time_available

        for task in self.sort_by_priority():
            if task.duration <= time_remaining:
                scheduled_tasks.append(task)
                time_remaining -= task.duration
            else:
                skipped_tasks.append(task)

        scheduled_tasks = self.sort_by_time(scheduled_tasks)
        skipped_tasks = self.sort_by_time(skipped_tasks)

        pet_by_task_id = {
            id(task): pet
            for pet in self.owner.get_list_of_pets()
            for task in pet.get_tasks()
        }
        
        self.scheduled_tasks = [(pet_by_task_id[id(task)], task) for task in scheduled_tasks]
        self.skipped_tasks = [(pet_by_task_id[id(task)], task) for task in skipped_tasks]

        return {
            "scheduled_tasks": self.scheduled_tasks,
            "skipped_tasks": self.skipped_tasks,
            "time_used": self.owner.time_available - time_remaining,
            "time_remaining": time_remaining,
        }

    def explain_reasoning(self) -> str:
        """Explain which tasks were scheduled or skipped, and for which pet, and why."""
        lines = [
            f"Scheduled {len(self.scheduled_tasks)} task(s) across {self.owner.name}'s pets "
            f"within {self.owner.time_available} available minutes:"
        ]
        for pet, task in self.scheduled_tasks:
            lines.append(f"  - {pet.name}: {task.name} ({task.duration} min, priority={task.priority}) scheduled.")

        if self.skipped_tasks:
            lines.append("Skipped due to insufficient remaining time:")
            for pet, task in self.skipped_tasks:
                lines.append(f"  - {pet.name}: {task.name} ({task.duration} min, priority={task.priority}) skipped.")

        return "\n".join(lines)

    def get_summary(self) -> str:
        """Return a short summary of the generated plan."""
        total_time = sum(task.duration for _, task in self.scheduled_tasks)
        return (
            f"{self.owner.name}'s plan: {len(self.scheduled_tasks)} task(s) scheduled, "
            f"{total_time} of {self.owner.time_available} minutes used."
        )

    def display_schedule(self) -> None:
        """Print the generated schedule across all of the owner's pets to the terminal."""
        print(f"Today's Schedule for {self.owner.name}'s pets:")
        if not self.scheduled_tasks:
            print("  No tasks scheduled.")
        for pet, task in self.scheduled_tasks:
            time_label = task.time_of_day if task.time_of_day else "Anytime"
            print(f"  {time_label} — {pet.name}: {task.name} ({task.duration} min) [priority: {task.priority}]")

        if self.skipped_tasks:
            print("Skipped (not enough time):")
            for pet, task in self.skipped_tasks:
                print(f"  - {pet.name}: {task.name} ({task.duration} min) [priority: {task.priority}]")

        print(self.get_summary())
