"""Turn the extracted event-archive markdown into src/lib/data/events.json.

The archive was 50-odd events of hand-written prose. The *facts* in it - number,
date, venue, ticket link - are what the homepage, /upcoming-dates and /event-archive
each restated in their own words, and therefore what drifted. Those are parsed out
here into fields. Everything else is kept verbatim as the event's `body` markdown,
photos and embeds included, so nothing that was written is lost.

Heuristic by nature. Run it once, read events.json, fix what it got wrong by hand.
It is not part of the build.
"""
import json, os, re

SCRATCH = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(SCRATCH, '..', '..'))
SRC = os.path.join(SCRATCH, 'out', 'event-archive.md')

# download.py renamed every image to a `bms_`-prefixed slug; the markdown here still
# carries the raw Notion names. Same rewrite finalize.py does, for the same reason.
idmap = json.load(open(os.path.join(SCRATCH, 'out', 'idmap.json'), encoding='utf8'))

raw = open(SRC, encoding='utf8').read()
body = re.sub(r'^---\n.*?\n---\n', '', raw, flags=re.S)

# An event starts at a heading, or a lone bold line, that names a BMS number.
NUM = re.compile(r'\bBMS\s*(AV)?\s*#?\s*(\d+)\b', re.I)
START = re.compile(r'^(#{1,3} .*|\*\*[^*].*\*\*)$')

lines = body.split('\n')
starts = []
for i, ln in enumerate(lines):
    if START.match(ln.strip()) and NUM.search(ln):
        starts.append(i)

# Merge a heading pair like "## Archived Event: BMS46, Sat 9th November" followed by
# "## Where: Crack Bellmer" - the second is a continuation, not a new event.
starts = [i for j, i in enumerate(starts)
          if j == 0 or NUM.search(lines[i]).group(2) != NUM.search(lines[starts[j-1]]).group(2)]

MONTHS = {m.lower(): n for n, m in enumerate(
    ['January','February','March','April','May','June','July','August',
     'September','October','November','December'], 1)}
MONTHS.update({m[:3].lower(): n for m, n in list(MONTHS.items())})
MONTHS['sept'] = 9
MONTHS['thurs'] = None  # guard: never a month
del MONTHS['thurs']
MON_RX = '|'.join(sorted(MONTHS, key=len, reverse=True))

DATE_RX = re.compile(
    rf'\b(\d{{1,2}})\s*(?:st|nd|rd|th)?\s+(?:of\s+)?({MON_RX})\b\.?\s*,?\s*(\d{{4}})?', re.I)
DATE_RX2 = re.compile(
    rf'\b({MON_RX})\s+(\d{{1,2}})\s*(?:st|nd|rd|th)?\b\.?\s*,?\s*(\d{{4}})?', re.I)

def strip_md(s):
    s = re.sub(r'<[^>]+>', '', s)          # colour spans added by extract.py
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
    # Not '_': it is rare as emphasis here and common inside @handles.
    return re.sub(r'[*#]', '', s).strip()

def find_date(text):
    """Day + month, and the year if it is stated. Returns (month, day, year|None)."""
    t = strip_md(text)
    m = DATE_RX.search(t)
    if m:
        return MONTHS[m.group(2).lower()], int(m.group(1)), int(m.group(3)) if m.group(3) else None
    m = DATE_RX2.search(t)
    if m:
        return MONTHS[m.group(1).lower()], int(m.group(2)), int(m.group(3)) if m.group(3) else None
    return None

# Every event was in Berlin bar the Utrecht one.
CITY = {'de helling': 'Utrecht'}

# Headings inside an event body that only restate a field, now that the field exists.
SCAFFOLD = re.compile(
    r'^#{1,6}\s*(where|when|lineup|line-up|address|tickets?|artists?( \(all live\))?)\s*:?\s*$',
    re.I)

