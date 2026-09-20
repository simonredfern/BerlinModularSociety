import json, os, re
from html import escape as html_escape

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCRATCH, 'out')
PROJ = os.path.abspath(os.path.join(SCRATCH, '..', '..'))
CONTENT = os.path.join(PROJ, 'src', 'content')
os.makedirs(CONTENT, exist_ok=True)

photos = json.load(open(os.path.join(OUT, 'photos.json'), encoding='utf8'))
idmap = json.load(open(os.path.join(OUT, 'idmap.json'), encoding='utf8'))

NAV = [
    # Home is in the menu rather than as a breadcrumb on every page.
    ('', 'Home', 'Home'),
    ('upcoming-dates', 'Upcoming Dates', 'Upcoming'),
    ('event-archive', 'Event Archive', 'Archive'),
    ('artist-list', 'Artist List', 'Artist List'),
    ('about', 'About', 'About'),
    ('community', 'Community', 'Community'),
    ('modular-courses', 'Modular Courses', 'Courses'),
    ('artist-area', 'Artist Area', 'Artist Area'),
]

COMPONENTS = {
    'Photo': '$lib/components/Photo.svelte',
    'Embed': '$lib/components/Embed.svelte',
    'Columns': '$lib/components/Columns.svelte',
    'Column': '$lib/components/Column.svelte',
    'Color': '$lib/components/Color.svelte',
    'NextEvent': '$lib/components/NextEvent.svelte',
    'EventList': '$lib/components/EventList.svelte',
    'EventArchive': '$lib/components/EventArchive.svelte',
}

def fix_text(t):
    # Collapse adjacent strong runs: **a****b** -> **ab**
    prev = None
    while prev != t:
        prev = t
        t = t.replace('****', '')
    return t

md_files = []
for root, _dirs, files in os.walk(OUT):
    for f in files:
        if f.endswith('.md'):
            md_files.append(os.path.relpath(os.path.join(root, f), OUT))

all_pages = []
for fn in sorted(md_files):
    slug = fn[:-3].replace(os.sep, '/')
    raw = open(os.path.join(OUT, fn), encoding='utf8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, flags=re.S)
    fm, body = m.group(1), m.group(2)

    # The header cover and icon are photo ids too, and they live in frontmatter
    # rather than in a <Photo> tag, so they need the same rewrite.
    def fm_photo(mm):
        key, old = mm.group(1), mm.group(2)
        new = idmap.get(old)
        if new is None or new not in photos:
            raise SystemExit(f'unmapped {key} photo id {old!r} in {fn}')
        return f'{key}: {json.dumps(new)}'
    fm = re.sub(r'^(cover|icon): "([^"]+)"$', fm_photo, fm, flags=re.M)

    # Rewrite photo ids to their downloaded slugs
    def repl(mm):
        old = mm.group(1)
        new = idmap.get(old)
        if new is None or new not in photos:
            raise SystemExit(f'unmapped photo id {old!r} in {fn}')
        return f'<Photo id="{new}" />'
    body = re.sub(r'<Photo id="([^"]+)" />', repl, body)
    body = fix_text(body)

    lines = body.split('\n')

    if slug == 'index':
        # "Next Event:" and the running order under it were typed into the homepage by
        # hand, and separately into /upcoming-dates and /event-archive. They are one
        # fact, so they come from events.json now via <NextEvent />.
        out, skipping = [], False
        for ln in lines:
            if re.match(r'^#+ *Next Event', ln):
                out.extend(['<NextEvent />', ''])
                skipping = True
                continue
            if skipping:
                # Swallow the hand-typed running order up to the next real heading.
                if ln.startswith('## ') and not re.match(r'^## *$', ln):
                    skipping = False
                else:
                    continue
            out.append(ln)
        # The trailing "## Links" block was a grid of cards duplicating the nav.
        if '### Links' in out:
            out = out[:out.index('### Links')]
        lines = out

    if slug == 'event-archive':
        # 50-odd events of prose, each restating its own date and venue. The facts are
        # in events.json and the prose in src/content/events/; <EventArchive /> joins
        # them back up. See scripts/migration/events.py.
        lines = ['<EventArchive />']

    if slug == 'upcoming-dates':
        # The Notion table here listed BMS57 and BMS58 as upcoming long after both had
        # happened. Same data as the archive, so read it from the same place.
        out, in_table = [], False
        for ln in lines:
            if ln.strip() == '## Upcoming BMS Dates':
                out.extend([ln, '', '<EventList show="upcoming" />', ''])
                in_table = True
                continue
            if in_table:
                if ln.startswith('Our public Google calendar'):
                    in_table = False
                else:
                    continue
            out.append(ln)
        lines = out

    body = '\n'.join(lines).strip()
    body = re.sub(r'\n{3,}', '\n\n', body)

    used = [c for c in COMPONENTS if re.search(rf'<{c}[ />]', body)]
    script = ''
    if used:
        imports = '\n'.join(f"\timport {c} from '{COMPONENTS[c]}';" for c in sorted(used))
        script = f'<script>\n{imports}\n</script>\n\n'

    if slug == 'event-archive':
        fm = re.sub(r'^description: ".*"$',
                    'description: "Every Berlin Modular Society event since BMS1 in '
                    'May 2021 - line-ups, venues, photos and streams."',
                    fm, count=1, flags=re.M)

    dest = os.path.join(CONTENT, fn)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'w', encoding='utf8').write(f'---\n{fm}\n---\n\n{script}{body}\n')

    meta = dict(re.findall(r'^(\w+): (.*)$', fm, flags=re.M))
    all_pages.append({
        'path': '' if slug == 'index' else slug,
        'title': json.loads(meta.get('title', '""')),
        'description': json.loads(meta.get('description', '""')),
    })
    print(f'{slug:48s} components: {",".join(sorted(used)) or "-"}')

