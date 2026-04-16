#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"

# --- Defaults ---
GLOBAL=false
UNINSTALL=false
DRY_RUN=false
LIST=false
TARGETS=()
SKILL_NAMES=()

# --- Usage ---
usage() {
  cat <<'EOF'
Usage: install.sh [OPTIONS] SKILL [SKILL...]

Install (symlink) agent skills into agent-specific directories.

Options:
  --global        Install to user-global scope instead of project scope
  --claude        Target Claude Code (default if no target specified)
  --codex         Target Codex
  --agents        Target Agents
  --all           Target all agents (claude + codex + agents)
  --uninstall     Remove symlinks instead of creating them
  --list          List available skills and exit
  --dry-run       Show what would happen without doing it
  -h, --help      Show this help message

Examples:
  ./install.sh app-secret-management           # Install to .claude/skills/
  ./install.sh --global my-skill               # Install to ~/.claude/skills/
  ./install.sh --codex --agents my-skill       # Install to .codex/ and .agents/
  ./install.sh --all my-skill other-skill      # Install to all targets
  ./install.sh --uninstall my-skill            # Remove symlink
  ./install.sh --list                          # Show available skills
  ./install.sh --dry-run --all my-skill        # Preview without changes
EOF
}

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --global)   GLOBAL=true; shift ;;
    --claude)   TARGETS+=("claude"); shift ;;
    --codex)    TARGETS+=("codex"); shift ;;
    --agents)   TARGETS+=("agents"); shift ;;
    --all)      TARGETS=("claude" "codex" "agents"); shift ;;
    --uninstall) UNINSTALL=true; shift ;;
    --list)     LIST=true; shift ;;
    --dry-run)  DRY_RUN=true; shift ;;
    -h|--help)  usage; exit 0 ;;
    -*)         echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    *)          SKILL_NAMES+=("$1"); shift ;;
  esac
done

# --- List mode ---
if $LIST; then
  echo "Available skills:"
  echo ""
  for skill_dir in "$SKILLS_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    skill_file="$skill_dir/SKILL.md"
    description=""
    if [ -f "$skill_file" ]; then
      # Parse description from YAML frontmatter, handling multi-line >- syntax
      description=$(awk '
        /^---$/ { frontmatter++; next }
        frontmatter == 1 && /^description:/ {
          # Check for inline value
          val = $0
          sub(/^description:[[:space:]]*/, "", val)
          # If it starts with >- or | or is empty, read continuation lines
          if (val ~ /^[>|]/) {
            val = ""
            while (getline > 0) {
              if (/^[a-zA-Z]/ || /^---$/) break
              line = $0
              sub(/^[[:space:]]+/, "", line)
              if (val != "") val = val " "
              val = val line
            }
          }
          print val
          exit
        }
        frontmatter >= 2 { exit }
      ' "$skill_file")
    fi
    printf "  %-24s %s\n" "$skill_name" "$description"
  done
  exit 0
fi

# --- Validate ---
if [ ${#SKILL_NAMES[@]} -eq 0 ]; then
  echo "Error: No skill names provided." >&2
  echo "Run with --list to see available skills, or -h for help." >&2
  exit 1
fi

# Default target is claude
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=("claude")
fi

# --- Resolve target directories ---
resolve_target_dir() {
  local target="$1"
  if $GLOBAL; then
    case "$target" in
      claude) echo "$HOME/.claude/skills" ;;
      codex)  echo "$HOME/.codex/skills" ;;
      agents)
        echo "Warning: --agents has no global convention, skipping." >&2
        echo ""
        ;;
    esac
  else
    case "$target" in
      claude) echo ".claude/skills" ;;
      codex)  echo ".codex/skills" ;;
      agents) echo ".agents/skills" ;;
    esac
  fi
}

# --- Git exclude helper ---
add_git_exclude() {
  local pattern="$1"
  local exclude_file=".git/info/exclude"
  [ -f "$exclude_file" ] || return 0
  if ! grep -qxF "$pattern" "$exclude_file" 2>/dev/null; then
    if $DRY_RUN; then
      echo "  [dry-run] Would append '$pattern' to $exclude_file"
    else
      echo "$pattern" >> "$exclude_file"
      echo "  Added '$pattern' to $exclude_file"
    fi
  fi
}

# --- Counters ---
installed=0
uninstalled=0
skipped=0
errors=0

# --- Process each skill × target ---
for skill_name in "${SKILL_NAMES[@]}"; do
  skill_source="$SKILLS_DIR/$skill_name"
  if [ ! -d "$skill_source" ]; then
    echo "Error: Skill '$skill_name' not found in $SKILLS_DIR/" >&2
    errors=$((errors + 1)) || true
    continue
  fi

  for target in "${TARGETS[@]}"; do
    target_dir="$(resolve_target_dir "$target")"
    [ -z "$target_dir" ] && continue

    target_path="$target_dir/$skill_name"

    if $UNINSTALL; then
      # --- Uninstall ---
      if [ -L "$target_path" ]; then
        if $DRY_RUN; then
          echo "[dry-run] Would remove symlink: $target_path"
        else
          rm "$target_path"
          echo "Removed: $target_path"
        fi
        uninstalled=$((uninstalled + 1)) || true
      elif [ -e "$target_path" ]; then
        echo "Warning: $target_path exists but is not a symlink, skipping." >&2
        skipped=$((skipped + 1)) || true
      else
        echo "Already absent: $target_path"
        skipped=$((skipped + 1)) || true
      fi
    else
      # --- Install ---
      if [ -L "$target_path" ]; then
        current_target="$(readlink "$target_path")"
        if [ "$current_target" = "$skill_source" ]; then
          echo "Already installed: $target_path -> $skill_source"
          skipped=$((skipped + 1)) || true
          continue
        else
          echo "Warning: $target_path points to $current_target, replacing."
          if ! $DRY_RUN; then
            rm "$target_path"
          fi
        fi
      elif [ -e "$target_path" ]; then
        echo "Error: $target_path exists and is not a symlink, skipping." >&2
        errors=$((errors + 1)) || true
        continue
      fi

      if $DRY_RUN; then
        echo "[dry-run] Would symlink: $target_path -> $skill_source"
      else
        mkdir -p "$target_dir"
        ln -s "$skill_source" "$target_path"
        echo "Installed: $target_path -> $skill_source"
      fi
      installed=$((installed + 1)) || true

      # Add target dir pattern to .git/info/exclude for project-scoped installs
      if ! $GLOBAL; then
        case "$target" in
          claude) add_git_exclude ".claude/skills/" ;;
          codex)  add_git_exclude ".codex/skills/" ;;
          agents) add_git_exclude ".agents/skills/" ;;
        esac
      fi
    fi
  done
done

# --- Summary ---
echo ""
if $UNINSTALL; then
  echo "Done: $uninstalled removed, $skipped skipped, $errors errors."
else
  echo "Done: $installed installed, $skipped skipped, $errors errors."
fi

exit $((errors > 0 ? 1 : 0))
