# Contributing

We welcome papers, official projects, classification corrections and missing earlier work. The collection focuses on executable representations of worlds, with a separately labeled boundary for software execution models and alternative representations.

## Add a record

1. Provide a primary source: arXiv, publisher, official technical report or author-maintained project.
2. Check the exact title, authors and first submission date. Leave publication date null if unconfirmed. Do not infer a release date from repository creation.
3. Choose a primary research question in `data/taxonomy.json`, then add cross-categories where justified. Explain the role of code and who determines the next state.
4. Add a unique record to `data/papers.json`. Preserve the source abstract separately from the editorial summary. Each resource needs its own type and provenance URL.
5. Set `verification.basis` honestly: primary abstract, official project, or full text. Record the date on which you reviewed the source.
6. Set `classic: false` and an empty `classic_note` by default. Selecting a representative work requires an editorial rationale. Keep `resource_status.evidence` synchronized with non-paper resource URLs; its badge follows the public-resource convention documented in the README.
7. Set `collections` and `benchmarks` (empty arrays when not applicable). A named benchmark protocol records `name`, `input`, `artifact`, `checks`, `caveat` and a primary `source`. Benchmark names within method papers are aliases, not additional paper records. Keep collection membership aligned with the protocol and identify differences between paper and public-release versions.
8. Run `python3 scripts/build.py` and `python3 -m unittest discover -s tests -v`; include generated files in the PR.

Do not edit `site/catalog.js`, exported files, `docs/BENCHMARKS.md` or the generated README directly. Edit `docs/README.template.md` for introductory copy. Edit `site/index.html`, `site/style.css` and `site/app.js` for the frontend.

Add collection announcements to `data/updates.json`. Categories list representative works first and then other papers by first submission date, including cross-listed contributions.

## Promote a crawler candidate

Candidates live in `data/inbox.json`, outside the public curated index. Read the source and create a complete record before promotion; the crawler's suggested category is not sufficient evidence. After adding the curated record, set the candidate's status to `accepted`. Set `rejected` with a reason for irrelevant or duplicate results. Keep decision records so later daily runs do not reopen the same candidate.

## Review checklist

- Is code the world representation, a controller, a rendering condition, or the object being predicted?
- Is this generated motion, an engine-stepped physical simulation, or a learned transition?
- Do tags describe measured targets rather than imply success?
- Are streaming, throughput and interaction latency distinguished?
- Is the main contribution generation or understanding, with useful cross-links?
- Are code links distinguished from project, data and weight links?

原始分类理由可以使用中文。代码注释和维护提交默认使用中文。英文主目录面向国际读者；中文深度分类说明在 `docs/TAXONOMY.md`。