def md_to_html(t):
    if not t:
        return ''
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               lambda m: f'<a href="{html_escape(m.group(2))}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
    return t.replace('&#123;', '{').replace('&#125;', '}').strip()

# Notion falls back to the literal word "image" when a block has no alt text. That is
# not a caption, and as alt text it is worse than nothing - screen readers already
# announce the role. Drop it rather than rendering a meaningless line under the photo.
PLACEHOLDER = {'image', 'images', 'photo', 'img', 'untitled', ''}

# Notion gave almost every image the alt text "image", so after stripping that the
# alt would be empty - which tells a screen reader the image is decorative. Most of
# these are event flyers, running orders and UI screenshots, and they are not. BMS
# named the files well, so the filename is a better description than nothing.
FILENAME_NOISE = {
    'img', 'image', 'photo', 'dsc', 'whatsapp', 'mv2', 'png', 'jpg', 'jpeg', 'webp',
    'at', 'crop', 'final', 'smaller', 'corrected', 'simple', 'b', 'e', 'still-e',
}
ACRONYMS = {'obs': 'OBS', 'diy': 'DIY', 'bms': 'BMS', 'av': 'AV', 'mkv': 'MKV'}

def alt_from_id(pid):
    """A readable description from an id like bms_obs-general-settings."""
    tokens = pid.split('_', 1)[-1].split('-')
    out = []
    for t in tokens:
        if not t or t.isdigit() or t in FILENAME_NOISE:
            continue
        m = re.fullmatch(r'([a-z]+)(\d+)', t)          # bms54 -> BMS54
        if m and m.group(1) in ACRONYMS:
            out.append(ACRONYMS[m.group(1)] + m.group(2))
            continue
        if len(t) == 1:
            continue
        out.append(ACRONYMS.get(t, t))
    # Drop a token that just repeats the one before it (bms_54-bms54-still).
    dedup = [t for i, t in enumerate(out) if i == 0 or t.lower() != out[i - 1].lower()]
    if not dedup:
        return ''
    text = ' '.join(dedup)
    return text[0].upper() + text[1:]

for rec in photos.values():
    if (rec.get('caption') or '').strip().lower() in PLACEHOLDER:
        rec['caption'] = ''
    rec['captionHtml'] = md_to_html(rec.get('caption'))
    rec['alt'] = re.sub(r'\s{2,}', ' ', re.sub(r'<[^>]+>', '', rec.get('alt') or '')).strip()
    if rec['alt'].strip().lower() in PLACEHOLDER:
        rec['alt'] = alt_from_id(rec['id'])

json.dump(photos, open(os.path.join(PROJ, 'src', 'lib', 'data', 'photos.json'), 'w', encoding='utf8'),
          indent=2, ensure_ascii=False)

json.dump(sorted(all_pages, key=lambda p: p['path']),
          open(os.path.join(PROJ, 'src', 'lib', 'data', 'pages.json'), 'w', encoding='utf8'),
          indent=2, ensure_ascii=False)
json.dump([{'slug': s, 'title': t, 'short': sh} for s, t, sh in NAV],
          open(os.path.join(PROJ, 'src', 'lib', 'data', 'nav.json'), 'w', encoding='utf8'),
          indent=2, ensure_ascii=False)
print(f'\npages.json: {len(all_pages)}   nav.json: {len(NAV)}')
