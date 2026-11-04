# Music Section Architecture

## Purpose and status

Music is a section of Mira Library, alongside History and Science. It preserves and connects scores, complete œuvre catalogues, biographies, primary documents, criticism, recordings, and musicological studies. Musicology is one category within the Music shelf, not the name of the section.



Mira Library holds sources and develops source-grounded understanding. Mira Music applies that understanding to study, interpretation, teaching, curation, composition, and work with other media. The collection serves sustained musical inquiry beyond any one playlist or project.

## Collections

Collections are overlapping navigation views. A source may appear in several views without duplicate records or files.

| Collection | Scope |
|---|---|
| Composers and œuvre catalogues | Complete work inventories, thematic catalogues, chronology, catalogue concordances, attribution disputes, fragments, lost works, and revisions |
| Scores and editions | Manuscripts, first editions, critical and performing editions, full scores, parts, reductions, and editorial commentary |
| Biography and primary documents | Scholarly biographies, correspondence, diaries, interviews, memoirs, and contemporary testimony |
| Criticism and reception | Reviews, essays, periodical criticism, and historical reassessments across languages and eras |
| Theory and musicology | Textbooks and specialist studies of harmony, counterpoint, form, rhythm, orchestration, analysis, music history, aesthetics, and performance practice |
| Performance and recordings | Discographies, interpretive traditions, historical recordings, performer writings, and documented comparisons |

Begin with the great composers of the classical tradition while permitting expansion into neglected composers and other traditions. Greatness guides initial curatorial selection, not a permanent database classification. Grace Mar's repertoire and cover constraints belong to that project, not to the whole Library.

## Catalogue entities and fields

Separate a musical composition from its versions, editions, performances, and digital manifestations. Use stable internal identifiers independent of titles, catalogue numbers, filenames, and provider URLs. The fields below are a conceptual proposal, not a claim about current software support.

| Entity | Principal fields |
|---|---|
| Person | Stable ID; preferred name; original-script name and variants; dates and uncertainty; roles; authority references |
| Musical work | Stable ID; original and translated titles; attributed composer; attribution status and source; catalogue identifiers; composition dates; genre; instrumentation; ordered movements or components; completion and survival status |
| Version or arrangement | Stable ID; parent work; version title; reviser or arranger; date; instrumentation; nature of revision; supporting source |
| Documentary source | Stable ID; title; authors and roles; category; publication date; publisher or periodical; language; subjects; explicit composer and work references; selection rationale |
| Edition or translation | Stable ID; source or exact musical version; editor and other contributor roles; translator; edition statement; publication details; source edition; language; completeness; editorial and translation limitations |
| Performance event | Stable ID; date and venue where known; programme; performers and roles; exact works and versions; supporting sources |
| Recorded performance | Stable ID; exact work and version; performers and roles; event or session references when known; takes or editing information when documented; musical timings; sources of credits |
| Release | Stable ID; label; catalogue number; release date; ordered tracks and recording references; issue or reissue relationships; mastering information when documented |
| Manifestation or presentation | Stable ID; edition or content references; print, file, or upload format; binding or technical characteristics; provider identifier and URL where applicable; checked date; ordered contents and coverage |
| Holding | Stable ID; manifestation reference; holding institution or owner; copy or local file location; condition and completeness; acquisition date; checksum and byte count for files; inspection state |
| Document or content component | Stable ID; parent document or work where applicable; title; author and contributor roles; language; revision details; container membership and locators |
| Evidence assertion | Stable ID; subject and field or relationship asserted; value or claim; source and locator; language; qualification and uncertainty; verification method and check date |

Every record needs provenance and an update date. Use explicit unknown or uncertain values where appropriate; missing information must not become a guessed fact. Date fields retain known precision and distinguish composition, performance, recording, publication, release, and acquisition dates.

Catalogue identifiers are repeatable structures containing scheme, number, catalogue edition, and authority source. Preserve concordances and superseded numbering. No external numbering scheme replaces the Library work ID.

Movements and separately studied components receive addressable identifiers linked to their parent work. Prefaces, articles, translations, and movement extracts can be addressed within a larger document or presentation. Container membership records the component, container, order, locator, and coverage; membership is distinct from authorship or intellectual derivation. One component may occur in several containers without duplicating its identity. A multi-work volume, anthology, album, or upload can reference multiple works or recordings.

A YouTube upload is a digital presentation. Several uploads or releases may contain the same recorded performance; one upload may contain several recordings. A release catalogue number identifies an issue, not a performance. Unknown sessions, takes, or mastering details remain unknown. An association based on displayed credits must not be labelled an audio match. Different performances of the same composition remain distinct.

Store estimated composition duration separately from recorded musical duration and checked presentation runtime, including any introductions or applause when known. A timestamp belongs to the exact presentation inspected; it cannot automatically transfer to another upload or release.

Separate the intellectual edition from its printed or digital manifestations and individual holdings. A publisher listing, an online scan, and a privately saved file establish different access states. Preserve roles such as editor, fingering contributor, preface author, and translator. Record a publisher's editorial designation as an attributed claim. Another institution's holding does not establish a Mira Library holding.

## Multilingual criticism

