---
name: app-secret-management
description: >-
  Guides implementation of CLI secret management using the system keyring +
  password manager pattern. Use when a project needs to store API keys, tokens,
  or credentials — especially when secrets must survive machine rebuilds. Triggers
  on: secret storage, keyring integration, credential backup, password manager
  export/import, Plaid tokens, API key management, machine migration, dotfile
  bootstrap, or any discussion of durable secret backup for CLI tools.
license: MIT
metadata:
  author: natecostello
  version: "1.0"
---

# App Secret Management

A reusable pattern for CLI applications that manage secrets: **system keyring for
runtime, password manager for durable backup**. This is the industry-standard
approach used by tools like `gh`, `aws`, and `docker` — delegate to existing
infrastructure rather than building custom encryption.

## Core Principles

1. **System keyring is the runtime store.** All secret reads at runtime come from
   the OS keyring (macOS Keychain, GNOME Keyring, Windows Credential Manager).
   Fast, secure, no passphrase prompts.

2. **Password manager is the durable backup.** On every secret mutation
   (create/update/delete), auto-export to the user's password manager. This is
   the recovery path — on a new machine, one import restores everything.

3. **Never block the primary operation.** If the password manager is unavailable
   (not installed, not logged in, network down), the keyring operation succeeds
   and the user gets a warning. Think `git commit` (always works offline) vs
   `git push` (the durable backup, can fail without blocking work).

4. **Composability via stdin/stdout.** Export produces text on stdout, import
   reads from stdin. This lets users pipe through any password manager CLI
   (`lpass`, `op`, `bw`, `pass`) without the app needing to know which one.

## Why Not Encrypted Files?

If the user already has a password manager, adding an age/GPG-encrypted file
creates two sources of truth with sync conflicts. Tools like `pass` and `gopass`
ARE the password manager — they replace LastPass, not supplement it. Tools that
already have a password manager delegate to it.

Only consider built-in encryption if the app must work in environments with no
password manager at all (CI pipelines, containers). In that case, treat it as
the password manager tier, not a third tier.

## Architecture

```
User runs command     ──►  Keyring (runtime)
  that mutates a            │
  secret                    ▼
                       Password Manager (durable backup, auto)
                            │
New machine            ◄────┘  (import restores to keyring)
```

## Implementation Guide

### 1. Keyring Layer

Use the platform's keyring abstraction. The app should never store secrets in
config files, environment variables, or databases.

**Python:** `keyring` library (auto-detects backend)
```python
import keyring

keyring.set_password("myapp", key, value)    # store
keyring.get_password("myapp", key)           # retrieve
keyring.delete_password("myapp", key)        # remove
```

**Node.js:** `keytar` library
**Rust:** `keyring` crate
**Go:** `zalando/go-keyring`

The service name (first arg) should be the app's name. Keep it consistent —
every secret for the app uses the same service name.

### 2. Auto-Export on Mutation

Every command that creates, updates, or deletes a secret should trigger an
auto-export after the keyring operation succeeds. Identify all mutation points
in the codebase:

- Account linking / OAuth token acquisition
- Manual secret set commands
- Secret deletion
- Migration from legacy storage (config files, env vars)
- Token refresh (if the app stores refreshed tokens)

The export should be **fire-and-forget** — do not add latency to the primary
operation. If the export fails, set a dirty flag (see section 4) and move on.

### 3. Export/Import via stdin/stdout

The export format should be human-readable and machine-parseable. JSON is the
default choice:

```json
{
  "service": "myapp",
  "exported_at": "2025-01-15T10:30:00Z",
  "secrets": {
    "api_key": "sk-...",
    "plaid_access_token_chase": "access-prod-...",
    "plaid_access_token_vanguard": "access-prod-..."
  }
}
```

**Export command** writes to stdout:
```bash
myapp secrets export --include-secrets
```

**Import command** reads from stdin:
```bash
myapp secrets import --force < secrets.json
```

This composes with any password manager:
```bash
# Backup to LastPass
myapp secrets export --include-secrets | lpass edit --notes myapp/secrets

# Restore from LastPass
lpass show --notes myapp/secrets | myapp secrets import --force

# Backup to 1Password
myapp secrets export --include-secrets | op item edit myapp/secrets notes=-

# Restore from 1Password
op item get myapp/secrets --fields notes | myapp secrets import --force
```

