# PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a busy pet owner stay consistent with
pet care. Enter your pets and their care tasks, and PawPal+ builds an explainable
daily plan that respects your time budget, task priorities, and scheduled times.

## Scenario

A busy pet owner needs help staying consistent with pet care. PawPal+ acts as an
assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

The system was designed UML-first, implemented as a standalone logic layer
(`pawpal_system.py`), covered with tests (`tests/test_pawpal.py`), and connected
to an interactive Streamlit UI (`app.py`).

## ✨ Features

PawPal+ implements the following scheduling algorithms and behaviors. All logic
lives in `pawpal_system.py` and is exercised by the demo in `main.py`.

- **Priority-first scheduling** — a greedy `generate_plan()` walks tasks in
  priority order (high → low, shortest-duration first as a tiebreak) and includes
  each one that still fits the remaining daily time budget.
- **Sorting by priority** — `Scheduler.sort_tasks()` orders tasks by priority
  rank, then duration; this is the order the planner consumes.
- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks chronologically
  by their `"HH:MM"` start time (converted to minutes-since-midnight, so
  un-padded times like `"8:00"` still sort correctly); unscheduled tasks sort last.
- **Filtering** — `Owner.filter_tasks(pet_name, status)` narrows tasks by pet,
  by completion status, or both.
- **Conflict warnings** — `Scheduler.find_conflicts()` / `conflict_warnings()`
  detect tasks that share a start time (an owner can't be in two places at once)
  and return friendly warning strings instead of crashing.
- **Daily / weekly recurrence** — `Task.next_occurrence()` and
  `Pet.complete_task()` auto-generate the next instance of a recurring task
  (`+1 day` for daily, `+7 days` for weekly) when it's completed; `"once"` tasks
  don't repeat.
- **Time-budget enforcement & skip reasons** — tasks that don't fit are marked
  `SKIPPED` with an explanation, and `Scheduler.explain()` reports why each task
  was included or left out.

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

## 🧪 Testing PawPal+

Run the full test suite from the repo root:

```bash
python -m pytest
```

### What the tests cover

The 24 tests in `tests/test_pawpal.py` exercise the scheduling logic in
`pawpal_system.py`, focusing on both happy paths and edge cases:

- **Task & pet basics** — marking a task complete flips its status; adding a task
  grows the pet's task list.
- **Sorting correctness** — tasks return in chronological order by `start_time`
  (including un-padded times like `"8:00"`), unscheduled tasks sort last, the
  original list is left unmutated, and priority ordering ranks high → low with an
  unknown priority sorting last.
- **Filtering** — narrowing tasks by pet, by status, and by both at once.
- **Recurrence logic** — completing a daily task creates a fresh `TODO` for the
  next day; weekly advances +7 days; `"once"` does not recur; the successor
  preserves the original's details; and repeated completions keep advancing.
- **Conflict detection** — same-time tasks are flagged (three clashing tasks
  produce all three pairwise warnings) and distinct/unscheduled times produce
  none. One test documents a known limitation: `"8:00"` and `"08:00"` are not
  detected as a clash because the check compares raw strings.
- **Greedy scheduling (`generate_plan`)** — empty scheduler, exact-fit budget
  boundary, tasks too big to fit (marked `SKIPPED`), high-priority preference
  under a tight budget, repeatability across re-runs, and skipping tasks that are
  already done.

### Sample test output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.1.0, pluggy-1.6.0
rootdir: /Users/dalissabrisita/AI110/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 24 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  4%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  8%]
tests/test_pawpal.py::test_sort_by_time_orders_chronologically PASSED    [ 12%]
tests/test_pawpal.py::test_filter_tasks_by_pet_and_status PASSED         [ 16%]
tests/test_pawpal.py::test_completing_recurring_task_creates_next_occurrence PASSED [ 20%]
tests/test_pawpal.py::test_weekly_task_advances_seven_days_and_once_does_not_recur PASSED [ 25%]
tests/test_pawpal.py::test_scheduler_detects_same_time_conflict PASSED   [ 29%]
tests/test_pawpal.py::test_scheduler_reports_no_conflicts_when_times_differ PASSED [ 33%]
tests/test_pawpal.py::test_sort_by_time_leaves_original_list_unchanged PASSED [ 37%]
tests/test_pawpal.py::test_sort_by_time_handles_non_zero_padded_times PASSED [ 41%]
tests/test_pawpal.py::test_sort_by_time_with_all_unscheduled_keeps_them_all PASSED [ 45%]
tests/test_pawpal.py::test_sort_tasks_orders_by_priority_then_duration PASSED [ 50%]
tests/test_pawpal.py::test_unknown_priority_sorts_last PASSED            [ 54%]
tests/test_pawpal.py::test_recurring_next_occurrence_preserves_task_details PASSED [ 58%]
tests/test_pawpal.py::test_completing_task_twice_advances_the_date_each_time PASSED [ 62%]
tests/test_pawpal.py::test_three_tasks_at_same_time_produce_three_pairwise_conflicts PASSED [ 66%]
tests/test_pawpal.py::test_conflict_check_ignores_unscheduled_tasks PASSED [ 70%]
tests/test_pawpal.py::test_conflict_check_is_string_based_not_time_based PASSED [ 75%]
tests/test_pawpal.py::test_generate_plan_on_empty_scheduler PASSED       [ 79%]
tests/test_pawpal.py::test_generate_plan_includes_task_that_fits_exactly PASSED [ 83%]
tests/test_pawpal.py::test_generate_plan_skips_task_larger_than_budget PASSED [ 87%]
tests/test_pawpal.py::test_generate_plan_prefers_high_priority_when_budget_is_tight PASSED [ 91%]
tests/test_pawpal.py::test_generate_plan_is_repeatable_across_runs PASSED [ 95%]
tests/test_pawpal.py::test_generate_plan_skips_already_completed_tasks PASSED [100%]

