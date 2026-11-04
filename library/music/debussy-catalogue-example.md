# Debussy Catalogue Architecture Test

## Result and scope

The [Music architecture](architecture.md) can distinguish a composition, its versions, printed editions, and recording uploads. This bounded example identifies four refinements before implementation: separate recordings from releases; separate intellectual editions from physical or digital holdings; preserve evidence at the claim and language level; and represent embedded documents and components without duplicating their containers.

This is a manually reviewed design example, not an executable schema test or an admitted Library record. Example IDs below are local to this document and reserve no production identifiers. Research checked on 2026-10-01. Only this example file was created; the architecture and live registry were not modified. No source files were downloaded into the Library, purchased, admitted, or published, and no recording was auditioned.

## Work and version records

| Example ID | Entity | Proposed representation and evidence |
|---|---|---|
| P1 | Person | Claude Debussy; composer and author of the solo transcription. Separate these roles from performers and edition editors. [H1], [H2] |
| W1 | Musical work | Six Épigraphes antiques; one cycle with six ordered movements. [H1], [H2] |
| V1 | Version | W1 for one piano, four hands; two players. [H2] |
| V2 | Version | W1 for solo piano; one player; composer transcription, not a separate unrelated composition. [H1], [H3] |
| C1 | Catalogue reference | Lesure 1977, number 131. [H3] |
| C2 | Catalogue reference | Lesure 2003, number 139. [H3] |

The catalogue number needs both a scheme edition and a displayed label: Henle uses L. 139 (131), while IMSLP labels the newer number CD and the older number L. Preserve those source conventions rather than normalizing the prefix alone. The cited catalogues themselves were not inspected. [H3], [I1]

Version is broader than revision. This example establishes a change of performing forces; it does not demonstrate a later authorial revision superseding an earlier text. An exact year for each version's composition remains unset here.

Movement records belong to W1, with version-specific score and recording locators attached separately. A movement number must not be treated as a timestamp or page number.

## Edition and holding records

| Example ID | Entity | Bibliographic fields | Holdings state |
|---|---|---|---|
| E1 | Edition of V2 | Henle HN 402; editor Ernst-Günter Heinemann; piano fingering Hans-Martin Theopold; preface François Lesure; publisher labels it Urtext. [H1] | Publisher metadata read; complete score not inspected or held |
| E2 | Edition of V1 | Henle HN 408; editor Ernst-Günter Heinemann; piano fingering Andreas Groethuysen; preface François Lesure. [H2] | Publisher metadata read; complete score not inspected or held |
| E3 | Candidate edition of V2 | BnF identifies a Durand issue dated [1994], transcribed by the composer. [B1] | Discovery-only: indexed record found, direct catalogue retrieval failed; not promoted to verified edition |
| D1 | Embedded documentary source | Lesure's preface associated with E1. [H3] | Publisher PDF text inspected online; no Library payload |
| F1 | Digital manifestation | Publisher PDF containing D1 in German, English, and French | Online text inspected, not downloaded or hash-verified |

E1 and E2 are editions of different versions, so comparing them does not test competing editions of the same version. E3 supplies a candidate for that comparison, but no differences in notation or measure numbering are claimed.

The same intellectual edition may have printed and digital manifestations. Keep publisher, edition statement, and editorial contributors on the edition; binding, file format, source URL, and individual-copy condition on the manifestation or holding. A library catalogue's copy is not a Mira Library holding.

Fingering and preface authorship need explicit contributor roles. An Urtext label is a publisher's edition designation, not a claim that the text is free of editorial judgment.

## Multilingual source test

D1 appears in three languages in one publisher file. Assign language-specific component locators: German and English on printed page IV; French on V. Translation direction and translators are not established by the inspected extract, so retain them as unknown. [H3]

The French premiere statement is qualified; the English wording is categorical. Preserve this difference as a source-language qualification, not a disagreement between independent critics. The preface is signed 1995 but cites a 2003 catalogue: its signature date must not become the current file's publication date. [H3]

This tests multilingual document handling, not the reception collection. No original-language review, attributed review translation, or conflicting critical pair was established. Those acceptance cases remain open rather than being filled with invented examples.

## Recording and release records

| Example ID | Entity | Representation |
|---|---|---|
| R1 | Recording candidate | François-Joël Thiollier performing V2; exact session, take, recording date, and mastering unspecified |
| A1 | Release | Naxos 8.553291, Piano Music Vol. 2; includes the cycle alongside other works. Label catalogue supports performer and album association. [N1] |
| U1 | Upload | YouTube video bMWthLep55I; titled as Thiollier's solo version; runtime 17:37 and six movement credits previously checked in this conversation. [Y1] |

