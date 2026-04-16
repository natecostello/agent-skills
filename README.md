# agent-skills

Personal collection of reusable agent skills following the [Agent Skills open standard](https://agentskills.io/specification).

## Philosophy

Skills in this repo are **reusable architectural patterns and workflows** — not project-specific configuration.

A skill like `app-secret-management` codifies an industry-standard pattern (system keyring + password manager + auto-export) that applies across any project dealing with secrets. The project's `CLAUDE.md` records how that pattern was instantiated (which library, which backend, where config lives). **The skill is the reusable reference; `CLAUDE.md` is the project-specific record.**

## Structure

```
agent-skills/
├── skills/
│   └── example-skill/
│       └── SKILL.md        # Frontmatter + instructions (agentskills.io spec)
├── install.sh              # Symlink installer for any agent
├── README.md
└── .gitignore
```

Each skill lives in its own directory under `skills/` and must contain a `SKILL.md` with valid [agentskills.io frontmatter](https://agentskills.io/specification). Skills can optionally include `scripts/`, `references/`, and `assets/` subdirectories.

## Usage

### Installing skills

```bash
# Install a skill for Claude Code (default) in the current project
./install.sh app-secret-management

# Install globally (user-wide)
./install.sh --global app-secret-management

# Install for multiple agents
./install.sh --codex --agents app-secret-management

# Install for all agents at once
./install.sh --all app-secret-management

# Install multiple skills
./install.sh --all app-secret-management tdd-workflow

# Preview without making changes
./install.sh --dry-run --all app-secret-management
```

### Uninstalling skills

```bash
./install.sh --uninstall app-secret-management
./install.sh --uninstall --global --all app-secret-management
```

### Listing available skills

```bash
./install.sh --list
```

### Target directories

| Target | Project scope | Global scope |
|---|---|---|
| `--claude` (default) | `.claude/skills/` | `~/.claude/skills/` |
| `--codex` | `.codex/skills/` | `~/.codex/skills/` |
| `--agents` | `.agents/skills/` | skipped (no global convention) |

Project-scoped installs automatically add the target directory pattern to `.git/info/exclude` so symlinks stay out of the project's git history.

## Creating a new skill

1. Copy the template:
   ```bash
   cp -r skills/example-skill skills/my-new-skill
   ```

2. Rename the `name` field in `SKILL.md` frontmatter to match the directory name:
   ```yaml
   ---
   name: my-new-skill
   description: >-
     What this skill does and when to use it. Be specific about triggers —
     include keywords and contexts that should activate this skill.
   license: MIT
   metadata:
     author: natecostello
     version: "0.1"
   ---
   ```

3. Fill in the markdown sections with instructions, examples, and edge cases.

4. Keep `SKILL.md` under 500 lines. Move detailed material to `references/` and reference it from the main file.

5. Install it:
   ```bash
   ./install.sh my-new-skill
   ```

## Specification

Skills follow the [agentskills.io specification](https://agentskills.io/specification). Required frontmatter fields are `name` and `description`. The `name` must match the parent directory, use lowercase letters/numbers/hyphens, and be 1-64 characters.
