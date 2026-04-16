---
name: example-skill
description: >-
  Template skill for creating new skills. Copy this directory, rename it, and
  fill in the sections below. Use as a starting point whenever you need to add
  a new skill to this repo.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
---

# Example Skill

A brief description of what this skill enables an agent to do and why it exists.

## When to Use

Describe the contexts, user phrases, or triggers that should activate this skill.

## Instructions

Step-by-step instructions the agent should follow when this skill is invoked.

1. First step
2. Second step
3. Third step

## Output Format

Describe the expected output structure or template.

```
# Example output template
## Section heading
- Key finding or action
```

## Examples

**Example 1:**
Input: A realistic user prompt
Output: What the agent should produce

**Example 2:**
Input: An edge-case prompt
Output: How the agent should handle it

## Edge Cases

- **Case 1**: Description of an edge case and how to handle it
- **Case 2**: Another edge case and its resolution

## References

If the skill needs supporting files, organize them as:

```
example-skill/
├── SKILL.md
├── scripts/      # Executable code for deterministic tasks
├── references/   # Detailed docs loaded as needed
└── assets/       # Templates, images, data files
```

Use relative paths from the skill root to reference bundled files.