============================== 24 passed in 0.02s ==============================
```

### Confidence Level: ⭐⭐⭐⭐⭐ (5/ 5)

All 24 tests pass and cover the core scheduling behaviors plus their edge cases,
so I'm confident the logic layer is reliable for the intended demo scenarios.


## 📐 Smarter Scheduling

Beyond the basic plan, PawPal+ adds four "smarter scheduling" features. All of
the logic lives in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | By priority + duration, or chronologically by start time |
| Filtering | `Owner.filter_tasks(pet_name, status)` | Narrow tasks by pet and/or completion status |
| Conflict detection | `Scheduler.find_conflicts()`, `Scheduler.conflict_warnings()` | Flags tasks sharing a start time; returns warnings, never crashes |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a daily/weekly task auto-creates the next one |

### Sorting behavior

Two sort orders are available on the `Scheduler`:

- **`Scheduler.sort_tasks()`** orders tasks by priority (high → low), then by
  shortest duration as a tiebreak. This is what `generate_plan()` uses to decide
  what to schedule first.
- **`Scheduler.sort_by_time()`** orders tasks chronologically by their `"HH:MM"`
  `start_time`. Times are converted to minutes-since-midnight for the sort key
  (robust to un-padded values), and unscheduled tasks sort to the end.

### Filtering behavior

**`Owner.filter_tasks(pet_name=None, status=None)`** returns tasks across all
pets, optionally narrowed:

- by **pet** — pass `pet_name="Rex"` to get just that pet's tasks;
- by **status** — pass `status=TaskStatus.DONE` (or the plain string `"done"`,
  since `TaskStatus` is a `str` enum) to get only completed/todo/skipped tasks;
- or **both** at once. With no arguments it returns every task.

### Conflict detection logic

**`Scheduler.find_conflicts()`** compares every pair of *scheduled* tasks (those
with a `start_time`) once and returns the pairs that share the same start time —
whether they belong to the same pet or different pets (an owner can't be in two
places at once). Unscheduled tasks are ignored.

**`Scheduler.conflict_warnings()`** wraps that into a lightweight, non-crashing
check: it returns a list of human-readable warning strings (e.g.
`⚠️ Conflict at 08:00: 'Morning walk' overlaps with 'Play time'.`) and an empty
list when there are none — so the app warns the user instead of failing.

### Recurring task logic

Each `Task` has a `frequency` (`"daily"`, `"weekly"`, or `"once"`) and a
`due_date`. **`Task.next_occurrence()`** uses `datetime.timedelta` to advance the
due date (`+1 day` for daily, `+7 days` for weekly) and returns a fresh `TODO`
copy, or `None` if the task doesn't repeat. **`Pet.complete_task(task)`** ties it
together: it marks the task `DONE` and, if it recurs, automatically adds the next
occurrence to the pet — so a daily walk reappears tomorrow and a weekly groom
reappears next week.

## 🎬 Demo Walkthrough

Launch the interactive app with:

```bash
streamlit run app.py
```

### Main UI features

The Streamlit UI (`app.py`) is a single scrolling page with these sections:

- **Owner** — set the owner's name and daily time budget (available minutes).
- **Add a Pet** — name a pet and pick a species; added pets are listed with a
  live task count.
- **Add a Task** — give a task a title, duration, priority, start time, target
  pet, and repeat frequency (daily / weekly / once). Each pet's tasks are shown
  in a table, sorted chronologically by start time.
- **Complete a Task** — mark a task done; a recurring task automatically
  schedules its next occurrence and the app confirms the new due date.
- **Browse Tasks** — filter all tasks by pet and/or status and view them in a
  priority-sorted table.
- **Build Schedule** — always-on conflict warnings plus a one-click daily plan
  shown with summary metrics (tasks planned, minutes used, tasks skipped), a
  time-ordered table of chosen tasks, and a table of skipped tasks with reasons.

### Example workflow

1. In **Owner**, set your name and a daily budget (e.g. 60 minutes).
2. In **Add a Pet**, add `Rex` (dog) and `Mia` (cat).
3. In **Add a Task**, give Rex a `Morning walk` (30 min, high priority, 08:00,
   daily) and a `Long groom` (45 min, low, 15:00, weekly); give Mia `Play time`
   (10 min, low, 08:00, daily) — deliberately at the same time as Rex's walk.
4. Scroll to **Build Schedule** — a conflict warning appears immediately because
   two tasks share the 08:00 slot.
5. Click **Generate schedule** to see today's plan: high-priority tasks are kept
   within the budget, lower-priority tasks that don't fit are listed as skipped
   with the reason.
6. Back in **Complete a Task**, mark the `Morning walk` done — PawPal+ confirms
   it has scheduled tomorrow's walk automatically.

### Key Scheduler behaviors on display

- **Sorting by time** — tasks reorder chronologically regardless of the order
  they were added.
- **Conflict warnings** — same-time tasks are flagged (`⚠️ Conflict at 08:00: …`)
  before any plan is built.
- **Filtering** — the Browse Tasks table narrows by pet and status.
- **Priority-first planning with a time budget** — `generate_plan()` fills the
  budget high-priority-first and explains every skip.
- **Daily / weekly recurrence** — completing a task rolls a daily task to
  tomorrow and a weekly task to next week.

### Sample CLI output

The same logic layer can be exercised without Streamlit by running the demo
script, which builds a small owner/pet/task setup and prints the results:

```bash
python main.py
```

```text
Dalissa's pets:
  - Rex (dog)
      * Long groom at 15:00 — 45 min, low priority, weekly (due 2026-07-05) [todo]
      * Morning walk at 08:00 — 30 min, high priority, daily (due 2026-07-05) [todo]
      * Feed breakfast at 07:30 — 10 min, high priority, daily (due 2026-07-05) [todo]
  - Mia (cat)
      * Vet meds at 12:30 — 15 min, high priority, daily (due 2026-07-05) [done]
      * Feed breakfast at 07:45 — 5 min, medium priority, daily (due 2026-07-05) [todo]
      * Play time at 08:00 — 10 min, low priority, daily (due 2026-07-05) [todo]

