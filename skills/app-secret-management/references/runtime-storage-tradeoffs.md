# Encrypted Store Implementation

Read this reference when implementing the encrypted local store — the single
keychain entry + local encrypted file pattern.

## How It Works

One keychain entry holds an encryption key. All app secrets live in a local
encrypted file, encrypted with that key. At startup, the app reads the key from
the keychain, decrypts the file, and holds secrets in memory.

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

## Encrypted File Formats

### age-encrypted JSON (recommended for CLIs)

Simple, CLI-composable, well-audited encryption.

```python
import json
import os
import subprocess
from pathlib import Path

def encrypt_secrets(secrets: dict, key: str, path: str) -> None:
    """Encrypt secrets dict to file using age."""
    plaintext = json.dumps(secrets, indent=2)
    result = subprocess.run(
        ["age", "--encrypt", "--passphrase", "-o", path],
        input=plaintext, text=True, capture_output=True,
        env={**os.environ, "AGE_PASSPHRASE": key},
    )
    if result.returncode != 0:
        raise RuntimeError(f"age encrypt failed: {result.stderr}")

def decrypt_secrets(key: str, path: str) -> dict:
    """Decrypt secrets file using age."""
    result = subprocess.run(
        ["age", "--decrypt", path],
        capture_output=True, text=True,
        env={**os.environ, "AGE_PASSPHRASE": key},
    )
    if result.returncode != 0:
        raise RuntimeError(f"age decrypt failed: {result.stderr}")
    return json.loads(result.stdout)
```

Requires `age` CLI installed. Available via Homebrew (`brew install age`),
most Linux package managers, and as a static binary.

### Fernet (Python, no external tools)

Symmetric encryption from the `cryptography` package. Good when you don't
want to require `age` as a dependency.

```python
import json
from pathlib import Path

from cryptography.fernet import Fernet

def encrypt_secrets(secrets: dict, key: bytes, path: str) -> None:
    f = Fernet(key)
    plaintext = json.dumps(secrets).encode()
    Path(path).write_bytes(f.encrypt(plaintext))

def decrypt_secrets(key: bytes, path: str) -> dict:
    f = Fernet(key)
    ciphertext = Path(path).read_bytes()
    return json.loads(f.decrypt(ciphertext))

# Generate a new key (store this in keychain):
# key = Fernet.generate_key()
```

### SOPS-encrypted YAML

Best when secrets are mixed into config files. Only values are encrypted;
keys and structure remain readable for debugging.

```bash
# Encrypt (using age key stored in keychain)
sops --encrypt --age $(age-keygen -y key.txt) config.yaml > config.enc.yaml

# Decrypt
sops --decrypt config.enc.yaml
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

To rotate the encryption key:

1. Decrypt with old key
2. Generate new key
3. Re-encrypt with new key
4. Store new key in keychain (overwrites old)
5. Trigger auto-export (backup the new state)

This is a single keychain write — no ACL concerns.

## Encrypted Store vs. Encrypted Backup

The encrypted store is the **runtime** layer — the encryption key lives in the
keychain, secrets live in a local file. The password manager is the **durable
backup**. Don't use an encrypted file as a backup tier alongside a password
manager — that creates two sources of truth with sync conflicts.