def clean_body(md, venue):
    """Drop headings that only repeat the date/venue, and demote the rest.

    Each event renders under its own <h2> in EventList, so a body <h2> would sit at
    the same level as the event it belongs to.
    """
    out = []
    for ln in md.split('\n'):
        t = ln.strip()
        if SCAFFOLD.match(t):
            continue
        h = re.match(r'^(#{1,6})\s*(.*)$', t)
        if h:
            inner = strip_md(h.group(2))
            # A heading that is only the date, or only the venue, is now a field.
            bare = DAYS.sub(' ', inner)
            bare = DATE_RX.sub(' ', bare)
            bare = DATE_RX2.sub(' ', bare)
            if venue:
                bare = re.sub(re.escape(venue), ' ', bare, flags=re.I)
            bare = re.sub(r'\b(19|20)\d{2}\b', ' ', bare)
            bare = re.sub(r'[^A-Za-z]', '', bare)
            if len(bare) < 3:
                continue
            # Keep the words, drop the date - the date is a field now.
            kept = DAYS.sub('', DATE_RX2.sub('', DATE_RX.sub('', h.group(2))))
            kept = re.sub(r'\s{2,}', ' ', kept).strip(' -:,.!')
            out.append('#### ' + (kept or h.group(2)))
            continue
        out.append(ln)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()

VENUES = [
    'Klunkerkranich', 'Crack Bellmer', 'Crackbellmer', 'Fitzroy', 'Marie Antoinette',
    'Neulant van Excel', 'Transistor Raum', 'Neulant', 'ACUD', 'LARK', 'Loophole',
    'LoopHole', 'Bar Drehmoment', 'De Helling', '90Mil', 'Berlin School of Sound',
]

TICKETS = re.compile(r'\[[^\]]*\]\((https://(?:ra\.co|dehelling\.nl)[^)]*)\)')
TIME_LINE = re.compile(r'^\*{0,2}(\d{1,2}[:.]\d{2})\*{0,2}\s*[-–]?\s+(.+)$')

NOISE = re.compile(
    r'archived\s*(event|stream|info)?|^\s*[-:,.]+|\bat\b|\bwith\b|\bon\b|\bthe\b',
    re.I)
DAYS = re.compile(r'\b(mon|tues?|wed(nes)?|thur?s?|fri|sat(ur)?|sun)(day)?\b\.?,?', re.I)

def event_name(head, venue):
    """The descriptive part of a heading - "Spectrum", "Earth Day", "DIY Kit Day"."""
    t = strip_md(re.sub(r'^#+\s*', '', head))
    t = NUM.sub(' ', t)
    t = DATE_RX.sub(' ', t)
    t = DATE_RX2.sub(' ', t)
    t = DAYS.sub(' ', t)
    if venue:
        t = re.sub(re.escape(venue), ' ', t, flags=re.I)
    t = re.sub(r'\b(19|20)\d{2}\b', ' ', t)
    t = NOISE.sub(' ', t)
    t = re.sub(r'[@()\[\]]', ' ', t)
    t = re.sub(r'\s{2,}', ' ', t).strip(' -:,.+&')
    return t if len(re.sub(r'[^A-Za-z]', '', t)) >= 3 else None

