# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

PawPal+ helps a busy pet owner plan their pet's care. A user should be able to:

1. **Add a pet and its care tasks** (like walks, feeding, or meds).
2. **Generate a daily plan** from those tasks.
3. **See today's plan** and why it was chosen.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design centered on four classes that split the app into a data
layer and a scheduling layer, kept separate from the Streamlit UI:

- **Owner** — Represents the person using the app and their overall
  constraints. It holds the owner's `name`, their daily `available_minutes`
  (the time budget), free-text `preferences`, and a list of `pets`. Its
  responsibilities are managing pets (`add_pet`, `list_pets`), so the Owner is
  the top-level container that ties everything together.

- **Pet** — Represents a single animal and the care it needs. It stores the
  pet's `name`, `species`, and a list of `tasks`. Its responsibilities are
  managing that pet's care tasks (`add_task`, `remove_task`, `list_tasks`). An
  Owner has many Pets (1-to-many).

- **Task** — Represents one unit of pet care, such as a walk, feeding, or meds.
  It holds a `name`, a `duration` in minutes, and a `priority` (high/medium/low).
  Its only responsibility is describing itself (`summary`); it is a simple data
  object that the scheduler reasons about. A Pet has many Tasks (1-to-many).

- **Scheduler** — The "brain" that turns tasks and constraints into a daily
  plan. It takes the collected `tasks` and the owner's `available_minutes`, then
  is responsible for ordering tasks (`sort_tasks`), choosing which ones fit the
  time budget (`generate_plan`), and explaining why tasks were included or
  skipped (`explain`). I deliberately kept the scheduling logic out of the data
  classes so the algorithm lives in one place and is easy to test.

The key relationships: an **Owner has many Pets**, a **Pet has many Tasks**, and
the **Scheduler depends on Tasks** (it uses them but doesn't own them). This
separation keeps data (Owner/Pet/Task) distinct from behavior (Scheduler) and
from presentation (the Streamlit UI in `app.py`).

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. In my initial design the `Owner` and `Scheduler` were disconnected. The
`Owner` held `available_minutes` and `preferences`, and the `Scheduler`
separately took `available_minutes`, but nothing linked them — whoever built the
`Scheduler` had to manually pull the tasks out of every pet and pass the minutes
in by hand. There was no actual code path that went from "an Owner with pets" to
"a daily plan," which is a core user action of the app.

To fix this, I connected the two classes so the `Owner` is responsible for
gathering all of its pets' tasks and constructing the `Scheduler` (with its own
`available_minutes`). I made this change because it removed the manual wiring,
kept the data (Owner/Pet/Task) properly linked to the behavior (Scheduler), and
gave the app a clear, single path from an owner's pets to a generated plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
My scheduler relies more on greedy picks the locally-best task at each step instead of searching for the globally-optimal combination.
It's reasonable b/c task lists are tiny, so a full optimizer (like knapsack search) adds complexity for no practical gain. Greedy is also explainable  because it goes in strict priority order, explain() can honestly report why each task was included or skipped, which matches how a busy owner actually thinks about their day.


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
