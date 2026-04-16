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
  version: "4.0"
---

# App Secret Management

One keychain entry per app, password manager for durable backup. Delegate to
existing OS and password manager infrastructure rather than building custom
encryption.

Applies across app types (CLI, GUI, web app, daemon) — the keyring access method
and nag mechanism vary by context.

## Core Principles

1. **One keychain entry per app.** Store a single encryption key in the OS
   keychain. All secrets live in a local encrypted file, encrypted with that key.
   This bounds ACL exposure to one entry — if it ever needs re-authorization,
   it's one action, not one per secret.

2. **OS CLI tools for interpreted languages.** Python, Node, Ruby CLIs access
   the keychain via OS CLI tools (`security` on macOS, `secret-tool` on Linux),
   not keyring libraries. OS CLI tools have stable binary identity
   (system-signed, fixed paths). Keyring libraries go through the interpreter
   binary, whose identity changes on upgrades, venv rebuilds, and reinstalls.

3. **Password manager is the durable backup.** On every secret mutation,
   auto-export the full secret set to the user's password manager. On a new
   machine, one import restores everything.

4. **Never block the primary operation.** If the password manager is unavailable,
   the keyring operation succeeds and the user gets a warning. Think `git commit`
   (always works offline) vs `git push` (durable backup, can fail gracefully).

5. **Composability via stdin/stdout.** Export to stdout, import from stdin. Pipes
   through any password manager CLI (`lpass`, `op`, `bw`) without the app knowing
   which one. See [keyring-by-framework.md](references/keyring-by-framework.md)
   for pipe examples.

## Architecture

```
App startup:
  1. Read encryption key from keychain (single OS keychain entry)
  2. Decrypt local secrets file
  3. Secrets available in memory

Secret mutation:
  1. Update local encrypted file
  2. Auto-export full secret set → password manager (fire-and-forget)

New machine:
  1. Import from password manager → local encrypted file + keychain entry
```

## Implementation

### Keyring Layer

One keychain entry holds the encryption key for the local secrets file. See
[keyring-by-framework.md](references/keyring-by-framework.md) for per-framework
code examples.

**Interpreted-language CLIs (Python, Node, Ruby):** Access the keychain via OS
CLI tools (`security` on macOS, `secret-tool` on Linux). See the reference doc
for code examples.

**Compiled-language CLIs (Go, Rust):** Library-based keychain access is fine —
compiled binaries have stable identity.

**Electron:** Use the built-in `safeStorage` API, which implements this pattern
natively (one keychain entry for encryption, encrypted buffers in local storage).

**Daemons:** If the service runs in user context (LaunchAgent, systemd user
service), keychain access works normally. If headless or root, the keyring may be
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

### Encrypted Local Store

The local secrets file is encrypted with the key from the single keychain entry.
Format options:

- **age-encrypted JSON** — simple, CLI-composable. Encrypt with `age`, decrypt
  at startup using the keychain-stored key.
- **Fernet (Python)** — symmetric encryption from the `cryptography` package.
  Simple key management, no external tools needed.
- **SOPS-encrypted YAML** — works well when secrets are mixed into config files.
  Only secret values are encrypted; keys and structure remain readable.

The encrypted file lives in the app's data directory (`~/.local/share/myapp/` on
Linux, `~/Library/Application Support/myapp/` on macOS). Protect with filesystem
permissions (chmod 600).

### Auto-Export on Mutation

Every command that creates, updates, or deletes a secret triggers auto-export
after the local encrypted file is updated. Auto-export serializes the app's
**full secret set** and writes it to the password manager item. This ensures the
backup is always a complete snapshot.

Identify all mutation points: account linking, secret set/delete, migration from
legacy storage, token refresh.

The export command should require an `--include-secrets` flag to include actual
values in output — without it, export shows metadata only (key names, dates) to
prevent accidental disclosure when piping to a terminal.

Export is **fire-and-forget** — never add latency to the primary operation. If
it fails, set a dirty flag and move on.

### Warn + Nag Pattern

When auto-export fails, warn immediately but do not fail the operation. Record
the failure in a dirty flag file in the app's data directory. On successful
export, clear it.

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

- [ ] Single keychain entry holds encryption key (not one entry per secret)
- [ ] Local encrypted file stores all secrets
- [ ] Interpreted-language CLI uses OS CLI tools for keychain access
- [ ] Every mutation point triggers auto-export (fire-and-forget)
- [ ] Export to stdout / import from stdin with `--include-secrets` safety gate
- [ ] Failed export sets dirty flag; successful export clears it
- [ ] Nag mechanism matches app type
- [ ] Config supports `backup_backend: none`
- [ ] Restore verified end-to-end on a clean keychain with real data
- [ ] Daemon context verified: keychain accessible, or alternative tier chosen
- [ ] CI disables auto-export (`backup_backend: none`)
- [ ] Headless/CI: app falls back to env vars when keyring unavailable

## Edge Cases

- **Multiple machines** — import should merge by default: match by secret name,
  skip if same name already exists. `--force` for full overwrite.
- **Token refresh** — refreshed tokens are mutations; trigger auto-export.
- **Bulk migration** — export once at the end, not once per secret.
- **Keyring locked** — let the OS prompt for unlock. Daemons should fail clearly
  and fall back to cached values if available.
- **Headless/CI** — `backup_backend: none`, read secrets from env vars
  (`MYAPP_SECRET_<NAME>`) or CI secrets manager when keyring is unavailable.
- **Bootstrap secret for daemon SDK** — service account token stored on disk has
  same trust model as age identity file. Protect with filesystem permissions.
