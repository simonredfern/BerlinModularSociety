import re, unicodedata

# Slots that are not a performer.
NOT_ARTIST = {
    'ends', 'modular roulette', 'modular roulette + special guests',
    'talk with freedom boxes', 'other collective takes space',
    '(other collective takes space)', 'dj set', 'modular roulette + special guests tbc',
}

# Names that contain a separator word but are one artist.
DO_NOT_SPLIT = {
    'chor für oberton und kehlgesang',   # German "und" - one choir
    'krach der roboter', 'lost between layers', 'not for human consumption',
    'nikita and anton',                  # confirmed one act, not two people
    'mau\'s acid machine', 'berlin modular society',
    'phoebe killdeer & the shift',       # a band, not a collaboration
}

# Billings the generic splitter cannot read.
OVERRIDE = {
    'Ambient Tai Chi: Simon Redfern + Mitch Altman': ['Ambient Tai Chi'],
    '3rd Party Influence (duo set: Simon Redfern and Daniel Tippmann) with Optical '
    'Collusion on visuals': ['3rd Party Influence', 'Optical Collusion'],
    # VTVT *is* Veith von Tsotzhousn and VanTa, so splitting double-counts them.
    'Veith von Tsotzhousn and VanTa (VTVT)': ['VTVT'],
    'VTVT w/ VanTa on visuals': ['VTVT'],
}

# Trailing or leading noise around a name.
QUAL = re.compile(
    r'\s*(\((?:[^()]*)\)|\[[^\]]*\])\s*$'          # (A/V show), [Detroit Underground]
    r'|\s*\*live\s*$'
    r'|\s+on\s+visuals?\s*$', re.I)
LEAD = re.compile(r'^\s*(\(dj\)|live\s+visuals?\s+by|visuals?\s+by|dj)\s+', re.I)

# Different names for the same artist. Keyed on the cleaned billing, case-insensitive.
# Only for genuinely different names - a case variant is handled automatically.
ALIAS = {
    'cuckoo': 'True Cuckoo',          # billed CUCKOO at BMS43, handle @truecuckoo
    'miquel': 'Miquel Dangla',        # billed MIQUEL at BMS28, handle @miqueldangla
    'vasco': 'Vasco Ispirian',        # billed Vasco at BMS16; confirmed same person
}

SPLIT = re.compile(r'\s+(?:b2b|x|w/|with|and|feat\.?|vs\.?)\s+|\s*&\s*|\s*\+\s*', re.I)

def clean(s):
    prev = None
    while prev != s:
        prev = s
        s = QUAL.sub('', s).strip()
    s = LEAD.sub('', s).strip()
    return ' '.join(s.split()).strip(' ,-–')

def split_act(act):
    """The individual artists in one billed slot."""
    if act in OVERRIDE:
        return list(OVERRIDE[act])
    a = clean(act)
    if not a or a.lower() in NOT_ARTIST:
        return []
    if a.lower() in DO_NOT_SPLIT:
        return [ALIAS.get(a.lower(), a)]
    parts = [clean(p) for p in SPLIT.split(a)]
    parts = [p for p in parts if p and p.lower() not in NOT_ARTIST and len(p) > 1]
    parts = [ALIAS.get(p.lower(), p) for p in parts]
    return parts or [ALIAS.get(a.lower(), a)]

def slug(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()
    return s or 'unknown'
