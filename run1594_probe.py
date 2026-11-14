#!/usr/bin/env python3
"""Run 1594 probe: cross-window reading-name check under run 1586's collision rule.

Open question from run 1593: the nine-seat itemization name appears in four
sentences across four windows and the bank-export reading name in two
sentences in one window. Check fresh:
  (a) no covering clause anywhere names the nine-seat itemization,
  (b) each non-reach tail naming nine-seat itemization sits beside a rule
      that pins its own window (the clause's "since that rule covers ..."
      phrase names a loss window),
  (c) both names stay confined as adjudicated in run 1593:
      nine-seat itemization in exactly four sentences across four windows,
      bank-export reading in exactly two sentences in one window,
      nine-seat pre-marking reading in exactly the one mirror sentence.
Also re-verify the stable census counts (55 non-reach, 26 verdict-family,
29 non-verdict, 23 coverless, 6 covered, 29 covering-clause sentences).
"""
import re, hashlib
from collections import Counter, defaultdict

PATH = '/home/hatch/repos/ai-producer-camp/index.html'
txt = open(PATH).read()
AUDIT_RE = re.compile(r'<section id="run-(\d+)-audit">.*?</section>\s*', re.S)
live = AUDIT_RE.sub('', txt)
print("full md5:", hashlib.md5(txt.encode()).hexdigest(), "bytes:", len(txt.encode()))
print("live md5:", hashlib.md5(live.encode()).hexdigest(), "bytes:", len(live.encode()))
print("audit sections:", len(AUDIT_RE.findall(txt)), "em-dash live:", live.count('\u2014'))

stripped = re.sub(r'<[^>]+>', ' ', live)
normtext = re.sub(r'\s+', ' ', stripped)
work = re.sub(r'(\d)\.(\d)', r'\1<DEC>\2', normtext)
parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"])', work)
sentences = []
for p in parts:
    s = p.replace('<DEC>', '.').strip()
    s = re.sub(r'\s+', ' ', s)
    if len(s) > 20:
        sentences.append(s)
print("total sentences (live, len>20):", len(sentences))

# --- stable census counts (same classifier as runs 1590-1593) ---
nonreach = [(i, s) for i, s in enumerate(sentences) if 'does not reach this' in s]
covering = [(i, s) for i, s in enumerate(sentences) if 'covers this' in s]
print("non-reach sentences:", len(nonreach))
print("covering-clause sentences:", len(covering))
# verdict-family: sentences whose head is a verdict-style "A July 2 instructor folder..."
verdict = [(i, s) for i, s in nonreach if s.startswith('A July 2 instructor folder')]
print("verdict-family non-reach:", len(verdict), " non-verdict non-reach:", len(nonreach) - len(verdict))
covered_names = set()
for i, s in covering:
    for m in re.findall(r'covers this ([^,.;]+?)(?: reading| itemization)', s):
        covered_names.add(m.strip())
print("distinct covering-clause reading names:", len(covered_names))

def window_of(s):
    m = re.match(r'A July 2 instructor folder lost or damaged ([^.]*?) leaves', s)
    if m:
        return m.group(1).strip()
    m = re.search(r'folder (?:was )?lost or damaged ([^.]*?)(?:,| leaves| since)', s)
    if m:
        return m.group(1).strip()
    # session-book piece sentences
    m = re.search(r'lost or damaged ([^.]*?)(?:,| leaves| since)', s)
    if m:
        return m.group(1).strip()
    return None

# --- (a) covering clauses naming nine-seat itemization ---
bad_cover = []
for i, s in covering:
    if 'covers this nine-seat itemization' in s:
        bad_cover.append((i, s))
print("\n=== (a) covering clauses naming 'nine-seat itemization':", len(bad_cover), "===")
for i, s in bad_cover:
    print("  -", s[:300])

