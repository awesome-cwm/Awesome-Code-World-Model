# Contributing

We welcome papers, official projects, classification corrections and missing earlier work. The collection focuses on executable representations of worlds, with a separately labeled boundary for software execution models and alternative representations.

## Add a record

1. Provide a primary source: arXiv, publisher, official technical report or author-maintained project.
2. Check the exact title, authors and first submission date. Leave publication date null if unconfirmed. Do not infer a release date from repository creation.
3. Follow **World Models Taxonomy V2** in `data/taxonomy.json`. Set `classification.area` to exactly one of the six research areas. Set `classification.direction` to one direction under that area, or `null` when none accurately describes the contribution. Supply the eight dimension arrays in `classification.tags`, with at least one valid auxiliary tag in total. Record the evidence in `classification.basis`; do not infer capabilities from titles alone.
   Select the primary area by the main contribution, rather than every component the paper uses. A method with a benchmark need not have Benchmark as its primary direction. Legacy `track`, `category`, `cross_categories`, and `dimensions` remain source metadata for maintenance; they no longer create multiple primary classifications.
4. Add a unique record to `data/papers.json`. Preserve the source abstract separately from the editorial summary. Each resource needs its own type and provenance URL.
5. Set `verification.basis` honestly: primary abstract, official project, or full text. Record the date on which you reviewed the source.
6. Set `classic: false` and an empty `classic_note` by default. Selecting a representative work requires an editorial rationale. Keep `resource_status.evidence` synchronized with non-paper resource URLs; its badge follows the public-resource convention documented in the README.
7. Set `collections` and `benchmarks` (empty arrays when not applicable). A named benchmark protocol records `name`, `input`, `artifact`, `checks`, `caveat` and a primary `source`. Benchmark names within method papers are aliases, not additional paper records. Keep collection membership aligned with the protocol and identify differences between paper and public-release versions.
8. Run `python3 scripts/build.py` and `python3 -m unittest discover -s tests -v`; include generated files in the PR.

Do not edit `site/catalog.js`, exported files, `docs/BENCHMARKS.md` or the generated README directly. Edit `docs/README.template.md` for introductory copy. Edit `site/index.html`, `site/style.css` and `site/app.js` for the frontend.

Add collection announcements to `data/updates.json`. The README lists each paper under exactly one primary research area, with representative works first and other papers ordered by first submission date. Auxiliary tags supply cross-cutting indexes without duplicating primary membership.

## Promote a crawler candidate

Candidates live in `data/inbox.json`, outside the public curated index. Read the source and create a complete record before promotion; the crawler's suggested category is not sufficient evidence. After adding the curated record, set the candidate's status to `accepted`. Set `rejected` with a reason for irrelevant or duplicate results. Keep decision records so later daily runs do not reopen the same candidate.

## Review checklist

- Is code the world representation, a controller, a rendering condition, or the object being predicted?
- Is this generated motion, an engine-stepped physical simulation, or a learned transition?
- Do tags describe measured targets rather than imply success?
- Are streaming, throughput and interaction latency distinguished?
- Does the record have exactly one V2 research area, a matching direction if specified, and at least one auxiliary tag from the correct dimension?
- Are code links distinguished from project, data and weight links?

Use English for commit messages. Code comments and classification rationale may be written in Chinese. The main collection is written in English for an international audience; detailed Chinese taxonomy notes are in `docs/TAXONOMY.md`.
