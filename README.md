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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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
