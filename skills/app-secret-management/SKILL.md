---
name: app-secret-management
description: >-
  Guides implementation of secret management for any local application (CLI,
  GUI, web app, daemon) using the system keyring + password manager pattern.
  Use when a project needs to store API keys, tokens, or credentials —
  especially when secrets must survive machine rebuilds. Triggers on: secret
  storage, keyring integration, credential backup, password manager
  export/import, Plaid tokens, API key management, machine migration, dotfile
  bootstrap, daemon secrets, Electron safeStorage, SOPS, age encryption, or
  any discussion of durable secret backup for local applications.
license: MIT
metadata:
  author: natecostello
  version: "3.1"
---

# App Secret Management

System keyring for runtime, password manager for durable backup. This is the
industry-standard approach used by `gh`, `aws`, `docker`, and VS Code — delegate
to existing infrastructure rather than building custom encryption.

Applies across app types (CLI, GUI, web app, daemon) — the keyring access method
and nag mechanism vary by context.

## Core Principles

1. **System keyring is the runtime store.** All secret reads come from the OS
   keyring (macOS Keychain, GNOME Keyring, Windows Credential Manager).

2. **Password manager is the durable backup.** On every secret mutation, auto-
   export to the user's password manager. On a new machine, one import restores
   everything.

3. **Never block the primary operation.** If the password manager is unavailable,
   the keyring operation succeeds and the user gets a warning. Think `git commit`
   (always works offline) vs `git push` (durable backup, can fail gracefully).

4. **Composability via stdin/stdout.** Export to stdout, import from stdin. Pipes
   through any password manager CLI (`lpass`, `op`, `bw`) without the app knowing
   which one. See [keyring-by-framework.md](references/keyring-by-framework.md)
   for pipe examples.

## Architecture

Runtime (keyring: direct or encrypted store) → auto-export → Password Manager (backup) → import on new machine

**Two runtime approaches** — direct keyring (one entry per secret) or single
keychain key + encrypted local store. Both are standard. Consult
[runtime-storage-tradeoffs.md](references/runtime-storage-tradeoffs.md) when
choosing between them.

## Implementation

### Keyring Layer

Use the platform's keyring abstraction. Never store secrets in plaintext config
files or databases. See
[keyring-by-framework.md](references/keyring-by-framework.md) for per-framework
code examples.

**Interpreted-language CLIs (Python, Node, Ruby):** Prefer OS CLI tools
(`security` on macOS, `secret-tool` on Linux) over library-based keyring access.
On macOS, keychain ACLs are tied to the interpreter binary path — when it
changes (venv rebuild, version upgrade, `nvm use`), every keychain entry
requires re-authorization. OS CLI tools are system-signed with stable paths and
never trigger re-auth. See the reference doc for code examples and fallback
guidance.

**Daemons:** If the service runs in user context (LaunchAgent, systemd user
service), keyring access works normally. If headless or root, the keyring may be
inaccessible — use one of these alternatives:

1. **SOPS + age** — encrypted config, decrypted at startup with a local identity
   file. Self-contained, no network or interactive unlock needed.
2. **Password manager SDK** (1Password, Bitwarden) — fetch at startup via SDK.
   Requires a bootstrap secret (service account token) stored on disk or in env,
   same trust model as an age identity file but adds network dependency.
3. **systemd credentials** (Linux) — kernel-protected, encrypted with TPM2 or
   local key, delivered via `$CREDENTIALS_DIRECTORY`.
4. **File-based keychain** (macOS) — dedicated `.keychain` file with password in
   System Keychain. More moving parts but works for true LaunchDaemons.

### Auto-Export on Mutation

Every command that creates, updates, or deletes a secret triggers auto-export
after the keyring operation succeeds. Auto-export serializes the app's **full
secret set** as JSON (secret names as keys, values as strings) and writes it to
the password manager item. This ensures the backup is always a complete snapshot.

Identify all mutation points: account linking, secret set/delete, migration from
legacy storage, token refresh.

The export command should require an `--include-secrets` flag to include actual
values in output — without it, export shows metadata only (key names, dates) to
prevent accidental disclosure when piping to a terminal.

Export is **fire-and-forget** — never add latency to the primary operation. If
it fails, set a dirty flag and move on.

### Warn + Nag Pattern

When auto-export fails, warn immediately but do not fail the operation. Record
pending secrets in a dirty flag file in the platform's app data directory
(`~/.local/share/myapp/` on Linux, `~/Library/Application Support/myapp/` on
macOS, `%APPDATA%/myapp/` on Windows). On successful export, clear it.

| App type | Warning | Persistent nag |
|---|---|---|
| CLI | Terminal message | Message on subsequent commands |
| GUI/Desktop | Toast / status bar | Badge or settings banner |
| Web app | Log at startup | Health endpoint flag |
| Daemon | syslog/journald | Health check endpoint |

### Configuration

```yaml
secrets:
  backup_backend: lastpass       # lastpass | 1password | bitwarden | none
  backup_item: "myapp/secrets"   # item name in password manager
```

Add these fields to the app's existing config file. `backup_backend: none`
disables auto-export (for CI or environments without a password manager).

### Restore on New Machine

```bash
lpass login user@example.com
lpass show --notes myapp/secrets | myapp secrets import --force
myapp secrets list  # verify
```

Automate in a dotfile manager (chezmoi `run_once`) for unattended bootstrap.

## Checklist

- [ ] All secret reads from system keyring or daemon alternative (see Keyring Layer)
- [ ] Runtime storage approach chosen (see [tradeoffs reference](references/runtime-storage-tradeoffs.md))
- [ ] Every mutation point triggers auto-export (fire-and-forget)
- [ ] Export to stdout / import from stdin with `--include-secrets` safety gate
- [ ] Failed export sets dirty flag; successful export clears it
- [ ] Nag mechanism matches app type
- [ ] Config supports `backup_backend: none`
- [ ] Restore works end-to-end on a clean keyring
- [ ] Daemon context verified: keyring accessible, or alternative tier chosen
- [ ] CI disables auto-export (`backup_backend: none`)
- [ ] Headless/CI: app falls back to env vars (e.g., `MYAPP_SECRET_<NAME>`) when keyring unavailable

## Edge Cases

- **Multiple machines** — import should merge by default: match by secret name,
  skip if same name already exists in keyring. `--force` for full overwrite.
- **Token refresh** — refreshed tokens are mutations; trigger auto-export.
- **Bulk migration** — export once at the end, not once per secret.
- **Keyring locked** — let the OS prompt for unlock. Daemons should fail clearly
  and fall back to cached values if available.
- **Headless/CI** — `backup_backend: none`, read secrets from env vars
  (`MYAPP_SECRET_<NAME>`) or CI secrets manager when keyring is unavailable.
- **macOS binary identity** — interpreted-language CLIs (Python, Node, Ruby)
  should use OS CLI tools to avoid re-authorization prompts when the interpreter
  binary path changes. See [keyring-by-framework.md](references/keyring-by-framework.md).
  For native apps, data protection keychain requires signed binary with
  entitlements. Test unsigned dev builds against legacy keychain.
- **Bootstrap secret for daemon SDK** — service account token stored on disk has
  same trust model as age identity file. Protect with filesystem permissions.
