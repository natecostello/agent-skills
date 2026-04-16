# Keyring Access by Framework

Read this reference when implementing the keyring layer for a specific framework
or app type.

## CLI and Library-Based Apps

**Python:** `keyring` library (auto-detects backend: macOS Keychain, Windows
Credential Locker, Linux Secret Service via D-Bus)
```python
import keyring

keyring.set_password("myapp", key, value)    # store
keyring.get_password("myapp", key)           # retrieve
keyring.delete_password("myapp", key)        # remove
```

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

**Python on macOS:** `pyobjc-framework-Security` for direct bindings to
`SecItemAdd`/`SecItemCopyMatching` without shelling out to `/usr/bin/security`.

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
