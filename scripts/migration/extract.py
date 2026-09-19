import re, json, glob, html, os
from html.parser import HTMLParser

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCRATCH, 'out')

PAGES = [
    ('page.html', '', 'Home'),
    ('p_upcoming-dates.html', 'upcoming-dates', 'Upcoming Dates'),
    ('p_event-archive.html', 'event-archive', 'Event Archive'),
    ('p_about.html', 'about', 'About'),
    ('p_community.html', 'community', 'Community'),
    ('p_modular-courses.html', 'modular-courses', 'Modular Courses'),
    ('p_submit.html', 'submit', 'Artist Submission'),
    ('p_artist-area.html', 'artist-area', 'Artist Area'),
    ('p_artist-area__for-performers.html', 'artist-area/for-performers', 'For Performers'),
    ('p_artist-area__artist-payments.html', 'artist-area/artist-payments', 'Artist Payments'),
    ('p_artist-area__performing-with-video.html', 'artist-area/performing-with-video', 'Performing with Video'),
    ('p_artist-area__using-obs.html', 'artist-area/using-obs', 'Using OBS'),
    ('p_artist-area__using-mkv-files.html', 'artist-area/using-mkv-files', 'Using MKV Files'),
    ('p_artist-area__streaming-test.html', 'artist-area/streaming-test', 'Streaming Test'),
    ('p_artist-area__media-assets.html', 'artist-area/media-assets', 'Media Assets'),
    ('p_artist-area__media-assets__media-assets-archive.html', 'artist-area/media-assets/media-assets-archive', 'Media Assets Archive'),
    ('p_br-mood-board.html', 'br-mood-board', 'BR Mood Board'),
]

class Node:
    def __init__(self, tag, attrs=None):
        self.tag = tag
        self.attrs = dict(attrs or {})
        self.kids = []
        self.text = ''
    def cls(self):
        return self.attrs.get('class', '')

VOID = {'img','br','hr','input','meta','link','source','circle','rect','stop','path','use'}

class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].kids.append(n)
        if tag not in VOID:
            self.stack.append(n)
    def handle_startendtag(self, tag, attrs):
        self.stack[-1].kids.append(Node(tag, attrs))
    def handle_endtag(self, tag):
        if tag in VOID: return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
    def handle_data(self, data):
        n = Node('#text'); n.text = data
        self.stack[-1].kids.append(n)

# Notion let you colour a span or a whole block. Super emitted that as
# class="color-orange" and friends; app.css defines the matching .nc-* classes.
COLOURS = {'gray', 'brown', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'red'}
COLOR_RX = re.compile(r'\bcolor-([a-z]+)\b')

def colour_of(node):
    """The Notion colour on this node, if it carries one. 'default' is not one."""
    m = COLOR_RX.search(node.cls())
    return m.group(1) if m and m.group(1) in COLOURS else None

def wrap_colour(text, colour):
    """Inline colour. Safe anywhere except at the very start of a block."""
    if not colour or not text.strip():
        return text
    return f'<span class="nc-{colour}">{text}</span>'


def wrap_colour_block(text, colour):
    """A whole coloured paragraph.

    mdsvex stops parsing markdown inside a line that opens with a tag, so a
    <span> wrapped round a paragraph would leave **bold** and [links](/x) as
    literal text. The <Color> component, with blank lines around the content,
    keeps the markdown working. A paragraph that merely *starts* with a
    coloured span hits the same limitation and comes through here too.
    """
    if not text.strip():
        return text
    return f'<Color c="{colour}">\n\n{text}\n\n</Color>'

def esc_md(s):
    # Escape only what would break markdown/mdsvex
    return s.replace('\\', '\\\\').replace('{', '&#123;').replace('}', '&#125;').replace('<', '&lt;').replace('>', '&gt;')

