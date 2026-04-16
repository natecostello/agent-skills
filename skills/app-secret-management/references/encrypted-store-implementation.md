# Encrypted Store Implementation

Read this reference when implementing the encrypted local store — the single
keychain entry + local encrypted file pattern.

## How It Works

One keychain entry holds an age identity key (`AGE-SECRET-KEY-1...`). All app
secrets live in a local encrypted file, encrypted to that identity's public
recipient. At startup, the app reads the identity key from the keychain,
decrypts the file, and holds secrets in memory.

This is the same pattern VS Code uses (via Electron `safeStorage`): one keychain
entry for encryption, encrypted buffers in local storage.

## Why One Entry

Each keychain entry is an independent ACL. On macOS, keychain ACLs are tied to
the binary that accessed the entry. If the binary changes (interpreter upgrade,
venv rebuild, app reinstall), every entry requires manual re-authorization —
one password prompt per entry, each requiring the user's login password.

With one entry, re-authorization is one prompt. With twenty entries, it's twenty
prompts. The encrypted store pattern makes this constant regardless of how many
secrets the app manages.

## Encryption Format: age

Use the **age** encryption format everywhere. One standard across all languages,
interoperable files.

**Use identity keys, not passphrase mode.** Age passphrase mode runs scrypt (a
deliberately slow KDF) on every decrypt — roughly 1 second with age's default
parameters, which are fixed in the spec and not tunable. Since the keychain
already stores a high-entropy machine-generated key, scrypt's brute-force
protection is wasted. Identity key mode uses X25519 key agreement + symmetric
decrypt, which is effectively instant.

The keychain stores the identity key string (a single ~74-character
`AGE-SECRET-KEY-1...` value). The public recipient needed for encryption is
derived on the fly from the identity — no separate key to manage.

### Python — `pyrage` library

Rust-backed Python bindings for age. Pre-built wheels on PyPI — no Rust
toolchain or external CLI needed.

```python
import json
from pathlib import Path

import pyrage
from pyrage import x25519

def generate_identity() -> str:
    """Generate a new age identity key. Store the returned string in the keychain."""
    return str(x25519.Identity.generate())

def encrypt_secrets(secrets: dict, identity_str: str, path: str) -> None:
    identity = x25519.Identity.from_str(identity_str)
    recipient = identity.to_public()
    plaintext = json.dumps(secrets).encode()
    Path(path).write_bytes(pyrage.encrypt(plaintext, [recipient]))

def decrypt_secrets(identity_str: str, path: str) -> dict:
    identity = x25519.Identity.from_str(identity_str)
    ciphertext = Path(path).read_bytes()
    return json.loads(pyrage.decrypt(ciphertext, [identity]))
```

### Non-Python CLIs / shell scripts — `age` CLI

The keychain stores the age identity key (`AGE-SECRET-KEY-1...`). Write it to a
temporary file for the `age` CLI, or pipe it via process substitution.

```bash
# Generate identity (once, during first-run setup)
age-keygen 2>/dev/null  # outputs AGE-SECRET-KEY-1... to stdout
# Store the secret key line in the keychain; derive the recipient:
RECIPIENT=$(echo "$IDENTITY_KEY" | age-keygen -y)

# Encrypt
echo '{"api_key": "sk-..."}' | age --encrypt --recipient "$RECIPIENT" -o secrets.age

# Decrypt (pipe identity via process substitution — no temp file on disk)
age --decrypt --identity <(echo "$IDENTITY_KEY") secrets.age
```

Available via Homebrew (`brew install age`), most Linux package managers, and
as a static binary.

### Config files with mixed secrets — SOPS + age

Only values are encrypted; keys and structure remain readable for debugging.

```bash
# After loading the age identity key from the keychain:
#   IDENTITY_KEY=AGE-SECRET-KEY-1...
RECIPIENT=$(echo "$IDENTITY_KEY" | age-keygen -y)

# Encrypt
sops --encrypt --age "$RECIPIENT" config.yaml > config.enc.yaml

# Decrypt
SOPS_AGE_KEY="$IDENTITY_KEY" sops --decrypt config.enc.yaml
```

## File Location

Store the encrypted file in the app's data directory:

| Platform | Path |
|---|---|
| macOS | `~/Library/Application Support/myapp/secrets.age` |
| Linux | `~/.local/share/myapp/secrets.age` |
| Windows | `%APPDATA%/myapp/secrets.age` |

Protect with filesystem permissions (chmod 600 on Unix).

## Key Rotation

To rotate the identity key:

1. Decrypt with old identity
2. Generate new identity (`x25519.Identity.generate()` / `age-keygen`)
3. Re-encrypt with new identity's public recipient
4. Store new identity key string in keychain (overwrites old)
5. Trigger auto-export (backup the new state)

This is a single keychain write — no ACL concerns.

## Encrypted Store vs. Encrypted Backup

The encrypted store is the **runtime** layer — the encryption key lives in the
keychain, secrets live in a local file. The password manager is the **durable
backup**. Don't use an encrypted file as a backup tier alongside a password
manager — that creates two sources of truth with sync conflicts.
