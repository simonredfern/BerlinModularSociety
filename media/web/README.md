# Scraped web-resolution sources

The 50 images recovered from the Super/Notion site in September 2026, at 1920px — the
largest size Cloudflare Images would serve. **These are committed; the variants built
from them are not.**

`npm run images` reads each file here and writes AVIF, WebP and a JPEG/PNG fallback at
640 / 1280 / 1920px into `static/images/`, which is gitignored.

Filenames carry the rights holder as a prefix — see [COPYRIGHT.md](../../COPYRIGHT.md).
The filename minus its extension is the id used by `<Photo id="..." />` and by
`src/lib/data/photos.json`.

Got something better? Put it in [`../originals/`](../originals/) under the same id; it
wins automatically.
