# Mira Library

The canonical public collaboration repository is
[mira-builds/mira-library](https://github.com/mira-builds/mira-library).
Use [the master index](library/library-index.md) to find an author shelf, then
follow [CONTRIBUTING](CONTRIBUTING.md) and the [initial assignments](collaboration/assignments/README.md).

This is a public catalog and standalone read-only passage reader. Core remains
the collection admission and curation authority. Source texts, scans, private
profiles, operational records and Core Git history are not included.

The incoming destructive mirror must be retired before this transition is
published. Proposals are reviewed data, kept outside the released collection
inventory; accepting a proposal does not itself admit text or change a score.
This collaboration baseline derives from public commit
`1cfbff19d70db367a3d89ce8fd5a62576c4ca25d` (270 records, 823 body records).
Newer Core working content requires a separately reviewed export.

## Use

Requires **Python 3.11 or newer**; no third-party runtime packages are required. Retrieval works offline.
Clone the repository, or choose **Code → Download ZIP** on GitHub and extract it. Open a terminal in
the resulting folder. There is no installer, browser application or AI account requirement.

```powershell
git clone https://github.com/mira-builds/mira-library.git
cd mira-library
python --version
```

Skip the Git commands if you downloaded the ZIP. If Python is unavailable, install it from
[python.org](https://www.python.org/downloads/) and reopen the terminal.
Follow the [Windows collaborator quick start](QUICKSTART.md) for archive setup and a real passage example.
Catalog browsing needs no archive:

```sh
python mira_library.py list --query Machiavelli
python mira_library.py list --era colonial --json
python mira_library.py show LIB-COLONIAL-AUTHORITY-080-MACHIAVELLI --json
```

Use source and body identifiers returned by `list` and `show` when selecting another work.
`list --query` searches metadata. `read --query` searches passages within one selected body; this version
does not provide collection-wide full-text search or synthesized answers.
Use the complete `locator` object from a reading result to replay that passage; the quick start supplies
a PowerShell-safe example that avoids native JSON quoting differences.
The archive may also be selected through `MIRA_LIBRARY_TEXT_ROOT`; an explicit `--text-root` takes precedence.
There is no implicit machine-specific archive location. Metadata browsing needs no archive.

Keep your archive outside this checkout. Preserve the relative filenames in `library-text://` references.
The reader verifies SHA-256 and byte length before returning passages. It never downloads or changes texts.
A missing body is reported separately from an unavailable catalog entry or a hash mismatch.
Source status describes the catalog's admitted copy; `verify` establishes availability in your supplied archive.

| Result | Meaning |
|---|---|
| `verified` | Local bytes match the admitted body. |
| `unavailable` | No body is registered, or the body is not admitted for reading. |
| `missing` | An admitted body is absent from the connected folder. |
| `hash-mismatch` | A file exists but its digest or length differs. |
| `unconfigured` / `invalid-root` | Select an existing external archive directory. |
| `no-match` | No matching passage was returned from the selected verified text. |

Verification reports metadata-only sources and unavailable bodies separately. Missing or mismatched
admitted bodies cause a nonzero exit status; metadata-only entries do not. An empty search result is
not an integrity failure. Byte verification establishes source identity, not the truth of its claims.

## Maintenance

This is a maintained export of an authoritative upstream collection. Source corrections belong upstream;
the export process stops if an exporter-owned destination file has been edited independently.
All published source and body identifiers remain stable. Private research and operational records are omitted.
`release.json` records catalog counts and checksums for the other public files, excluding itself.

Run `python -B checks.py` to validate catalog identities, body metadata, release checksums and local links
without access to archive texts. Add `--tracked` to check the Git file inventory in a clean checkout.
Run `python -B -m unittest discover -s tests -v` to test the standalone reader and catalog checks.
Tests use synthetic texts in external temporary storage.
GitHub Actions runs both checks on pushes and pull requests, on Windows and Linux with Python 3.11 and 3.14.
The workflow has read-only repository access and needs no archive, API credentials or third-party Python packages.
Automated setup checks do not establish that an independent collaborator has completed the walkthrough.

Civilization/era browsing interfaces, saved research collections and optional cited conversation remain
deferred directions. This first release delivers the repository and portable retrieval foundation.

## Attribution and rights

Catalog records preserve source, translation, edition and license metadata. Those records are not a grant
of redistribution rights. Follow each source edition's terms. The passage reader preserves the existing
Mira Library `library-passage-v1` locator format. No general open-source license is asserted by this preparation.
