# Keyring Access by Framework

Read this reference when implementing the keyring layer for a specific framework
or app type.

## Interpreted-Language CLIs (Python, Node, Ruby, etc.)

**macOS binary-identity problem:** macOS Keychain ties access control to the
binary that created each entry. Interpreted-language CLIs run through an
interpreter binary (`python3`, `node`, `ruby`) whose path changes on version
upgrades, venv rebuilds, `uv tool install`, `nvm use`, `rbenv` switches, etc.
When the path changes, macOS prompts for re-authorization — once per keychain
entry. This is a fundamental macOS security model constraint with no upstream fix.

**Recommendation:** Use OS-native CLI tools via subprocess. These are always
authorized (system-signed binaries with stable paths) and never trigger re-auth.

**macOS** — `security` (Apple-signed, always in `/usr/bin/`):

> **Note:** `-w` passes the password via process argv, which is briefly visible
> to other processes (e.g., `ps`). This is the standard `security` CLI interface
> and is generally accepted for CLI tools on macOS. For high-sensitivity secrets,
> consider the encrypted store approach (single keychain entry) to minimize
> exposure — see [runtime-storage-tradeoffs.md](runtime-storage-tradeoffs.md).

```python
import subprocess

def keychain_set(service: str, account: str, password: str) -> None:
    # -U updates the item if it already exists, or creates it if not
    subprocess.run(
        ["security", "add-generic-password", "-s", service, "-a", account,
         "-w", password, "-U"],
        check=True,
    )

def keychain_get(service: str, account: str) -> str | None:
    r = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
        capture_output=True, text=True,
    )
    return r.stdout.strip() if r.returncode == 0 else None

def keychain_delete(service: str, account: str) -> None:
    # Idempotent — succeeds silently if the entry doesn't exist
    subprocess.run(
        ["security", "delete-generic-password", "-s", service, "-a", account],
        capture_output=True,
    )
```

**Linux** — `secret-tool` (freedesktop.org Secret Service):
```python
import subprocess

def keyring_set(service: str, account: str, password: str) -> None:
    subprocess.run(
        ["secret-tool", "store", "--label", f"{service}/{account}",
         "service", service, "account", account],
        input=password.encode(), check=True,
    )

def keyring_get(service: str, account: str) -> str | None:
    r = subprocess.run(
        ["secret-tool", "lookup", "service", service, "account", account],
        capture_output=True, text=True,
    )
    return r.stdout.strip() if r.returncode == 0 else None

def keyring_delete(service: str, account: str) -> None:
    subprocess.run(
        ["secret-tool", "clear", "service", service, "account", account],
        check=True,
    )
```

**Cross-platform wrapper:** Detect the platform at startup and dispatch to the
appropriate functions above. For Windows (no binary-identity issue), the Python
`keyring` library is fine.

**Fallback — Python `keyring` library:** If OS CLI tools are unavailable, the
`keyring` library works but be aware of the macOS binary-identity issue. Every
Python binary path change (venv rebuild, version upgrade, `uv tool install`)
will trigger one re-authorization prompt per keychain entry. This is tolerable
for 1-2 secrets but painful at scale — see
[runtime-storage-tradeoffs.md](runtime-storage-tradeoffs.md) for mitigation via
encrypted store.

```python
import keyring

keyring.set_password("myapp", key, value)    # store
keyring.get_password("myapp", key)           # retrieve
keyring.delete_password("myapp", key)        # remove
```

## Compiled-Language CLIs (Go, Rust, etc.)

Compiled binaries have stable identity — the binary IS the app — so
library-based keyring access works without the binary-identity problem.

**Rust:** `keyring` crate — maps `(service, user)` pairs to platform stores.
**Go:** `zalando/go-keyring` — wraps macOS Keychain, Windows Credential Manager,
Linux D-Bus Secret Service.

Use the app's name as the service name. Keep it consistent across all secrets.

## Electron Apps

Use the built-in `safeStorage` API (available since Electron v15; VS Code
migrated from `keytar` to `safeStorage` in VS Code v1.80). Stores an
encryption key in the OS keychain, returns encrypted buffers for local storage.
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

## Local Web Apps

Call `keyring.get_password()` (or equivalent) at startup and hold secrets in
memory. No interactive prompts are possible mid-request. The initial secret must
have been stored by a process that could handle keychain ACL prompts (e.g., a
CLI setup command or first-run wizard).

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
