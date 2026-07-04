# PawPal+ Project Reflection

## 1. System Design

Core Actions: Add a pet,  Create a task, and see a summary ofyour tasks for the day

Brainstorm:


**a. Initial design**
- Briefly describe your initial UML design.
My intial UML desing included  4 classes which are Owner, Pet, Task, and Scheduler. 
- What classes did you include, and what responsibilities did you assign to each?

Owner class: Owner class has name, list of pets, time_available for the day, time of the day preferences, (morning, evening, afternoon, etc), categroy preferences as well (walk, etc). Raises an error if name is empty or time_available isn't a positive number.

Methods:
add_pet(pet) -> rejects a pet if the owner already has one with the same name (case-insensitive)
get_list_of_pets()

Pet class: Pet class has name, species, and age of pet, and the list of tasks. Raises an error if name is empty.

Methods:
add_task(task)
remove_task(task) -> now takes the Task object itself instead of a task_id
get_tasks()
task_count()



Task class: Tasks has name, duration, priority (low, medium, high), is_completed, category, frequency (daily, weekly, as_needed), time_of_day (an "HH:MM" string, or "" for a flexible/any-time task). Raises an error if name is empty.

Methods:
mark_complete()
mark_incomplete()
task_priority() -> converts priority (high/medium/low) into 1/2/3
frequency_priority() -> converts frequency (daily/weekly/as_needed) into 1/2/3
task_window() -> parses time_of_day into (start, start+duration) minutes since midnight; returns None if flexible
time_period() -> classifies time_of_day into morning/afternoon/evening/night by distance from noon; returns "none" if flexible


Scheduler: Scheduler only holds an owner now (no separate pet field) — it builds one combined schedule across every pet that owner has, instead of one schedule per pet.

Methods:
user_task_priority(task)
matches_preferred_time(task)
matches_preferred_category(task)
sort_by_priority() -> returns (pet, task) pairs from all pets, ordered by priority/frequency score with preference tiebreakers
detect_conflicts() -> not implemented yet
generate_plan()
explain_reasoning()
get_summary()
display_schedule() -> prints "Today's Schedule" for all pets to the terminal

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes my design changed a lot during implementation after chatting with Claude Code as at first I focused on an appraoch for creating a seperate schedule for each pet given each of their tasks. However, after chatting with claude I realized that this was not the right approach as it would be weird to create a daily schedule for each pet, when for example you will most likely have to feed all of your pets daily. It would be a horrible choice to feed each of them for one day lol. Addionally after chatting with Claude I updated some attributes and methods for the classes as I realized it would be able to simplify my code and I would have an easier time accessing information as well.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
The constraints that me scheduler considered were the priority of the task, priority from the frequency, and then the owner preferences based on time of day and category. I decided that the priority of the task and frequency of the task mattered more as those priorities are greater than the user preferences as user preferences are mainly treated like suggestions, thus I decided to treat them as tie breakers for tasks have the same priority score. After that was the contraint of time as after sorting them by priority the schedule generator would take as many of the hhigh priority time tasks as it could within the time budget.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff the scheduler makes is that it uses a greedy algorithm meaning that if a task has a high priority and doesn't fit within the budgeted time then it is ignored. This is a reasonable trade off to make as it heavily reduces the code complexity as this would involve back tracking inot the scheduled-tasks and skipped-tasks and looking over what tasks to remove and keep in order to add a high priority task back into the scheduled tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
