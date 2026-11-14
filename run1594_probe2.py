#!/usr/bin/env python3
"""Run 1594 probe 2: reconciled-classifier recount + bank-export standalone
confinement correction.

Probe 1 counted 'bank-export reading' as a raw substring, so sentence [2301]
(which carries only the DISTINCT name 'nine-seat bank-export reading' x4)
was miscounted as a third bank-export sentence. This probe counts standalone
'bank-export reading' (not preceded by 'nine-seat ') and re-runs the
reconciled classifier from run1589_probe.py for the stable counts.
"""
import re, hashlib

PATH = '/home/hatch/repos/ai-producer-camp/index.html'
txt = open(PATH).read()
AUDIT_RE = re.compile(r'<section id="run-(\d+)-audit">.*?</section>\s*', re.S)
live = AUDIT_RE.sub('', txt)

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

def lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n

def window(s):
    m = re.match(r'A July 2 instructor folder lost or damaged ([^.]*?) leaves', s)
    return m.group(1) if m else None

MAIN = re.compile(r'leaves the evening (able|unable|still unable) to tell from paper')
TABLE = re.compile(r"leaves the founder's 0:00-0:20 table-read")

mirror_idx = set()
for i in range(1, len(sentences)):
    s, prev = sentences[i], sentences[i-1]
    if ('covers this' in s and 'covers this' not in prev
            and 'does not reach this' in s and 'does not reach this' in prev
            and window(s) is not None and window(s) == window(prev)
            and lcp(s, prev) >= 250):
        mirror_idx.add(i)

nonreach = [s for s in sentences if 'does not reach this' in s]
vf, nv = [], []
for i, s in enumerate(sentences):
    if 'does not reach this' not in s:
        continue
    if i in mirror_idx:
        nv.append((i, s))
    elif 'tell from paper' in s and (MAIN.search(s) or TABLE.search(s)):
        vf.append((i, s))
    else:
        nv.append((i, s))
coverless_nv = [(i, s) for i, s in nv if 'covers this' not in s]
covered_nv = [(i, s) for i, s in nv if 'covers this' in s]
covering = [s for s in sentences if 'covers this' in s]
print("CENSUS non-reach=%d verdict=%d non-verdict=%d coverless=%d covered=%d covering-clause=%d mirrors=%d"
      % (len(nonreach), len(vf), len(nv), len(coverless_nv), len(covered_nv), len(covering), len(mirror_idx)))
print("mirror idx:", sorted(mirror_idx))

# --- standalone bank-export reading (not preceded by 'nine-seat ') ---
standalone = re.findall(r'(?<!nine-seat )bank-export reading', live)
print("\nstandalone 'bank-export reading' occurrences live:", len(standalone))
sb_sents = [(i, s) for i, s in enumerate(sentences)
            if re.search(r'(?<!nine-seat )bank-export reading', s)]
print("sentences containing standalone 'bank-export reading':", len(sb_sents))
for i, s in sb_sents:
    n = len(re.findall(r'(?<!nine-seat )bank-export reading', s))
    print(f"  [{i}] win={window(s)!r} standalone-occ={n} total-occ={s.count('bank-export reading')} :: {s[:120]}")
# sentence 2301 check: all 4 occurrences are the distinct nine-seat name
s2301 = sentences[2301]
print("\n[2301] 'nine-seat bank-export reading' occ:", s2301.count('nine-seat bank-export reading'),
      " standalone occ:", len(re.findall(r'(?<!nine-seat )bank-export reading', s2301)))

# --- nine-seat itemization: confirm the four sentences and their windows ---
print("\nnine-seat itemization sentences:")
for i, s in enumerate(sentences):
    if 'nine-seat itemization' in s:
        print(f"  [{i}] win={window(s)!r} occ={s.count('nine-seat itemization')} "
              f"covering={'covers this nine-seat itemization' in s} "
              f"nonreach-tails={len(re.findall(chr(39)+'does not reach this nine-seat itemization', s))}")
# every non-reach tail naming it: rule pins its own window (re-verify per-tail)
print("\nper-tail pin check:")
bad = 0
for i, s in enumerate(sentences):
    if 'nine-seat itemization' not in s:
        continue
    for m in re.finditer(r'the ([a-zA-Z0-9\-]+) rule does not reach this nine-seat itemization(?: reading)?(?: either)?, since that rule covers ([^,.;]+)', s):
        rule, pinned = m.group(1), m.group(2).strip()
        print(f"  [{i}] rule={rule!r} pinned={pinned!r}")
        if 'since that rule covers' not in s[m.start():m.start()+300]:
            bad += 1
print("tails missing pin phrase:", bad)
print("\nPROBE2 DONE")
