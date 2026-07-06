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

My scheduler considers three constraints:

- **Time budget** — the owner's `available_minutes` is a hard cap. A task is only
  added to the plan if its `duration` still fits the minutes remaining.
- **Priority** — each task is `high`, `medium`, or `low`, ranked numerically so
  `generate_plan()` considers high-priority tasks first.
- **Duration (as a tiebreak)** — among equal-priority tasks, shorter ones are
  scheduled first so the plan fits as many important tasks as possible.

There's also a fourth, softer signal: **start time**. It doesn't decide *whether*
a task is included, but it drives `sort_by_time()` (chronological display) and
`find_conflicts()` (flagging two tasks set for the same time).

I decided the **time budget** mattered most because it's the whole point of the
app — a busy owner has a fixed amount of time, and a plan that ignores that isn't
useful. **Priority** came second because when time is scarce, the owner cares far
more that meds and feeding happen than that an optional grooming session does. I
left `preferences` as free-text rather than a hard constraint, because encoding
fuzzy preferences into the algorithm would add complexity without a clear,
testable payoff for this scenario.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
My scheduler is greedy: it picks the locally-best task at each step (highest
priority that still fits) instead of searching for the globally-optimal
combination.

This is reasonable because task lists are tiny, so a full optimizer (like a
knapsack search) adds complexity for no practical gain. Greedy is also
explainable — because it goes in strict priority order, `explain()` can honestly
report why each task was included or skipped, which matches how a busy owner
actually thinks about their day.


---

## 3. AI Collaboration

**a. How you used AI (and which features were most effective)**

I used my AI coding assistant across every phase: brainstorming the UML,
converting the design into Python, writing tests, wiring the Streamlit UI, and
drafting docs. The features that mattered most for building the *scheduler*
specifically were:

- **File-aware context (attaching files with `@`).** Pointing the assistant at
  `pawpal_system.py` and `uml_draft.mmd` at the same time meant its suggestions
  matched my real method names and signatures instead of inventing new ones. This
  was the single biggest quality lever.
- **Running the code, not just writing it.** The assistant could actually run
  `python main.py` and `python -m pytest` and read the real output. That turned
  "this should work" into "here is the verified output," which caught mismatches
  early (e.g., confirming `sort_by_time()` reordered tasks as expected).
- **Docstring and test scaffolding.** It was fast at drafting thorough
  docstrings and edge-case tests (empty scheduler, exact-fit budget, un-padded
  times), which I could then review and prune.

The most helpful prompts were *specific and constraint-bearing* — e.g., "surface
`conflict_warnings()` in the UI using `st.warning`, and don't mutate task state
on every rerun" — rather than open-ended "build the scheduler" asks.

**b. Judgment and verification**

- I evaluated suggestions by reading them against my separation-of-concerns rule
  (data in Owner/Pet/Task, algorithms in Scheduler, presentation in `app.py`) and
  by verifying behavior with the test suite and `main.py` output — not by trusting
  the code because it looked plausible.

**c. An AI suggestion I rejected / modified to keep the design clean**

When building the Streamlit UI, the straightforward suggestion was to build and
render the daily plan on every page rerun. I rejected that as-is because
`generate_plan()` **mutates** task state (it marks tasks `SKIPPED`), so running it
on every rerun would silently change data just from a user clicking around. I
modified the approach so that only the **non-mutating** `find_conflicts()` /
`conflict_warnings()` check runs continuously (conflicts should always be
visible), while the mutating `generate_plan()` stays gated behind an explicit
"Generate schedule" button. This kept state changes intentional and predictable
and preserved the clean line between reading data and changing it.

**d. Using separate chat sessions per phase**

I kept each phase in its own chat session — UML design, logic + tests, the
Streamlit feature build, and finally docs/UML-sync/reflection. This kept the
context focused: each session started from the current files rather than dragging
along stale assumptions, so the assistant didn't, for example, keep referencing
the *draft* UML after the code had moved on. It also gave me a clean, per-phase
record of decisions, which made it easy to revisit "why did I change this?"
later (like reconciling `uml_final.mmd` against the finished code).

**e. What I learned about being the "lead architect"**