Store U1's R1 association as metadata-supported, not audio-matched. The earlier YouTube inspection showed Thiollier and the album in its music credits; this design turn did not repeat playback or availability verification. Keep the provenance of that earlier check with the assertion.

The label's catalogue does not establish U1's precise master or timing. An upload runtime cannot automatically populate R1's musical duration, and an album catalogue number cannot serve as a recording ID. A compilation or reissue can reuse the same recorded performance.

Proposed extension: A1 becomes a release/container record with ordered tracks, each linked to its recording and work component. U1 becomes a presentation containing the six components in sequence. One upload can contain multiple recordings; one recording can have multiple presentations. Do not require a one-to-one parent relationship.

No second upload of the same performance was verified. The design describes the relationship, but duplicate-recording detection is not empirically tested here.

## Expected retrieval behavior

| Question | Expected answer from this example |
|---|---|
| Which version is solo piano? | V2, with E1 as a documented edition and R1 as a recording candidate |
| Are HN 402 and HN 408 duplicate editions? | No; they represent different performing versions |
| Does 131 versus 139 imply a different composition? | No; retain the catalogue-edition concordance |
| Do we own the score because its product page was read? | No; all complete-score holdings remain absent in this pilot |
| Have we collected three independent critical opinions? | No; F1 presents language components of one preface |
| Does a complete video imply the whole album is held? | No; upload, recording, release, and local holding remain separate |
| Is the performance suitable for sleep? | Unresolved; bibliographic evidence alone cannot establish its dynamics or listener response |

These are manually checked modelling expectations, not results from existing Library software.

## Acceptance case disposition

| Architecture case | Outcome |
|---|---|
| Multiple catalogue identifiers and a revised version | Partial: concordance and performing versions represented; chronological revision not tested |
| Two editions with differing editorial claims and numbering | Partial: separate editions modelled; competing texts and measure differences not inspected |
| Original review and attributed translation | Untested; multilingual editorial material is a useful adjacent case |
| Conflicting critical judgments | Untested; translation qualification is not independent critical disagreement |
| Multiple uploads of one recording | Untested empirically; recording-to-release-to-upload structure exposed as a necessary refinement |
| Collected volume and partial holdings | Partial: multi-work album represented; collected-score volume and partial file coverage not inspected |
| Lost or disputed work without false score holdings | Untested; no such record created |

The bounded Debussy test is complete. It supports the core entity distinctions, not full acceptance of the implementation design. Broad acquisition should not be inferred from this example.

## Recommended architecture refinements

1. Split performance event, recorded performance, and release. Allow unknown sessions and reuse across releases without forced duplication.
2. Split edition, manifestation, and holding. Support container membership and item-level coverage for albums, collected scores, prefaces, and movement extracts.
3. Add claim-level evidence: source, locator, language, reported wording or paraphrase, uncertainty, verification method, and check date. Keep editorial judgment distinct from independently established fact.
4. Preserve document-component language and revision metadata. Do not assume that a signed essay date is the date of a revised web file, or that all translations preserve the same confidence.

These are recommendations for a later architecture revision, not changes silently applied to the controlling contract. No additional research is required to understand or decide these four refinements.

## Source register

- **H1 — inspected publisher page:** [Henle HN 402](https://www.henle.de/de/Six-Epigraphes-antiques/HN-402). Supports the solo edition's identity and contributor roles; not a complete-score inspection.
- **H2 — inspected publisher page:** [Henle HN 408](https://www.henle.de/Six-Epigraphes-antiques-for-Piano-Four-hands/HN-408). Supports four-hands edition identity and contributor roles.
- **H3 — inspected publisher PDF text:** [Lesure preface for HN 402](https://www.henle.de/media/a7/98/9b/1697725792/0402-1697725792-sync.pdf), printed pages IV–V. Supports the catalogue concordance and multilingual example. Browser text extraction was read; no visual score inspection is claimed.
- **I1 — inspected catalogue index:** [IMSLP list of Debussy works](https://imslp.org/wiki/List_of_works_by_Claude_Debussy), numbering legend. Corroborates how this index labels numbering systems; not an original Lesure catalogue.
- **N1 — inspected label catalogue PDF text:** [Naxos Debussy catalogue](https://www.naxos.com/sharedfiles/PDF/SegmentCatalogue_Debussy.pdf), PDF page 2, row 8.553291. Establishes album and pianist association, not audio identity.
- **B1 — discovery only:** [BnF Durand solo edition record](https://catalogue.bnf.fr/ark:/12148/cb377282055). Search-index metadata retrieved; direct record fetch failed. Candidate only.
- **Y1 — earlier conversation inspection:** [Thiollier complete-cycle upload](https://www.youtube.com/watch?v=bMWthLep55I). Earlier browser read established displayed duration and credits. No new playback check or audition in this test.
