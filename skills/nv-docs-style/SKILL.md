---
name: nv-docs-style
description: Layout, page format and Docsify setup for a repo's docs/ folder, with lessons/, adr/ and research/ sections. Read by research-about, teach and to-adr. Run it to check, create or restructure docs/ outside a flow.
disable-model-invocation: true
argument-hint: "Leave empty to check docs/ and offer to fix it"
---

# Docs style

Every doc a skill writes is Markdown inside `docs/`, viewed with [Docsify](https://docsify.js.org/). `assets/skeleton/` in this skill's folder is a fresh `docs/` folder. Paths below resolve from the repo root (the directory the calling skill was run in, when there is no repo).

## Layout

```
docs/
  index.html        Docsify setup, copied from the skeleton
  .nojekyll         keeps GitHub Pages from hiding files that start with _
  README.md         home page: what the docs hold, one row per section
  _navbar.md        top bar: Home · Lessons · ADR · Research
  _sidebar.md       home sidebar: links to the three sections
  assets/theme.css  dark theme, copied from the skeleton
  lessons/
    README.md       table of topics, newest first
    _sidebar.md     Home, Lessons, then one link per topic
    <topic-slug>/
      README.md     overview: goal, scope, date, ordered list of lessons
      _sidebar.md   the topic's pages in reading order
      0001-<name>.md
      glossary.md
      sources.md
  research/         same shape as lessons/
  adr/
    README.md       table of ADRs: number, title, status, date
    _sidebar.md     Home, ADR, then one link per ADR in number order
    0001-<name>.md
```

Only these sit at the top of `docs/`. Topic slugs and file names are lowercase dash-case. Page numbers are four digits, start at `0001`, and keep their number when pages are added later.

## Sidebars and navigation

Docsify loads the `_sidebar.md` in the folder of the current page and falls back to the parent folder. So the home page shows the home sidebar, a section page shows the section sidebar, and a topic page shows the topic sidebar.

- Write every link from the docs root with a leading slash: `/research/kafka/0002-partitions.md`. A folder link ends in `/` and opens its `README.md`.
- The pagination plugin builds Previous and Next from the sidebar, so list pages in reading order. Pages need no footer links.
- Section sidebar, one line per topic, newest first:
  ```markdown
  - [← Home](/)
  - [Research](/research/)
    - [Kafka](/research/kafka/)
  ```
- Topic sidebar:
  ```markdown
  - [← All research](/research/)
  - [Overview](/research/kafka/)
  - [1. What Kafka is](/research/kafka/0001-what-kafka-is.md)
  - [2. Partitions](/research/kafka/0002-partitions.md)
  - [Glossary](/research/kafka/glossary.md)
  - [Sources](/research/kafka/sources.md)
  ```
- ADR sidebar lists `- [7. Use zod for input validation](/adr/0007-use-zod-for-input-validation.md)` lines in number order.
- When a page is added, update its topic sidebar, the section sidebar and the section `README.md` table in the same run.

## Page format

- One `#` title per page. Sections under `##`.
- First line under the title is an italic kicker: `*Research · Kafka · 2 of 5*` or `*Lesson · Kafka · 2 of 5*`.
- Code and commands in fenced blocks with a language. Diagrams in ```` ```mermaid ```` blocks. Comparisons in tables.
- Key points as a blockquote starting `> **Key point:**`. Pitfalls as `> **Watch out:**`.
- Cite a claim right after the sentence with its source number linked to the source's URL: `[[3]](https://kafka.apache.org/documentation/)`, where 3 is its number in the topic's `sources.md`.
- Plain Markdown only. No raw HTML, no per-page CSS or scripts.
- Prose follows `../nv-writing-style/SKILL.md` if it is installed.

`glossary.md` lists `**Term**: one or two sentence definition. See [page](/path.md).` entries, one per paragraph, sorted alphabetically. Use each term the same way in every page of the topic.

`sources.md` is a numbered list. Each item is the title as a link, then an indented line: author or publisher, date or version, type (docs, guide, blog, spec, video), and one line on what it covers. Add a `## Gaps` section for areas with no good source.

## Check docs/

Every skill that writes docs runs this first.

1. **No `docs/` folder:** copy `assets/skeleton/` to `docs/`. Replace `{{SITE_NAME}}` with a title from the repo name and `{{SITE_DESCRIPTION}}` with one line on what the repo is. Continue.
2. **`docs/` matches the layout:** `index.html` loads Docsify, `_navbar.md` and `_sidebar.md` exist, and nothing sits at the top level except the files above and the three section folders. Create a missing section folder from the skeleton and continue.
3. **`docs/` exists but doesn't match:** build a restructure plan (below) and ask the user once, showing the plan: "docs/ doesn't follow nv-docs-style. Restructure it like this?"
   - **Yes:** restructure, then continue.
   - **No:** keep the current layout. Write into the folder the repo already uses for this kind of doc (an existing `docs/adr/`, `docs/research/`, lessons folder), in the format the docs there already use. If there is none, write to this layout's path for that section only. Update whatever sidebar or index the current layout has. Change nothing else.

## Restructure

1. **Inventory** every file under `docs/`. Classify each folder or file as an ADR (numbered decision record), a lesson or course, research or reference notes, or a docs-site file (`index.html`, `_sidebar.md`, theme, assets).
2. **Plan the moves.**
   - ADRs go to `adr/NNNN-<name>.md`, keeping their numbers.
   - Lessons go to `lessons/<topic-slug>/`, research and reference notes to `research/<topic-slug>/`. Content that fits none of the three goes to `research/<topic-slug>/` too, named after its folder.
   - Loose pages that belong together become one topic. Number them in their current reading order (the old sidebar or index order).
   - HTML pages written by earlier versions of `research-about` or `teach` are converted to Markdown in this format. Their `style.css` and quiz scripts are dropped.
3. **Show the plan** as a short list of `old path → new path` lines in the question above. Mention files you would delete.
4. **Apply it.** Use `git mv` when the repo is under git, so history follows the files. Copy in skeleton files that are missing. Keep an existing `index.html` only if the user customised it beyond the skeleton; otherwise replace it, keeping the site name.
5. **Fix links.** Rewrite every internal link to the new root paths. Write every `README.md` and `_sidebar.md` the layout needs.
6. **Check.** Every link in every `.md` file points to a file that exists. Leave the changes uncommitted and list them for the user.

## Viewing

Tell the user to run `npx docsify-cli serve docs` and open `http://localhost:3000`. To view from another device on the same network, add `--host 0.0.0.0` and open `http://<machine-ip>:3000`.