def emph(t, marker):
    """Wrap in emphasis markers while keeping surrounding whitespace outside them."""
    core = t.strip()
    if not core:
        return t
    lead = t[:len(t) - len(t.lstrip())]
    trail = t[len(t.rstrip()):]
    return f'{lead}{marker}{core}{marker}{trail}'

def inline(node):
    """Render inline content (text, links, strong, em) to markdown."""
    out = []
    for k in node.kids:
        if k.tag == '#text':
            out.append(esc_md(k.text))
        elif k.tag == 'a':
            href = k.attrs.get('href', '')
            raw = inline(k)
            label = raw.strip()
            if not label: continue
            # Keep whitespace that sat inside the <a> outside the markdown link,
            # or "Artist Submission </a>page." renders as "...(/submit)page."
            lead = raw[:len(raw) - len(raw.lstrip())]
            trail = raw[len(raw.rstrip()):]
            out.append(f'{lead}[{label}]({href}){trail}')
        elif k.tag in ('strong', 'b'):
            out.append(emph(inline(k), '**'))
        elif k.tag in ('em', 'i'):
            out.append(emph(inline(k), '*'))
        elif k.tag in ('br',):
            out.append('\n')
        elif k.tag in ('svg', 'script', 'style'):
            continue
        elif k.tag == 'span' and colour_of(k):
            out.append(wrap_colour(inline(k), colour_of(k)))
        else:
            out.append(inline(k))
    return ''.join(out)

def plain(node):
    out = []
    for k in node.kids:
        if k.tag == '#text': out.append(k.text)
        elif k.tag in ('svg','script','style'): continue
        else: out.append(plain(k))
    return ''.join(out)

IMG_BASE = re.compile(r'(https://images\.spr\.so/[^\s"\']+?)/(?:public|w=\d+[^\s"\']*)')

def img_key(url):
    m = IMG_BASE.match(url)
    base = m.group(1) if m else url
    return base.rsplit('/', 1)[-1], base

CREDIT_RX = re.compile(
    r'[\s.,\-–—]*\b(?:photo(?:graph(?:er|y)?)?|phtographer|pic|image|shot)\s*(?:by|:)?[\s:]*(\S.*)$',
    re.I | re.S)
HANDLE_RX = re.compile(r'@?\[([^\]]+)\]\(([^)]+)\)')

def split_credit(caption_md):
    """Split a trailing photographer credit off a markdown caption.
    Returns (caption, credit_name, credit_url)."""
    if not caption_md:
        return caption_md, None, None
    m = CREDIT_RX.search(caption_md)
    if not m:
        return caption_md.strip(), None, None
    credit_md = m.group(1).strip(' .,…')
    caption = caption_md[:m.start()].strip(' .,…\n')
    url = None
    hm = HANDLE_RX.search(credit_md)
    if hm:
        url = hm.group(2)
        credit_md = HANDLE_RX.sub(lambda x: '@' + x.group(1), credit_md)
    credit_md = re.sub(r'\s*@\s*', ' @', credit_md).strip(' .,@')
    credit_md = re.sub(r'\s{2,}', ' ', credit_md)
    # A "credit" longer than a name is really caption prose - reject it
    if not credit_md or len(credit_md.split()) > 6:
        return caption_md.strip(), None, None
    return caption, credit_md, url


images = {}

def register_image(url, alt, caption_md, caption_txt, w, h, page):
    name, base = img_key(url)
    source_md = caption_md or esc_md(alt or '')
    cap, credit, credit_url = split_credit(source_md)
    # Plain-text caption, for alt text
    cap_plain = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', cap)
    cap_plain = re.sub(r'[*_`]', '', cap_plain).strip()
    rec = images.setdefault(name, {
        'name': name, 'base': base, 'alt': '', 'caption': '',
        'credit': None, 'creditUrl': None, 'pages': []
    })
    if cap and not rec['caption']:
        rec['caption'] = cap
    if not rec['alt']:
        rec['alt'] = cap_plain or (alt or '').strip()
    if credit and not rec['credit']:
        rec['credit'] = credit
        rec['creditUrl'] = credit_url
    if page not in rec['pages']:
        rec['pages'].append(page)
    return name

