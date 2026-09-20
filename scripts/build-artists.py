#!/usr/bin/env python3
"""Rebuild src/lib/data/artists.json from the line-ups in events.json.

    npm run artists

Every act in a line-up is split into the individual artists behind it, so
"JacqNoise b2b Dan Graveyard" counts for both, and the twenty spellings of
drusnoise land on one record. Each act gains an `artists` list of slugs.

**This merges; it does not overwrite.** artists.json is part generated, part
curated - `aka` entries nobody was ever billed under (3PI), a website found by
hand, a preferred spelling - and all of that survives a rebuild. Only newly
observed spellings and handles are added.

The per-appearance `url` and `instagram` in events.json are deliberately left
alone. They record what was true on the night; artists.json records what is
true now.
"""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from importlib import import_module
A = import_module('artist-names')

PROJ = os.path.dirname(HERE)
EVENTS = os.path.join(PROJ, 'src', 'lib', 'data', 'events.json')
ARTISTS = os.path.join(PROJ, 'src', 'lib', 'data', 'artists.json')

events = json.load(open(EVENTS, encoding='utf8'))
existing = json.load(open(ARTISTS, encoding='utf8')) if os.path.exists(ARTISTS) else {}

seen = collections.defaultdict(lambda: {'names': [], 'instagram': [], 'url': []})
for e in events:
    for act in e['lineup']:
        names = A.split_act(act['act'])
        act['artists'] = [A.slug(n) for n in names]
        for n in names:
            r = seen[A.slug(n)]
            r['names'].append(n)
            # A handle on a solo billing belongs to that artist; on a shared one
            # there is no telling which of them it is.
            if len(names) == 1:
                for h in (act.get('instagram') or []):
                    if h.lower() not in [x.lower() for x in r['instagram']]:
                        r['instagram'].append(h)
                if act.get('url') and act['url'] not in r['url']:
                    r['url'].append(act['url'])

def canonical(names):
    counts = collections.Counter(names)
    mixed = [n for n in counts if n != n.upper()]
    pool = mixed or list(counts)
    return max(pool, key=lambda n: (counts[n], -len(n)))

out = {}
for slug, r in seen.items():
    prev = existing.get(slug, {})
    name = prev.get('name') or canonical(r['names'])          # a curated name wins
    # `aka` is for genuinely different names - Third Party Influence, 3PI - not for
    # the same name rendered differently. A spelling that differs only in case,
    # spacing or punctuation is noise: "E. SHAPERE" is not another name for
    # "E.Shapere".
    def same_name(x, y):
        strip = lambda v: ''.join(c for c in v.casefold() if c.isalnum())
        return strip(x) == strip(y)

    aka = {n for n in r['names']} | set(prev.get('aka', []))
    aka = {n for n in aka if not same_name(n, name)}

    handles, lower = list(prev.get('instagram', [])), set()
    lower = {h.lower() for h in handles}
    for h in r['instagram']:
        if h.lower() not in lower:
            handles.append(h); lower.add(h.lower())

    rec = {'slug': slug, 'name': name}
    if aka: rec['aka'] = sorted(aka)
    if handles: rec['instagram'] = handles
    url = prev.get('url') or (r['url'][0] if r['url'] else None)
    if url: rec['url'] = url
    out[slug] = rec

# A record nobody is billed under any more is dropped. These are almost always
# stale: a billing that has since been split, aliased or cleaned up, leaving the
# old auto-generated record behind. Reported rather than removed silently.
for slug, prev in existing.items():
    if slug not in out:
        print(f'  dropped {slug!r} ({prev.get("name")}) - no longer in any line-up')

out = dict(sorted(out.items()))
for path, data in ((ARTISTS, out), (EVENTS, events)):
    with open(path, 'w', encoding='utf8') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write('\n')

appearances = collections.Counter(s for e in events for a in e['lineup'] for s in a['artists'])
print(f'artists: {len(out)}   appearances: {sum(appearances.values())}')
print(f'  with a handle: {sum(1 for r in out.values() if r.get("instagram"))}'
      f'   with a website: {sum(1 for r in out.values() if r.get("url"))}'
      f'   with aka: {sum(1 for r in out.values() if r.get("aka"))}')
