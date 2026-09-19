import json, os, re, urllib.request, hashlib, sys

SCRATCH = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(SCRATCH, '..', '..'))
WEB = os.path.join(PROJ, 'media', 'web')
os.makedirs(WEB, exist_ok=True)

images = json.load(open(os.path.join(SCRATCH, 'out', 'images.json'), encoding='utf8'))

# Filenames carry the rights holder as a prefix - see COPYRIGHT.md. Everything the
# migration recovered is BMS's own flyer art, event stills, logos or screenshots, so
# `bms_` is the default. Rename any file whose photographer turns out to be someone
# else, and update its id in photos.json and in the <Photo> tag.
PREFIX = 'bms_'

def slugify(s):
    s = re.sub(r'\.(jpe?g|png|webp|gif)$', '', s, flags=re.I)
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-') or 'image'
    return PREFIX + s

EXT = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif'}

photos, used = {}, {}
fails = []
for i, (name, rec) in enumerate(images.items(), 1):
    sid = slugify(name)
    if sid in used:
        used[sid] += 1
        sid = f'{sid}-{used[sid]}'
    else:
        used[sid] = 1
    url = rec['base'] + '/w=1920,quality=90,fit=scale-down'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (site-migration)'})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
            ct = r.headers.get('Content-Type', '').split(';')[0].strip()
    except Exception as e:
        fails.append((name, str(e)))
        print(f'  [{i}/{len(images)}] FAIL {name}: {e}', flush=True)
        continue
    ext = EXT.get(ct, 'jpg')
    fn = f'{sid}.{ext}'
    with open(os.path.join(WEB, fn), 'wb') as fh:
        fh.write(data)
    photos[sid] = {
        'id': sid,
        'file': fn,
        'alt': rec['alt'],
        'caption': rec['caption'],
        'credit': rec['credit'],
        'creditUrl': rec['creditUrl'],
        'source': rec['base'],
        'pages': rec['pages'],
    }
    print(f'  [{i}/{len(images)}] {fn}  {len(data)//1024}KB', flush=True)

json.dump(photos, open(os.path.join(SCRATCH, 'out', 'photos.json'), 'w', encoding='utf8'),
          indent=2, ensure_ascii=False)
# name -> slug map, so the markdown can be rewritten
json.dump({n: s for n, s in zip(images.keys(), photos.keys())} if len(images) == len(photos) else
          {n: slugify(n) for n in images},
          open(os.path.join(SCRATCH, 'out', 'idmap.json'), 'w', encoding='utf8'), indent=2, ensure_ascii=False)
total = sum(os.path.getsize(os.path.join(WEB, p['file'])) for p in photos.values())
print(f'\ndownloaded {len(photos)}/{len(images)}  total {total/1024/1024:.1f} MB  failures: {len(fails)}')
for n, e in fails: print('  FAIL', n, e)