Powerful AI tools are extremely fast at producing plausible code, but "plausible"
is not "correct" or "well-designed." My job as lead architect was to *own the
boundaries* — decide the class responsibilities, the separation of data /
behavior / UI, and the constraints — and then use the AI to fill them in quickly.
The value came from directing (clear, constrained prompts), reviewing (rejecting
suggestions that blurred concerns, like state-mutating renders), and verifying
(running the tests and demo instead of assuming). The AI accelerated the *typing*;
the architecture, the tradeoffs, and the final call on what was "clean" stayed
with me.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 24 tests in `tests/test_pawpal.py` cover the core scheduling behaviors and
their edge cases:

- **Task & pet basics** — marking a task complete flips its status; adding a task
  grows the pet's list.
- **Sorting** — chronological order by `start_time` (including un-padded times
  like `"8:00"`), unscheduled tasks sorting last, the original list staying
  unmutated, and priority order ranking high → low with unknown priorities last.
- **Filtering** — narrowing by pet, by status, and by both at once.
- **Recurrence** — daily creates tomorrow's `TODO`, weekly advances +7 days,
  `"once"` doesn't recur, the successor preserves the original's details, and
  repeated completions keep advancing the date.
- **Conflict detection** — same-time tasks are flagged (three clashing tasks give
  all three pairwise warnings), distinct/unscheduled times give none, and one
  test documents the known limitation that `"8:00"` vs `"08:00"` isn't caught
  because the check compares raw strings.
- **Greedy scheduling** — empty scheduler, exact-fit budget boundary, tasks too
  big to fit (marked `SKIPPED`), high-priority preference under a tight budget,
  repeatability across re-runs, and skipping already-done tasks.

These matter because they lock in the two things a user actually trusts the app
to get right: **which tasks make the plan** (time + priority) and **whether the
plan is honest about what it left out** (skip reasons and conflicts). Testing the
boundaries — exact-fit budget, unknown priority, string-based time comparison —
is where scheduling logic is most likely to break silently.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm confident (⭐⭐⭐⭐⭐) in the logic layer for the intended scenarios: all 24
tests pass, and running `main.py` end-to-end produces the plan, conflicts,
filtering, and recurrence I expect. My confidence is scoped to the behaviors I
tested — the algorithm is deliberately simple, which makes it easy to reason
about and hard to get subtly wrong.

If I had more time I'd test: (1) **time-value normalization**, so `"8:00"` and
`"08:00"` are treated as the same time in conflict detection instead of as
different strings; (2) **overlapping durations**, so a task at 08:00 that runs 30
minutes conflicts with one starting at 08:15, not just an exact time match; (3)
**invalid or missing input** (negative/zero durations, malformed times,
unknown frequencies); and (4) a **per-pet vs. shared time budget** — `main.py`
gives each pet its own 60 minutes, and I'd add tests around how the budget should
behave when tasks compete across pets.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the **separation of concerns**: the data classes
(Owner/Pet/Task), the scheduling algorithm (Scheduler), and the UI (`app.py`) are
cleanly split. That paid off directly — because the logic lives in one testable
place, I could write 24 tests against it, run the whole thing from `main.py`
without Streamlit, and later surface features like conflict warnings in the UI
just by calling existing methods. The design made every later phase easier.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd make time a real first-class value instead of an `"HH:MM"` string. Right now
conflict detection compares strings, so `"8:00"` and `"08:00"` slip past it, and
conflicts only mean "same exact start time" rather than "overlapping windows."
Parsing times into real time/`datetime` objects and comparing `[start, start +
duration]` intervals would make conflict detection genuinely correct. I'd also
reconcile the budget model — decide clearly whether the time budget is per-pet or
shared across all pets — since `main.py` and `app.py` currently treat it slightly
differently.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Designing the boundaries first is what made everything else possible. By deciding
early that data, algorithm, and presentation would be separate, I gave both
myself and the AI a clean structure to build inside — which meant AI suggestions
either fit the architecture or were easy to reject when they didn't. The lesson:
a good up-front design isn't just documentation, it's the thing that keeps a
fast, powerful tool (or a fast-moving me) from making a mess.
