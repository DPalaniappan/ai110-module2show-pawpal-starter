"""PawPal+ class skeletons.

Structure mirrors diagrams/uml.mmd: Owner, Pet, Task, Scheduler.
No logic implemented yet — stubs only.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    id: int
    name: str
    duration: int
    priority: int
    category: str
    time_of_day: str
    status: str = "not complete"

    def get_id(self) -> int:
        pass

    def task_valid(self) -> bool:
        pass

    def update_status(self, code) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: int) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def task_count(self) -> int:
        pass


@dataclass
class Owner:
    name: str
    time_available: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_list_of_pets(self) -> list[Pet]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_tasks(self, pet: Pet) -> list[Task]:
        pass

    def detect_conflicts(self) -> list:
        pass

    def generate_plan(self) -> dict:
        pass

    def explain_reasoning(self) -> str:
        pass

    def get_summary(self) -> str:
        pass