Preserve the critic, article title, publication, issue or volume, date, pages, original language, and exact subject. The subject may be a composition, edition, concert, performer, or recording. Distinguish premiere responses, contemporary reviews, retrospective assessments, and later scholarship.

Keep original text and translation as separate, linked items. Identify the translator, translation method, source edition, and any abridgment. An automated translation is a reading aid with explicit provenance, not an unidentified substitute for the original.

When one file contains multiple languages, identify its language components and their locators without duplicating the file. Preserve qualifications in each language; a more categorical translation must not silently strengthen the source claim. Translation differences are not automatically disagreements between independent critics. Leave translation direction or attribution unknown when the source does not establish it.

Track signed essay dates, revision dates, edition dates, and file-check dates separately. A retained signature date does not establish the publication date of a revised document. Preserve evidence of revision without inventing when or by whom it occurred.

Record significant judgments with supporting passage locators and their qualifications. Preserve documented rebuttals, changes of mind, and later reassessments. Do not convert disagreement into a consensus score.

Select critics for an explicit contribution: historical influence, analytical depth, specialist knowledge, or a distinct critical tradition. Review the developing collection across languages and eras; online English-language availability alone must not define its scope. Numerical representation targets remain unset until roster design.

## Relationships and interpretation

Proposed relationship types include `composed_by`, `version_of`, `edition_of`, `translation_of`, `performs`, `reviews`, `discusses`, `responds_to`, and explicit container membership. Each relationship records its subject, object, evidence, and uncertainty. A stronger claim such as influence requires specific evidence; adjacency or shared vocabulary does not establish it.

Attach evidence to individual claims and relationships, not only to the whole record. Each assertion identifies its source, locator, language, reported wording or faithful paraphrase, uncertainty, verification method, and check date. Preserve conflicting assertions with their attribution; any preferred catalogue value needs an explicit basis. Distinguish publisher metadata, editorial judgment, documentary evidence, and directly inspected material. A source discovered through an index remains a candidate when its underlying content has not been inspected.

Mira's interpretations remain separately authored notes linked to the sources actually consulted. Distinguish score-based observations, documentary facts, a critic's judgment, provisional interpretation, and observations from audio actually inspected. A browser playing a video does not establish an audition.

Locators must fit their medium: page and passage for prose; edition, movement, measure and page for scores; exact recording and timestamp for audio. Measure numbering can differ across editions. Never manufacture locators or infer performance characteristics from metadata.

## Coverage and study states

| Dimension | What it establishes |
|---|---|
| Catalogue coverage | Works represented against a named catalogue and version, with an explicit scope and unresolved exceptions |
| Holdings coverage | Scores, editions, documents, or recordings actually held, including missing volumes, parts, pages, or movements |
| File verification | Whether a private payload is present, hash-verified, and inspected for identity and completeness |
| Study state | Whether an item has been read, score-studied, listened to, or assessed, with a bounded account of what was examined |
| Open gaps | Missing translations, uncertain attribution, incomplete source routes, or other limits |

A complete œuvre catalogue does not imply complete score holdings or study of every work. A saved file does not imply reading or listening. A complete edition of one work does not establish complete composer coverage. Retain the Library's distinction between registry representation, private payload presence, hash verification, and current reproducibility.

## Storage and existing owners

Use the shared Library registry as the intended catalogue authority, with Music navigation generated from governed metadata. Do not create a competing hand-maintained catalogue. A proposed `section: music` extension and the musical entities above require implementation review before use; current support is not established by this document.

Source files belong in the configured private Library store, following existing admission rules. Preserve original score scans and readable document originals with provenance. OCR supports discovery but does not replace notation; MusicXML or other derivatives must retain their relationship to an inspected original and their verification limits. Recording catalogue entries can remain link-only; this design initiates no media downloads.



This Music contract does not force musical periodization into History's era definitions. Use dates, subjects, and explicitly sourced musical-period labels where helpful. Reuse existing infrastructure where it fits; identify schema dependencies where it does not.

## Acceptance cases and next boundary

Before schema implementation or acquisition at scale, demonstrate that the design can represent:

1. One composition with multiple catalogue identifiers and a revised version.
2. Two score editions with different editorial claims and measure numbering.
3. An original-language review and a separately attributed translation.
4. Conflicting critical judgments with their respective supporting passages.
5. A single recording appearing in multiple releases and uploads, plus a multi-recording upload, without duplicate performances or inferred audio identity.
6. A collected volume containing multiple works and embedded documents, with separate manifestations and partial local holdings.
7. A lost or disputed work present in the catalogue without a falsely claimed score.
8. A multilingual document whose language versions differ in qualification, with unknown translators retained explicitly and separate signature and revision dates.
9. Competing claims about the same field, each retaining its evidence and an explicit basis for any preferred catalogue value.

The [Debussy catalogue example](debussy-catalogue-example.md) supplied the four refinements incorporated here: recording and release separation; edition, manifestation, and holding separation; claim-level evidence; and embedded multilingual document components. Its partial and untested cases remain open; incorporating its findings does not establish full acceptance or software support.

The next decision is whether to address a remaining acceptance case, design an initial reference roster, or authorize schema implementation. This contract grants none of those actions automatically. No registry mutation, source admission, catalogue activation, staging, commit, push, or publication is part of this revision.
