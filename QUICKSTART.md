# Windows collaborator quick start

Open PowerShell in the repository folder. Python 3.11 or newer is required; no additional packages are
needed. Your archive must already exist outside the repository, with its registered filenames intact.
Obtain missing texts through your established authorized sources; the tool does not download them.

## Browse without an archive

```powershell
python --version
python mira_library.py list --query Machiavelli
python mira_library.py show LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI --json
```

The record lists body identifiers, edition, provenance and rights metadata. Catalog presence does not
establish local availability. Every catalog record can be inspected without connecting texts.

## Connect your archive

```powershell
$env:MIRA_LIBRARY_TEXT_ROOT = Read-Host 'Enter the full path to your existing archive folder'
python mira_library.py verify
```

The setting lasts for this PowerShell session. Alternatively, add `--text-root` followed by the folder
path to a `verify` or `read` command. Choose the folder containing the registered relative filenames.

Verification checks digests and lengths without changing files. An incomplete archive can still supply
individually verified texts. `missing` means a registered file was not found; `hash-mismatch` means
different bytes were found. `unavailable` describes a source/body not admitted for reading. Do not rename
an unrelated edition to satisfy a missing filename or disable integrity checks.

## Read a real passage

This example uses Machiavelli's *The Prince*, body `LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI-PG10827`.
It requires that registered body in your archive.

```powershell
python mira_library.py verify --source LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI --body LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI-PG10827
python mira_library.py read LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI-PG10827 --query prince --json
```

Inspect the passage, context, edition and translator. Its locator binds the passage to the exact body
and bytes. It is an electronic locator, not an invented printed page number.

## Replay the locator

Paste this entire PowerShell block. It obtains a passage and replays its returned locator using Python's
argument handling, avoiding differences in PowerShell JSON quoting. It writes no files.

```powershell
@'
import json
import subprocess
import sys

base = [sys.executable, 'mira_library.py', 'read',
        'LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI',
        'LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI-PG10827']
result = json.loads(subprocess.check_output(base + ['--query', 'prince', '--json']))
if not result.get('passages'):
    raise SystemExit('No passage returned; check the archive and query result.')
passage = result['passages'][0]
replayed = json.loads(subprocess.check_output(
    base + ['--locator-json', json.dumps(passage['locator']), '--json']))
assert replayed['passages'][0]['text'] == passage['text']
assert replayed['passages'][0]['locator'] == passage['locator']
print('Verified: the locator reproduced the same passage.')
'@ | python -
```

Select other source/body IDs using `list` and `show`. Preserve the returned locator with citations and
check each edition's quotation terms. A locator can be replayed on another computer holding the same
registered bytes, even when the archive folder has a different absolute path.

## Troubleshooting and completion

- **Python is unavailable:** install it, reopen PowerShell and check `python --version`.
- **Reading fails:** check the folder setting and that body's verification result.
- **The folder moved:** set `MIRA_LIBRARY_TEXT_ROOT` again; no catalog edits are needed.
- **No passage matches:** try a word present in the selected edition. Search is lexical, not semantic or translated.
- **A file differs:** retain it separately and obtain the registered edition; do not bypass the checksum.

The walkthrough is complete when you can browse, verify a body, inspect a passage and replay its locator
without assistance. [Return to the repository guide](README.md).