# --- (b)+(c) nine-seat itemization occurrences ---
print("\n=== nine-seat itemization occurrences ===")
nsi_sents = [(i, s) for i, s in enumerate(sentences) if 'nine-seat itemization' in s]
print("sentences containing 'nine-seat itemization':", len(nsi_sents))
print("occurrences live:", live.count('nine-seat itemization'))
winmap = defaultdict(list)
for i, s in nsi_sents:
    w = window_of(s)
    winmap[w].append(i)
    occ = s.count('nine-seat itemization')
    kinds = []
    if 'covers this nine-seat itemization' in s:
        kinds.append('COVERING')
    nr = len(re.findall(r'does not reach this nine-seat itemization', s))
    if nr:
        kinds.append(f'NON-REACH x{nr}')
    # for each non-reach tail, extract the rule and its pinned window
    tails = re.findall(r'the ([a-zA-Z0-9\-]+) rule does not reach this nine-seat itemization(?: reading)?(?: either)?, since that rule covers ([^,.;]+)', s)
    print(f"  [{i}] win={w!r} occ={occ} kinds={kinds}")
    for rule, pinned in tails:
        print(f"      tail rule={rule!r} pins window={pinned.strip()!r}")
    print(f"      :: {s[:160]}")
print("distinct windows for nine-seat itemization:", len(winmap))
for w, idxs in sorted(winmap.items(), key=lambda kv: str(kv[0])):
    print(f"  {w!r} -> sentence idx {idxs}")

# check: every non-reach tail naming it has a pinned window phrase
unpinned = []
for i, s in nsi_sents:
    for m in re.finditer(r'does not reach this nine-seat itemization', s):
        tail = s[m.start():m.start()+400]
        if 'since that rule covers' not in tail:
            unpinned.append((i, tail[:200]))
print("non-reach tails naming nine-seat itemization WITHOUT a pinning window phrase:", len(unpinned))
for i, t in unpinned:
    print("  -", i, t)

# --- bank-export reading confinement ---
print("\n=== bank-export reading occurrences ===")
ber_sents = [(i, s) for i, s in enumerate(sentences) if 'bank-export reading' in s]
print("sentences containing 'bank-export reading':", len(ber_sents))
print("occurrences live:", live.count('bank-export reading'))
ber_wins = set()
for i, s in ber_sents:
    w = window_of(s)
    ber_wins.add(w)
    kinds = []
    if 'covers this bank-export reading' in s:
        kinds.append('COVERING')
    nr = len(re.findall(r'does not reach this bank-export reading', s))
    if nr:
        kinds.append(f'NON-REACH x{nr}')
    print(f"  [{i}] win={w!r} occ={s.count('bank-export reading')} kinds={kinds} :: {s[:160]}")
print("distinct windows for bank-export reading:", len(ber_wins), sorted(str(w) for w in ber_wins))

# nine-seat bank-export reading is a DISTINCT name; count separately
print("occurrences of distinct name 'nine-seat bank-export reading':", live.count('nine-seat bank-export reading'))
nber_sents = [(i, s) for i, s in enumerate(sentences) if 'nine-seat bank-export reading' in s]
print("sentences containing it:", len(nber_sents))
for i, s in nber_sents:
    print(f"  [{i}] win={window_of(s)!r} :: {s[:160]}")

# --- nine-seat pre-marking reading confinement ---
print("\n=== nine-seat pre-marking reading occurrences ===")
print("occurrences live:", live.count('nine-seat pre-marking reading'))
npm_sents = [(i, s) for i, s in enumerate(sentences) if 'nine-seat pre-marking reading' in s]
print("sentences containing it:", len(npm_sents))
for i, s in npm_sents:
    print(f"  [{i}] win={window_of(s)!r} occ={s.count('nine-seat pre-marking reading')} :: {s[:160]}")

# --- any covering clause naming nine-seat itemization OR bank-export outside the adjudicated mirror? ---
print("\n=== covering clauses by reading name (tail) ===")
c = Counter()
for i, s in covering:
    for m in re.findall(r'covers this ([^,.;]+?)(?: reading| itemization)', s):
        c[m.strip()] += 1
for k, v in sorted(c.items()):
    print(f"  {v}x {k!r}")