events = []
for j, i in enumerate(starts):
    end = starts[j + 1] if j + 1 < len(starts) else len(lines)
    head = lines[i].strip()
    chunk = [l for l in lines[i + 1:end]]
    text = '\n'.join(chunk)

    nm = NUM.search(head)
    number = f"BMS{'AV' if nm.group(1) else ''}{nm.group(2)}"

    # Date: prefer the heading, then the first few lines under it.
    d = find_date(head) or find_date('\n'.join(chunk[:8]))

    venue = next((v for v in VENUES if v.lower() in strip_md(head + '\n' + text[:400]).lower()), None)
    venue = {'Crackbellmer': 'Crack Bellmer', 'LoopHole': 'Loophole',
             'Neulant': 'Neulant van Excel'}.get(venue, venue)

    tm = TICKETS.search(text)

    # A run of two or more "HH:MM act" lines is a running order, not prose.
    lineup, rest, run = [], [], []
    def flush():
        if len(run) >= 2:
            lineup.extend(run)
        else:
            rest.extend(src for _, src in ((x, x['_src']) for x in run))
        run.clear()
    for ln in chunk:
        m = TIME_LINE.match(ln.strip())
        if m and strip_md(m.group(2)):
            run.append({'time': m.group(1).replace('.', ':'),
                        'act': strip_md(m.group(2)), '_src': ln})
        else:
            flush()
            rest.append(ln)
    flush()
    for a in lineup:
        a.pop('_src', None)

    rest_md = re.sub(r'\n{3,}', '\n\n', '\n'.join(rest)).strip()

    events.append({
        'number': number,
        'date': f'{d[2]:04d}-{d[0]:02d}-{d[1]:02d}' if d and d[2] else None,
        '_partialDate': f'{d[0]:02d}-{d[1]:02d}' if d and not d[2] else None,
        'name': event_name(head, venue),
        'venue': venue,
        'city': CITY.get((venue or '').lower(), 'Berlin'),
        'url': tm.group(1) if tm else None,
        'lineup': lineup,
        'body': clean_body(rest_md, venue),
    })

# BMS59 was never in the archive - it was the "Next Event" heading on the Super
# homepage, retyped there by hand. It belongs in the same list as everything else,
# and it also anchors the year walk below for BMS58 and BMS57.
events.insert(0, {
    'number': 'BMS59',
    'date': '2026-09-25',
    'name': 'Pollen',
    'venue': '90Mil',
    'city': 'Berlin',
    'url': 'https://ra.co/events/2536386',
    'lineup': [
        {'time': '19:00', 'act': 'Ambient Tai Chi + MAPP: Simon Redfern + Mitch Altman',
         'url': 'https://www.ambienttaichi.com/', 'space': 'Movement Space or Outside'},
        {'time': '20:30', 'act': 'trismo', 'instagram': ['trismooo'],
         'space': 'Movement Space'},
        {'time': '21:00', 'act': 'Phoebe Killdeer & THE SHIFT',
         'instagram': ['phoebekilldeerandtheshift'], 'space': 'Movement Space'},
        {'time': '22:00', 'act': 'NEVERSLEEP feat. E. SHAPERE',
         'url': 'http://neversleepmusic.de', 'instagram': ['NEVERSLEEPmusic'],
         'space': 'Movement Space'},
        {'time': '23:00', 'act': 'Vile Tensor', 'instagram': ['vile.tensor'],
         'space': 'Movement Space'},
        {'time': '00:00', 'act': 'Rocco.fx & Depuratumba',
         'instagram': ['Rocco.fx', 'depuratumba'], 'space': 'Movement Space'},
        {'time': '01:00', 'act': '(other collective takes space)', 'space': 'Movement Space'},
        {'time': '02:00', 'act': '3rd Party Influence', 'url': 'https://3pi.tv/',
         'instagram': ['3rdPartyInfluence'], 'space': 'Project Space'},
        {'time': '04:00', 'act': 'Ends'},
    ],
    'body': 'There are several other performance and workshop spaces, and the whole '
            'event runs from 16:00 to 04:00.',
    'note':
        'BMS59 takes place in the context of [Pollen](https://ra.co/events/2536386) — a 24 hour interdisciplinary festival. You will need to have / get membership for 5 Euros and then there is a suggested donation of 20 to 30 Euros. The second image shows the broader context for the night.',
})

# Events are written newest-first and the sequence never goes backwards, so an event
# that gave only "Thursday 7th March" takes the latest year that still lands it before
# the event above it. One dated anchor is enough to carry a whole undated run.
def as_ymd(d):
    return tuple(int(x) for x in d.split('-'))

upper = None   # the date of the next-newer event; nothing may be on or after it
for e in events:
    if e['date']:
        if upper and as_ymd(e['date']) >= as_ymd(upper):
            print(f"  ! {e['number']} {e['date']} is not older than {upper} - check by hand")
        upper = e['date']
        continue
    if not e['_partialDate']:
        continue
    mm, dd = e['_partialDate'].split('-')
    if upper is None:
        continue
    uy, um, ud = as_ymd(upper)
    y = uy if (int(mm), int(dd)) < (um, ud) else uy - 1
    e['date'] = f'{y:04d}-{mm}-{dd}'
    e['inferredYear'] = True
    upper = e['date']

