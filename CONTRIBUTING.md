# Contributing

We welcome papers, official projects, classification corrections and missing earlier work. The collection focuses on executable representations of worlds, with explicit scope notes for software execution models and related enabling work.

## Add or correct a record

1. Read a primary source: the author abstract, publisher page, official report, project or repository. Verify the exact title, authors and first submission date. Leave unconfirmed dates null; repository creation is not a paper publication date.
2. Use the 22 flat topics in `data/taxonomy.json`. Set `classification.readme_topic` to one topic ID representing the main contribution, and include it in the nonempty, unique `classification.topics` list. The former controls one README placement; the latter enables overlapping website filters. These are the same vocabulary, with no additional hierarchy.
3. Record `classification.checked` as an ISO date (`YYYY-MM-DD`), an English `summary_reason`, and an English `topic_reasons` entry for every selected topic. Its keys must exactly match `topics`. Include nonempty `sources` with `url`, `basis` and `note`, plus an `uncertainties` array. Source basis is `primary_abstract`, `official_project` or `full_text`. Describe the sections actually read; do not claim a complete full-text review or reproduction from an abstract.
4. Preserve the source abstract separately from the editorial summary in `data/papers.json`. Each resource needs its own type and provenance URL. Keep `verification` and `resource_status.evidence` honest and current.
5. Keep `classic: false` and `classic_note: ""` unless a representative-work designation has an editorial rationale. A topic denotes research scope, not demonstrated quality.
6. Preserve legacy `track`, `category`, `cross_categories` and `dimensions` for crawler compatibility. They do not define public categories. Maintain `collections` and `benchmarks` where applicable. A named protocol records `name`, `input`, `artifact`, `checks`, `caveat` and a primary `source`; it is not another paper record.
7. Run `python3 scripts/build.py`, `python3 -m unittest discover -s tests -v` and `node tests/search.test.cjs`. Include generated files in the PR and verify `python3 scripts/build.py --check`.

## Topic boundaries

- General World Model describes an integrated framework, not a quality ranking. A component or a method using a world model does not automatically qualify.
- Multi-Agent refers to entities acting inside the world, not collaborating coding agents.
- Streaming, Real-Time and Acceleration are distinct. Preserve reported timing and hardware conditions. Generic long-horizon simulation is not necessarily Long Video Generation.
- Code Execution concerns computational semantics, state prediction or correctness; merely executing generated world code is insufficient.
- A training-free adaptation is not automatically Post-Training. Supporting someone else's distilled checkpoint is not evidence that this project trained it.
- A method may receive a website Benchmark topic when it introduces and substantively defines a named task suite and scoring protocol. Substantive newly introduced data resources may support Dataset; record the actual public scope separately. Keep its README placement under the main contribution. Reusing existing tests or publishing demonstration files is insufficient.
- Resource availability and Dataset are separate. A code, project or weights link can support a resource badge without constituting a dataset release. Record promised or incomplete releases explicitly; publishing a paper about a dataset does not imply that its full data are downloadable.

Select topics based on supported contributions; there is no fixed per-paper tag limit. The website combines selected topics by intersection, together with month, title/author search and resource filters.

## Generated files and README

Do not hand-edit the generated README, `site/catalog.js`, exports, `docs/BENCHMARKS.md`, `docs/TOPIC_REVIEW.md` or their generated web pages. Edit `docs/README.template.md` for introductory copy; edit source data for records and evidence. Frontend sources are `site/index.html`, `site/style.css`, `site/search.js` and `site/app.js`.

Each paper appears exactly once in the README bibliography. Do not duplicate entries under recent updates or reading paths. Website topics may overlap, while a result list still shows each paper once. The per-paper topic review preserves the evidence and actual reading scope.

Add collection announcements to `data/updates.json`. The Chinese classification guide is [docs/TAXONOMY.md](docs/TAXONOMY.md); the root `Code_World_Models_Taxonomy.md` is a matching convenience copy.

## Promote a crawler candidate

Candidates in `data/inbox.json` stay outside the public index. Read the source and complete the record and topic evidence before promotion; the crawler's low-confidence legacy category suggestion is not sufficient. After adding the curated record, set its status to `accepted`. Set `rejected` with a reason for irrelevant or duplicate results. Preserve decisions so later discovery runs do not reopen the same candidate.

Use English for commit messages and public classification reasons. The main collection is written in English; detailed taxonomy and maintenance notes may be in Chinese.
