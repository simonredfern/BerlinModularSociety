# Migration scripts

One-shot tooling that lifted the content out of Super.so in September 2026. Kept for
provenance and in case anything needs re-extracting. **Not part of the build.**

They expect the 17 fetched Super HTML pages in this directory, as `page.html` (the
homepage) and `p_<slug>.html`, with `__` standing in for a `/` in a nested slug:

```sh
curl -sSL https://berlinmodularsociety.com/ -o page.html
curl -sSL https://berlinmodularsociety.com/about -o p_about.html
curl -sSL https://berlinmodularsociety.com/artist-area/using-obs -o p_artist-area__using-obs.html
# ...see the PAGES list at the top of extract.py for all 17
```

Then, in order — each one reads what the last wrote:

| Script | Does |
|---|---|
| `extract.py` | Walks the `notion-root` article in each page, emits markdown + `out/images.json` |
| `download.py` | Pulls every image at 1920px from `images.spr.so` into `media/web/`, slugifying filenames and prefixing them `bms_` |
| `finalize.py` | Rewrites photo ids, injects component imports, writes `src/content/` and the data files |
| `events.py` | Turns the event archive into `src/lib/data/events.json` + `src/content/events/` |

`extract.py` maps Notion block types to markdown and components: `notion-text` to
paragraphs, `notion-image` to `<Photo>`, `notion-embed` to `<Embed>`, `notion-column-list`
to `<Columns>`/`<Column>`, headings to `##`/`###`.

`events.py` must run after `download.py` (it needs `out/idmap.json` to rewrite photo
ids) and after `finalize.py` (it edits the `photos.json` that finalize writes).

## What became data

Three places on the Super site restated the same event facts in their own words, and
they disagreed: the homepage's "Next Event" heading, the `/upcoming-dates` table —
which still listed BMS57 and BMS58 as upcoming months after both had happened — and
`/event-archive`. `events.py` parses the number, date, venue, ticket link and running
order out of all of it into `src/lib/data/events.json`. Everything else stays as prose
in `src/content/events/<slug>.md`.

## Careful

- The date parsing is heuristic. Most archive entries gave a day and month but no
  year ("Thursday 7th March"), so `events.py` walks the list newest-first and takes
  the latest year that still lands each event before the one above it. Events it had
  to infer a year for carry `"inferredYear": true` in `events.json`. It prints a
  warning for any event that lands out of order.
- Re-running `finalize.py` regenerates `src/content/` and `photos.json` from the
  original Super HTML. Any hand-editing of those files since the migration would be
  lost. `events.py` likewise rewrites `src/content/events/`.
