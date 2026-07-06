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

Today's Schedule for [OWNER NAME]
Rex (dog):
Daily plan: 2 task(s), 40/60 min used.
  ✓ Feed breakfast (10 min, high)
  ✓ Morning walk (30 min, high)
  ✗ Long groom — skipped: needs 45 min, only 20 left

Mia (cat):
Daily plan: 2 task(s), 20/60 min used.
  ✓ Vet meds (15 min, high)
  ✓ Feed breakfast (5 min, medium)
```

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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
