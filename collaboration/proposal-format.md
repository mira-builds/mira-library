# Shelf proposal format

Each proposal is a UTF-8 JSON object, at most 64 KiB, in
`contributions/<shelf-id>/<candidate-id>.json`. The filename and object identities
must match the stable [shelf bindings](shelves.json).

Required fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `shelf_id`, `source_id`, `candidate_id` | Stable shelf/source and lowercase filename identity |
| `work_title`, `language`, `edition`, `translator` | Exact witness; state `unknown` or `not-applicable` honestly |
| `source_url` | Public HTTP(S) edition/source URL without credentials or signed tokens |
| `proposed_coverage` | `complete-work`, `partial-work`, `selected-passages`, `fragmentary` or `unknown` |
| `inspection_status` | `located` or `inspected`; never `admitted` |
| `inspection_notes` | What was actually checked, including endings, difficult content and limits |
| `payload` | `null` for located-only; inspected files require `sha256`, positive integer `bytes`, and `encoding` |

The encoding can explicitly say `not-applicable (PDF)` when inspecting a binary
original; this does not make the file an admitted text derivative. No extra
fields, duplicate JSON keys, code attachments, private paths or raw source bodies
are accepted. Modern edition availability does not grant redistribution rights.
Schema checks do not verify truth, a download or the reliability of a translation.

Example identity layout: `contributions/twain-shelf/edition-one.json`. Obtain
actual metadata rather than copying fabricated hashes from a template. Use the
assigned issue to agree work/language scope before collecting evidence.