for e in events:
    e.pop('_partialDate', None)

# The facts go in events.json; the prose goes in src/content/events/<number>.md.
#
# Both halves could have lived in the JSON, but an event body carries <Photo> and
# <Embed> tags, and those are Svelte components - mdsvex has to compile them. A
# markdown string inside JSON would only ever render as text. Splitting it also keeps
# the prose editable as prose.
EVENTS_MD = os.path.join(PROJ, 'src', 'content', 'events')
os.makedirs(EVENTS_MD, exist_ok=True)

COMPONENTS = {'Photo': '$lib/components/Photo.svelte',
              'Color': '$lib/components/Color.svelte',
              'Embed': '$lib/components/Embed.svelte'}

written = 0
for e in events:
    body = e.pop('body', '').strip()
    e['slug'] = e['number'].lower()
    e['hasBody'] = bool(body)
    if not body:
        continue
    used = sorted(c for c in COMPONENTS if re.search(rf'<{c}[ />]', body))
    script = ''
    if used:
        imports = '\n'.join(f"\timport {c} from '{COMPONENTS[c]}';" for c in used)
        script = f'<script>\n{imports}\n</script>\n\n'
    def photo_id(mm):
        new = idmap.get(mm.group(1))
        if new is None:
            raise SystemExit(f"unmapped photo id {mm.group(1)!r} in {e['number']}")
        return f'<Photo id="{new}" />'
    body = re.sub(r'<Photo id="([^"]+)" />', photo_id, body)

    open(os.path.join(EVENTS_MD, f"{e['slug']}.md"), 'w', encoding='utf8').write(
        script + body + '\n')
    written += 1

# Curated event data, overlaid on whatever the parse produced.
#
# post-fixes.json is the master record for event facts. It holds things the parser
# cannot know or got wrong:
#
#   - dates and line-ups for BMS1-BMS9 and BMSAV1, which predate the old site (its
#     archive began at BMS10) and came off Facebook. Facebook returns HTTP 400 to any
#     logged-out request, so these cannot be re-fetched without a session.
#   - line-ups the parser could not see, because the archive wrote them as prose or
#     arrow-separated on one line rather than as a timed run.
#   - event flyers, as `image`.
#   - `facebookNote`, where the Facebook billing differs from the archive. The archive
#     is the master record; the Facebook version is reported, not silently applied.
#
# Regenerate after editing events.json by hand:
#   python3 -c "import json; e=json.load(open('src/lib/data/events.json')); \
#     k=['date','name','venue','city','url','image','lineup','facebookNote']; \
#     json.dump({x['number']:{a:x[a] for a in k if x.get(a)} for x in e}, \
#     open('scripts/migration/post-fixes.json','w'), indent=2, ensure_ascii=False)"
POST_FIXES = json.load(open(os.path.join(SCRATCH, 'post-fixes.json'), encoding='utf8'))

for e in events:
    fix = POST_FIXES.get(e['number'], {})
    for k, v in fix.items():
        e[k] = v
    # A date confirmed by Facebook is no longer a guess.
    if 'date' in fix and fix['date'] == e.get('date'):
        e.pop('inferredYear', None)

out = os.path.join(PROJ, 'src', 'lib', 'data', 'events.json')
json.dump(events, open(out, 'w', encoding='utf8'), indent=2, ensure_ascii=False)
print(f'event bodies written: {written}')

dated = sum(1 for e in events if e['date'])
print(f'events: {len(events)}   dated: {dated}   undated: {len(events) - dated}')
for e in events:
    flag = ' ' if e['date'] else '?'
    print(f" {flag}{e['number']:8s} {e['date'] or '----------'}  {(e['venue'] or '-'):22s} "
          f"lineup={len(e['lineup']):2d} body={'yes' if e['hasBody'] else '-'}")
