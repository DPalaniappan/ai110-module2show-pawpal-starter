# PawPal+ Project Reflection

## 1. System Design

Core Actions: Add a pet,  Create a task, and see your tasks for the day

Brainstorm:


**a. Initial design**
- Briefly describe your initial UML design.
My intial UML desing included  4 classes which are Owner, Pet, Task, and Scheduler. 
- What classes did you include, and what responsibilities did you assign to each?

Owner class: Owner class has name, list of pets, time_available for the day, 

Methods:
 add_pet()  
 get_list_of_pets()

Pet class: Pet class has name, species, and age of pet, and the list of tasks

Methods:
add_task to pet(task), 
remove_task(taks_id), 
get_tasks()
task_count()



Task class: Tasks has id, name, duration, priority, task status, category, time of the day(morning, evening, afternoon, night) status of task

Methods:
get_id
task_valid
update_status()-> aligns with number with switchs tatement updating it to value (not complete, inporgress, complete)

Scheduler: Scheduler has owner class

Methods:
sort_takss bu priority and duration for each pet
detect conflicts with time and priporty
generate plan
explain reasoning()-> how many tasks mad ethe cut and what got pleft behind
getSummary() return summary of scheduled task

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
