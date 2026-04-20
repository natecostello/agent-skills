# MADR 4.0 ADR Template

Use this template when creating a new ADR. Replace all `<angle bracket>` placeholders with concrete information. Remove guidance comments before saving.

---

```markdown
---
status: proposed
date: <YYYY-MM-DD>
decision-makers: <list of names/roles who made this decision>
<!-- Optional RACI fields — include when relevant: -->
<!-- consulted: <list of people whose input was sought> -->
<!-- informed: <list of people who were notified> -->
related ADRs:
  - "<link and brief description of relationship>"
---

# <Short noun phrase describing the decision>

## Context and Problem Statement

<Describe the context and problem in 2-5 sentences. What forces are at play? Why does this decision need to be made now?>

## Decision Drivers

* <driver 1 — a concern, constraint, or requirement that shaped the decision>
* <driver 2>
* <driver 3>

## Considered Options

* <Option 1 title>
* <Option 2 title>
* <Option 3 title>

## Decision Outcome

Chosen option: "<Option title>", because <1-2 sentence justification tying back to decision drivers>.

Plan: `<path>` (created at `<commit-hash>`, last version before deletion at `<commit-hash>~1`)
<!-- Include the plan reference only if a planning document was created for this decision -->

### Consequences

* Good, because <positive consequence>
* Good, because <positive consequence>
* Neutral, because <neutral observation>
* Bad, because <negative consequence or trade-off>

### Confirmation

<How will we verify the decision was implemented correctly? Reference specific tests, metrics, or verification steps.>

## Pros and Cons of the Options

### <Option 1 title>

<1-2 sentence description of this option.>

* Good, because <advantage>
* Good, because <advantage>
* Neutral, because <observation>
* Bad, because <disadvantage>

### <Option 2 title>

<1-2 sentence description.>

* Good, because <advantage>
* Bad, because <disadvantage>

### <Option 3 title>

<1-2 sentence description.>

* Good, because <advantage>
* Bad, because <disadvantage>

## More Information

Implemented in PR #<number> (merged <date>).
<!-- Add links to relevant discussions, external references, or amended ADRs -->
```