def find_img(node):
    if node.tag == 'img': return node
    for k in node.kids:
        r = find_img(k)
        if r is not None: return r
    return None

def find_iframe(node):
    if node.tag == 'iframe': return node
    for k in node.kids:
        r = find_iframe(k)
        if r is not None: return r
    return None

def find_cls(node, cls):
    if cls in node.cls(): return node
    for k in node.kids:
        r = find_cls(k, cls)
        if r is not None: return r
    return None

def block(node, page, depth=0):
    """Render a block-level node to markdown lines."""
    c = node.cls()
    t = node.tag
    out = []

    if t in ('script', 'style', 'svg', 'nav'):
        return out

    if 'notion-image' in c:
        im = find_img(node)
        if im is None: return out
        src = im.attrs.get('src', '')
        fig = find_cls(node, 'notion-caption')
        cap_md = inline(fig).strip() if fig is not None else ''
        cap_txt = plain(fig).strip() if fig is not None else ''
        name = register_image(src, im.attrs.get('alt', ''), cap_md, cap_txt,
                              im.attrs.get('width'), im.attrs.get('height'), page)
        out.append(f'<Photo id="{name}" />')
        return out

    if 'notion-embed' in c:
        fr = find_iframe(node)
        if fr is None: return out
        src = html.unescape(fr.attrs.get('src', ''))
        src = re.split(r'["\'<]', src)[0]
        title = fr.attrs.get('title', '')
        out.append(f'<Embed src="{src}" title="{title}" />')
        return out

    if t in ('h1','h2','h3','h4','h5','h6') or 'notion-heading' in c:
        lvl = int(t[1]) if t.startswith('h') and t[1].isdigit() else 2
        txt = inline(node).strip()
        m2 = re.fullmatch(r'\*\*(.+)\*\*', txt, flags=re.S)
        if m2 and '**' not in m2.group(1):
            txt = m2.group(1).strip()
        if txt: out.append('#' * max(2, lvl) + ' ' + wrap_colour(txt, colour_of(node)))
        return out

    if 'notion-column-list' in c:
        out.append('<Columns>')
        for k in node.kids:
            if 'notion-column' in k.cls():
                out.append('<Column>')
                for kk in k.kids:
                    out.extend(block(kk, page, depth + 1))
                out.append('</Column>')
        out.append('</Columns>')
        return out

    if t in ('ul', 'ol') or 'notion-bulleted-list' in c or 'notion-numbered-list' in c:
        marker = '1.' if t == 'ol' or 'numbered' in c else '-'
        for li in node.kids:
            if li.tag != 'li' and 'notion-list-item' not in li.cls():
                out.extend(block(li, page, depth))
                continue
            txt = inline(li).strip()
            if txt: out.append(f'{marker} {txt}')
        return out

    if t in ('p',) or 'notion-text' in c:
        # A notion-text div may wrap nested blocks; check for block children first
        has_block = any(
            ('notion-image' in k.cls() or 'notion-embed' in k.cls() or 'notion-column-list' in k.cls()
             or k.tag in ('ul','ol','h1','h2','h3'))
            for k in node.kids)
        if has_block:
            for k in node.kids:
                out.extend(block(k, page, depth))
            return out
        txt = inline(node).strip()
        if not txt:
            return out
        c = colour_of(node)
        if c:
            out.append(wrap_colour_block(txt, c))
        elif txt.startswith('<span class="nc-'):
            # An inline span is fine mid-sentence but not as the first thing in
            # a block - mdsvex would treat the whole paragraph as raw HTML.
            out.append(wrap_colour_block(txt, 'plain'))
        else:
            out.append(txt)
        return out

    if t == 'a' and ('notion-page' in c or 'notion-link' in c):
        label = plain(node).strip()
        href = node.attrs.get('href', '')
        if label: out.append(f'- [{label}]({href})')
        return out

    # generic container: recurse
    for k in node.kids:
        if k.tag == '#text':
            if k.text.strip(): out.append(esc_md(k.text.strip()))
        else:
            out.extend(block(k, page, depth))
    return out

