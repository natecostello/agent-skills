# Keyring Access by Framework

Read this reference when implementing the keyring layer for a specific framework
or app type. The app stores **one keychain entry** (the age identity key for a
local encrypted secrets file) — see the main skill and the
[encrypted store implementation guide](encrypted-store-implementation.md) for implementation details.

## Interpreted-Language CLIs (Python, Node, Ruby, etc.)

Access the keychain via OS-native CLI tools. Their binary identity is stable
(system-signed, fixed paths). Keyring libraries go through the interpreter
binary, whose identity changes on upgrades, venv rebuilds, and reinstalls —
each change requires manual re-authorization of the keychain entry.

**macOS** — `security` (Apple-signed, `/usr/bin/security`):

```python
import subprocess

SERVICE = "myapp"
ACCOUNT = "identity-key"

def keychain_set(value: str) -> None:
    subprocess.run(
        ["security", "add-generic-password", "-s", SERVICE, "-a", ACCOUNT,
         "-w", value, "-U"],
        check=True,
    )

def keychain_get() -> str | None:
    r = subprocess.run(
        ["security", "find-generic-password", "-s", SERVICE, "-a", ACCOUNT, "-w"],
        capture_output=True, text=True,
    )
    return r.stdout.strip() if r.returncode == 0 else None

def keychain_delete() -> None:
    r = subprocess.run(
        ["security", "delete-generic-password", "-s", SERVICE, "-a", ACCOUNT],
        capture_output=True,
    )
    if r.returncode != 0 and r.returncode != 44:
        raise RuntimeError(f"security delete failed (exit {r.returncode})")
```

> **Note:** `add-generic-password -w <value>` passes the value via process
> argv, briefly visible to other processes (e.g., `ps`). Since this is storing
> an age identity key (not the actual secrets), the exposure is limited. This is
> the standard `security` CLI interface.

**Linux** — `secret-tool` (freedesktop.org Secret Service):

```python
import subprocess

SERVICE = "myapp"
ACCOUNT = "identity-key"

def keychain_set(value: str) -> None:
    subprocess.run(
        ["secret-tool", "store", "--label", f"{SERVICE}/{ACCOUNT}",
         "service", SERVICE, "account", ACCOUNT],
        input=value.encode(), check=True,
    )

def keychain_get() -> str | None:
    r = subprocess.run(
        ["secret-tool", "lookup", "service", SERVICE, "account", ACCOUNT],
        capture_output=True, text=True,
    )
    return r.stdout.strip() if r.returncode == 0 else None

def keychain_delete() -> None:
    subprocess.run(
        ["secret-tool", "clear", "service", SERVICE, "account", ACCOUNT],
        check=True,
    )
```

**Cross-platform wrapper:** Detect the platform at startup and dispatch to the
appropriate functions above. For Windows (no binary-identity issue), the Python
`keyring` library is fine for accessing the single encryption key entry.

## Compiled-Language CLIs (Go, Rust, etc.)

Compiled binaries have stable identity — the binary IS the app — so
library-based keyring access works without the binary-identity problem.

**Rust:** `keyring` crate — maps `(service, user)` pairs to platform stores.
**Go:** `zalando/go-keyring` — wraps macOS Keychain, Windows Credential Manager,
Linux D-Bus Secret Service.

Use the app's name as the service name. One entry for the age identity key.

## Electron Apps

Use the built-in `safeStorage` API (available since Electron v15; VS Code
migrated from `keytar` to `safeStorage` in VS Code v1.80). This implements the
single-keychain-entry pattern natively — one keychain entry for encryption,
encrypted buffers in local storage.

```javascript
const { safeStorage } = require('electron');

if (safeStorage.isEncryptionAvailable()) {
  const encrypted = safeStorage.encryptString(secret);   // -> Buffer
  const decrypted = safeStorage.decryptString(encrypted); // -> string
}
```

`isEncryptionAvailable()` can return false before the `ready` event or on Linux
without a Secret Service provider. Handle this at startup.

## Tauri Apps

`tauri-plugin-keyring` wraps the Rust `keyring` crate. Also consider
`tauri-plugin-configurate`, which stores config on disk but keeps secret fields
in the OS keyring — plaintext never touches the filesystem.

## Native macOS (Swift)

Security framework: `SecItemAdd`, `SecItemCopyMatching`, `SecItemUpdate`,
`SecItemDelete`. Wrapper libraries: KeychainAccess, SwiftSecurity.

Prefer the data protection keychain (`kSecUseDataProtectionKeychain`) over
legacy file-based keychains — uses code signing entitlements instead of ACLs,
eliminating user prompts for apps in the same access group.

## Native Windows

DPAPI: `CryptProtectData`/`CryptUnprotectData`. Encryption is bound to the
logged-in user's credentials — no user interaction needed.

**Python:** `win32crypt.CryptProtectData()` from pywin32.
**.NET:** `ProtectedData` class.

## Password Manager Pipe Examples

Export/import composes with any password manager via stdin/stdout:

```bash
# LastPass
myapp secrets export --include-secrets | lpass edit --notes myapp/secrets
lpass show --notes myapp/secrets | myapp secrets import --force

# 1Password
myapp secrets export --include-secrets | op item edit myapp/secrets notes=-
op item get myapp/secrets --fields notes | myapp secrets import --force

# Bitwarden (bw CLI requires get/edit with JSON; adapt to your bw version)
myapp secrets export --include-secrets | bw get item myapp/secrets | \
  jq --arg notes "$(cat)" '.notes = $notes' | bw edit item myapp/secrets
bw get item myapp/secrets | jq -r '.notes' | myapp secrets import --force
```

## Background Services and Daemons

See the daemon section in the main SKILL.md for the decision framework. Summary
of keyring access by context:

| Context | Keyring access | Approach |
|---|---|---|
| LaunchAgent (macOS) | Full — user session | Normal keyring calls |
| systemd user service (Linux) | Full — user D-Bus session | Normal keyring calls |
| LaunchDaemon (macOS, root) | None — no user session | SOPS+age, PM SDK, or file-based keychain |
| systemd system service (Linux) | None — no D-Bus | SOPS+age, systemd credentials, or PM SDK |
| Headless Linux | Maybe — requires D-Bus setup | Start session explicitly, or bypass keyring |
