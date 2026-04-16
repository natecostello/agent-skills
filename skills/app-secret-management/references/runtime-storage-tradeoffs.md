# Runtime Storage: Direct Keyring vs. Encrypted Store

Read this reference when deciding how secrets are stored at runtime. Both
approaches are standard; the right one depends on the application.

## The Two Approaches

**Direct keyring** — one keychain entry per secret. `gh` and `docker` use this.

**Single key + encrypted store** — one keychain entry holds an encryption key,
all secrets live in a local encrypted file or database. VS Code and Electron
apps use this (via `safeStorage`).

## Comparison

| | Direct keyring | Single key + encrypted store |
|---|---|---|
| Implementation | Simple — just call keyring API | Extra layer: encrypt/decrypt + local file |
| Secret count | Best for small, stable sets (under ~10) | Better for large or growing sets (10+) |
| Bulk operations | Slow — one keychain call per secret | Fast — one unlock, then local I/O |
| Backup/export | Must enumerate keychain entries | Copy one file (or serialize one object) |
| Per-secret ACL | OS manages access per item | Single ACL on the encryption key |
| Failure blast radius | Lose one entry, lose one secret | Corrupt file, lose all secrets |
| Keychain pollution | One entry per secret in user's keychain | One entry total |

## When to Use Which

**Direct keyring** when the secret count is small and predictable (a handful of
API keys, a fixed set of service credentials). Simpler to implement, no file
format to maintain, and per-secret OS access control is a benefit.

**Encrypted store** when secrets are numerous or grow dynamically (one token per
linked institution, per-user credentials in a multi-account app). Avoids
keychain pollution, makes bulk export trivial, and is significantly faster for
apps that read many secrets at startup.

The tipping point is around 10 secrets for compiled apps. Below that, direct
keyring is simpler and the overhead is negligible. Above that, keychain
pollution and slow enumeration become real costs. Apps with dynamic/growing
secret counts (e.g., one token per linked account) should use encrypted store
from the start since the count is unbounded.

### Interpreted-language CLIs: lower tipping point

For CLI apps written in Python, Node, Ruby, or other interpreted languages, the
tipping point is lower — even a handful of direct keyring entries can be
painful. On macOS, keychain ACLs are tied to the binary that accessed each
entry. When the interpreter binary path changes (venv rebuild, version upgrade,
`nvm use`, etc.), macOS prompts for re-authorization **once per keychain
entry**. With direct keyring, this scales linearly with secret count: 3 secrets
= 3 prompts, 22 secrets = 22 prompts.

The encrypted store approach bounds this to a single re-authorization (for the
one encryption key entry), regardless of how many secrets are stored in the
local encrypted file. This makes encrypted store the safer default for
interpreted-language CLIs with more than 2-3 secrets.

Note: using OS CLI tools (`security` on macOS, `secret-tool` on Linux) instead
of library-based keyring access avoids the binary-identity problem entirely —
see [keyring-by-framework.md](keyring-by-framework.md). But minimizing keychain
entries via encrypted store is still good defensive design for resilience against
other ACL edge cases (code signing changes, keychain migrations).

## Encrypted Store Formats

- **age-encrypted JSON** — simple, CLI-composable. Encrypt with `age`, decrypt
  at startup using keychain-stored key or age identity file.
- **SQLite + safeStorage buffers** — Electron's approach. `safeStorage` encrypts
  each value, store the buffers in SQLite.
- **SOPS-encrypted YAML** — works well when secrets are mixed into config files.
  Only secret values are encrypted; keys and structure remain readable.

## Encrypted Store vs. Encrypted Backup — Not the Same Thing

The encrypted store pattern is the **runtime** layer — the encryption key lives
in the keychain, secrets live in a local file. The password manager is still the
durable backup. Don't confuse this with using an encrypted file as a backup tier
alongside a password manager — that creates two sources of truth with sync
conflicts. Only use built-in encryption as the backup tier if no password manager
is available (CI, containers).

Both runtime approaches feed into the same password manager backup tier — this
choice only affects local storage.