========================================
All tasks sorted by time
========================================
  Feed breakfast at 07:30 — 10 min, high priority, daily (due 2026-07-05) [todo]
  Feed breakfast at 07:45 — 5 min, medium priority, daily (due 2026-07-05) [todo]
  Morning walk at 08:00 — 30 min, high priority, daily (due 2026-07-05) [todo]
  Play time at 08:00 — 10 min, low priority, daily (due 2026-07-05) [todo]
  Vet meds at 12:30 — 15 min, high priority, daily (due 2026-07-05) [done]
  Long groom at 15:00 — 45 min, low priority, weekly (due 2026-07-05) [todo]

========================================
Conflict detection
========================================
⚠️ Conflict at 08:00: 'Morning walk' overlaps with 'Play time'.

========================================
Filtering
========================================
Rex's tasks only:
  Long groom at 15:00 — 45 min, low priority, weekly (due 2026-07-05) [todo]
  Morning walk at 08:00 — 30 min, high priority, daily (due 2026-07-05) [todo]
  Feed breakfast at 07:30 — 10 min, high priority, daily (due 2026-07-05) [todo]

Still to do (status == todo):
  Long groom at 15:00 — 45 min, low priority, weekly (due 2026-07-05) [todo]
  Morning walk at 08:00 — 30 min, high priority, daily (due 2026-07-05) [todo]
  Feed breakfast at 07:30 — 10 min, high priority, daily (due 2026-07-05) [todo]
  Feed breakfast at 07:45 — 5 min, medium priority, daily (due 2026-07-05) [todo]
  Play time at 08:00 — 10 min, low priority, daily (due 2026-07-05) [todo]

Already done (status == done):
  Vet meds at 12:30 — 15 min, high priority, daily (due 2026-07-05) [done]

========================================
Today's Schedule for Dalissa
========================================

Rex (dog):
Daily plan: 2 task(s), 40/60 min used.
  ✓ Feed breakfast (10 min, high)
  ✓ Morning walk (30 min, high)
  ✗ Long groom — skipped: needs 45 min, only 20 left

Mia (cat):
Daily plan: 2 task(s), 15/60 min used.
  ✓ Feed breakfast (5 min, medium)
  ✓ Play time (10 min, low)
  ✗ Vet meds — skipped: already completed

========================================
Recurring tasks
========================================

Completing: Morning walk at 08:00 — 30 min, high priority, daily (due 2026-07-05) [todo]
  -> next occurrence: Morning walk at 08:00 — 30 min, high priority, daily (due 2026-07-06) [todo]

Completing: Long groom at 15:00 — 45 min, low priority, weekly (due 2026-07-05) [skipped]
  -> next occurrence: Long groom at 15:00 — 45 min, low priority, weekly (due 2026-07-12) [todo]
```
