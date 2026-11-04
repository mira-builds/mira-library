# Contributing to Mira Library

Work through a shelf issue and pull request. The public collaboration home is
`mira-builds/mira-library`; Core remains the collection admission and curation
authority. Proposals do not change catalog truth or an author's score.

1. Claim an assigned shelf issue and its explicit work/language target. Start
   from the public baseline commit named in that issue. Check with the maintainer
   before acquisition: Core may already hold material absent from this public
   snapshot.
2. Inspect primary source routes and exact editions. Preserve work extent,
   language, translator/editor, table/verse structure and known source limits.
3. Add one evidence proposal at
   `contributions/<shelf-id>/<candidate-id>.json`. Use the schema in
   [proposal format](collaboration/proposal-format.md). Keep source texts, PDFs,
   private paths, operational records and credentials out of Git.
4. Run `python -B checks.py` and
   `python -B -m unittest discover -s tests -v`. CI also checks tracked inventory.
5. Open a PR referencing the issue, explaining the gap, evidence, inspection
   limits and remaining uncertainty. All proposals require maintainer review;
   no automatic merge or admission is configured.

Do not edit generated catalog, master/shelf indexes, reader code, workflows or
`release.json` as a source-proposal PR. Those are maintainer changes. In
particular, do not alter release hashes merely to make a proposal pass: proposals
are deliberately outside the released collection inventory.

An inspected candidate must report actual payload size/hash; a located-only
source has `payload: null`. Neither state means admitted, read in full, approved
for redistribution or complete for the author's corpus. A newer upstream text
is not automatically correct. Record version/wording differences for review.

The maintainer reviews the evidence, checks current Core holdings and integrates
any separately authorized admissions/corrections. The resulting public catalog
is regenerated through the reviewed export workflow. Proposal validation proves
format and scope, not source reliability or successful admission.

The initial assignee is the repository-owner account `mira-builds`. No separate
collaborator invitation is needed for that account. Human/operator review is
still required; no claim of independent GitHub approval is implied.