HEADER_RX = re.compile(r'<div[^>]*class="[^"]*notion-header\b.*?(?=<article)', re.S)

def extract_header(src, page):
    """The Super page header - cover photo and page icon.

    These sit *outside* <article class="notion-root">, which is why the first
    pass through this script lost them: the homepage banner and the big BMS logo
    were never in the part of the page being walked.
    """
    m = HEADER_RX.search(src)
    if not m:
        return None, None, None
    h = m.group(0)

    def grab(cls):
        im = re.search(rf'<img[^>]*class="{cls}"[^>]*>', h)
        if not im:
            return None
        srcm = re.search(r'src="([^"]*)"', im.group(0))
        altm = re.search(r'alt="([^"]*)"', im.group(0))
        if not srcm:
            return None
        return register_image(html.unescape(srcm.group(1)),
                              altm.group(1) if altm else '', '', '', None, None, page)

    tm = re.search(r'<h1[^>]*class="notion-header__title"[^>]*>(.*?)</h1>', h, re.S)
    header_title = html.unescape(re.sub(r'<[^>]+>', '', tm.group(1))).strip() if tm else None

    return grab('notion-header__cover-image'), grab('notion-header__icon'), header_title


def extract(fname, slug, title):
    src = open(os.path.join(SCRATCH, fname), encoding='utf8', errors='ignore').read()
    m = re.search(r'<article[^>]*class="notion-root.*?</article>', src, flags=re.S)
    if not m:
        raise SystemExit(f'no article in {fname}')
    tp = Tree(); tp.feed(m.group(0))
    art = tp.root.kids[0]
    page = slug or 'index'
    cover, icon, header_title = extract_header(src, page)
    lines = block(art, page)

    # collapse blank runs, drop empties
    body, prev = [], None
    for ln in lines:
        ln = ln.rstrip()
        if not ln.strip():
            continue
        if ln == prev:
            continue
        body.append(ln)
        prev = ln

    desc = ''
    dm = re.search(r'<meta name="description" content="([^"]*)"', src)
    if dm: desc = html.unescape(dm.group(1)).strip()
    return page, header_title or title, desc, body, cover, icon

manifest_pages = []
for fname, slug, title in PAGES:
    page, title, desc, body, cover, icon = extract(fname, slug, title)
    manifest_pages.append({'slug': slug, 'page': page, 'title': title, 'description': desc,
                           'blocks': len(body), 'cover': cover, 'icon': icon})
    fm = ['---', f'title: {json.dumps(title)}', f'description: {json.dumps(desc)}']
    if cover: fm.append(f'cover: {json.dumps(cover)}')
    if icon: fm.append(f'icon: {json.dumps(icon)}')
    fm += ['---', '']
    dest = os.path.join(OUT, f'{page}.md')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'w', encoding='utf8').write(
        '\n'.join(fm) + '\n\n'.join(body) + '\n')

json.dump(images, open(os.path.join(OUT, 'images.json'), 'w', encoding='utf8'), indent=2, ensure_ascii=False)
json.dump(manifest_pages, open(os.path.join(OUT, 'pages.json'), 'w', encoding='utf8'), indent=2, ensure_ascii=False)
print(f'pages: {len(manifest_pages)}  images: {len(images)}')
for p in manifest_pages:
    extra = ' '.join(filter(None, ['cover' if p['cover'] else '', 'icon' if p['icon'] else '']))
    print(f"  {p['page']:45s} {p['blocks']:3d} blocks  {extra}")
credited = sum(1 for v in images.values() if v['credit'])
print(f'images with credit parsed: {credited}/{len(images)}')
