# High-resolution originals

Empty on purpose. **Nothing here is required to build the site.**

`media/web/` holds the 1920px versions scraped from the old Super/Notion site. Those are
derived files — Cloudflare Images never served the true originals, so 1920px wide,
re-compressed, is the best quality that migration could recover.

## When you get the originals

Drop them in here and re-run the build. That's the whole upgrade:

```sh
npm run images
```

`scripts/build-images.mjs` prefers `media/originals/<id>.<ext>` over
`media/web/<id>.<ext>`, so every page picks up the better source with **no markup
changes**. `src/lib/data/photo-sizes.json` records which source each image came from,
so you can see at a glance what has been upgraded:

```sh
grep -c '"source": "originals"' src/lib/data/photo-sizes.json
```

## Filenames must match

The id is the filename without its extension, and it must match the id already used in
`src/lib/data/photos.json` and in the `<Photo id="..." />` tags. The extension may differ —
a TIFF or a higher-quality JPEG both work.

```
media/web/bms_bms43-still-b6.jpg        <- scraped, 1920px
media/originals/bms_bms43-still-b6.tif  <- yours, wins when present
```

To list the ids that would benefit most, sort by the recovered width:

```sh
node -e "const s=require('./src/lib/data/photo-sizes.json');
Object.values(s).filter(p=>p.source==='web').sort((a,b)=>a.width-b.width)
.slice(0,20).forEach(p=>console.log(p.width+'x'+p.height, p.id))"
```

## The flyers and stills are worth chasing

Most of `media/web/` is event artwork and video stills from the BMS streams. Whoever
made a flyer will have the layered original, and the stills came out of recordings that
still exist — both are far better sources than a 1920px re-encode.