The `--include-secrets` flag is a safety gate — without it, export shows
metadata only (key names, creation dates) so users don't accidentally pipe
secrets to a terminal.

### 4. Warn + Nag Pattern

When the password manager is unavailable during auto-export:

**Immediately:** Warn, but do not fail the command.
```
✓ Secret stored in keyring.
⚠ Backup skipped (LastPass not logged in).
  Run `myapp secrets export` when available.
```

**Set a dirty flag** that records which secrets are pending backup:
```
~/.local/share/myapp/backup_pending.json
```
```json
{
  "pending": ["api_key", "plaid_access_token_chase"],
  "since": "2025-01-15T10:30:00Z"
}
```

**On subsequent commands**, show a persistent reminder:
```
⚠ 2 secrets not backed up. Run `myapp secrets export` or log in to your password manager.
```

**On successful export**, clear the dirty flag.

This follows the git model: `git commit` always works, your shell prompt shows
"3 commits ahead" until you push, and `git push` clears the state.

### 5. Configuration

Add a secrets section to the app's config file:

```yaml
secrets:
  backup_backend: lastpass       # lastpass | 1password | bitwarden | none
  backup_item: "myapp/secrets"   # item name/path in the password manager
```

- `backup_backend: none` disables auto-export entirely (opt-out for CI or
  environments where no password manager exists).
- The backend name maps to the CLI tool used for piping (`lpass`, `op`, `bw`).
- Keep the config minimal — the app only needs to know which tool to call and
  what to name the item.

### 6. Restore on New Machine

The full restore flow:

```bash
# 1. Install the app
# 2. Log in to password manager
lpass login user@example.com

# 3. Restore all secrets in one command
lpass show --notes myapp/secrets | myapp secrets import --force

# 4. Verify
myapp secrets list
```

This can be automated in a dotfile manager (chezmoi `run_once` script, or
equivalent) for fully unattended machine bootstrap.

## Testing Considerations

- **Unit tests**: Mock the keyring backend. Test that mutation commands trigger
  export. Test that export failure sets the dirty flag without failing the
  command.
- **Integration tests**: Use a test keyring backend (most keyring libraries
  support in-memory or file-based backends for testing).
- **CI**: Set `backup_backend: none` in CI config so tests don't try to call
  password manager CLIs.
- **Manual verification**: After implementing, run the full cycle: set a secret,
  verify it's in the keyring, export, delete from keyring, import, verify
  it's restored.

## Checklist

When implementing this pattern in a project, verify each item:

- [ ] All secret reads come from the system keyring (no config files, no env vars)
- [ ] Every mutation point triggers auto-export
- [ ] Auto-export is fire-and-forget (never blocks or slows the primary operation)
- [ ] Export writes to stdout, import reads from stdin
- [ ] Export has a safety gate (`--include-secrets` or equivalent)
- [ ] Failed export sets a dirty flag with pending secret names
- [ ] Subsequent commands show a nag message when secrets are pending backup
- [ ] Successful export clears the dirty flag
- [ ] Config supports `backup_backend: none` to disable auto-export
- [ ] Restore from password manager works end-to-end on a clean keyring
- [ ] CI config disables auto-export

## Edge Cases

- **Multiple machines**: If Machine A links a new account while Machine B has a
  stale backup, importing the stale backup on Machine A would overwrite the new
  token. Import should merge by default (add missing, skip existing) with a
  `--force` flag for full overwrite. Document this clearly.

- **Token refresh**: If the app refreshes tokens (e.g., OAuth refresh tokens),
  the refreshed token is a mutation — trigger auto-export. Otherwise the backup
  goes stale silently.

- **Bulk migration**: When migrating secrets from legacy storage (config file,
  env vars), treat the entire migration as a single mutation — export once at
  the end, not once per secret.

- **Keyring locked**: On some systems the keyring may be locked (e.g., after
  sleep). The keyring library will prompt for unlock. This is expected OS
  behavior — do not try to work around it.

- **Headless/CI**: No keyring available. Use `backup_backend: none` and inject
  secrets via environment variables or a CI secrets manager. The app should
  support reading from env vars as a fallback when no keyring is available.
