# Copyright

This repository holds two different kinds of thing under two different licences.

> **Names to confirm.** The two holders below are this file's best reading — Simon
> Redfern wrote the application, the content is the group's. Nobody has checked them
> against how BMS is actually constituted, and BMS is a collective rather than a
> registered entity. Correct them if they are wrong; everything else here depends on
> them being right.

## Code — AGPLv3

Copyright © 2021–2026 Simon Redfern.

The SvelteKit application. Specifically:

| | |
|---|---|
| `src/lib/components/` | all components |
| `src/lib/*.js` | `events.js`, `calendar.js` |
| `src/routes/` | all routes |
| `src/app.css`, `src/app.html` | |
| `scripts/` | build, migration and the drift check |
| root config | `svelte.config.js`, `vite.config.js`, `package.json`, workflows |

See [LICENSE](LICENSE).

**Where this code came from.** It is a derivative of the [3pi.tv](https://3pi.tv) site,
also AGPLv3 and by the same author — BMS was migrated off Super the same way and reuses
its components, build scripts and migration tooling. The AGPL carries across; if anyone
other than Simon contributed to that repo, their copyright carries across too.

## Content — all rights reserved

Copyright © 2021–2026 Berlin Modular Society.

Not covered by the AGPL, and not licensed for reuse:

| | |
|---|---|
| `src/content/` | every page, including `events/` |
| `src/lib/data/events.json` | the events, line-ups and venues |
| `src/lib/data/photos.json` | captions, alt text and credits |
| `src/lib/data/nav.json`, `links.json` | |
| `media/` | every image, including the seven Facebook flyers |
| `static/favicon.png` | the BMS logo |
| | the Berlin Modular Society name and logo themselves |

Ask first: info@berlinmodularsociety.com

`src/lib/data/pages.json` and `photo-sizes.json` are generated, and follow whichever
licence covers what they were generated from.

**The split is not a clean directory boundary**, which is the thing to watch: `src/lib/`
holds components (code) next to `src/lib/data/` (mostly content). Anyone reusing this
codebase needs to take the components and scripts and leave the data behind.

## Photographs and artwork

Filenames carry the rights holder as a prefix, so you can tell at a glance whose an
image is without opening a data file:

```
<rights-holder>_<description>.<ext>

bms_bms43-still-b6.jpg          BMS's own
bms_logo-in-black-on-white-background.jpg
unknown_something.jpg           provenance genuinely unknown
jane-doe_bms60-crowd.jpg        someone else's, credited to them
```

The id is the filename without its extension, and it is what `<Photo id="..." />` and
the key in `src/lib/data/photos.json` both use. Renaming a file means changing all three.

### Two batches, two provenances

The 62 images come from two places, and `source` in `photos.json` says which:

| | | |
|---|---|---|
| **55** | scraped from the Super site | `source` is an `images.spr.so` URL |
| **7** | the BMS3–BMS9 event flyers, taken off the Facebook events in September 2026 | `source` is `"Facebook event"` |

All 62 are prefixed `bms_`. Reviewed and accepted as BMS's own in September 2026: they
are event flyers, running-order cards, video stills from BMS's own streams, the logo and
its variants, the page banner, and OBS screenshots — work made by or for BMS.

### No photographer credits survived

Nothing on the Super site recorded one: every image's caption was Notion's placeholder,
the literal word "image". So every `credit` field in `photos.json` is `null`.

That is a gap in the record rather than a dispute. A few images have someone else's hand
in them somewhere, and if you ever learn whose, they are worth crediting:

| | |
|---|---|
| the `IMG_####` photos on `/community` | candid shots of people at events, the sort a guest takes |
| `bms_whatsapp-image-2025-04-15-at-08-47-04` | on BMS50, forwarded from someone |
| `bms_bms9-flyer` | built around a photograph of a performer at a modular rig |
| `bms_bms3-country-fair` | the event was co-presented with NÖ, so the poster may be too |

To credit one: rename the file with that person's prefix, and fill in `credit` and
`creditUrl` in `photos.json`. The credit then renders under the photo.

### If you are in a photo and want it down

Email info@berlinmodularsociety.com and it will be removed.
