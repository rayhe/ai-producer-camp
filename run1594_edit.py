#!/usr/bin/env python3
"""Run 1594 edit: append the run-1594-audit section recording the fresh
cross-window reading-name census. No live-copy change: the census confirms
all three parts of run 1593's open question, so the edit is the audit
section only, carrying forward the accumulated chain from the run-1593
audit paragraph with this run's verdict clause appended.

Operates on the FULL file; audit sections are never stripped or rewritten.
Reverting (removing the new section) reproduces the original file byte
for byte.
"""
import re, hashlib

PATH = '/home/hatch/repos/ai-producer-camp/index.html'
txt = open(PATH).read()
AUDIT_RE = re.compile(r'<section id="run-(\d+)-audit">.*?</section>\s*', re.S)
print("pre-edit audit sections:", len(AUDIT_RE.findall(txt)))
print("pre-edit md5:", hashlib.md5(txt.encode()).hexdigest(), "bytes:", len(txt.encode()))
print("pre-edit em-dash full:", txt.count('\u2014'))
live = AUDIT_RE.sub('', txt)
print("pre-edit live md5:", hashlib.md5(live.encode()).hexdigest(), "bytes:", len(live.encode()))
assert len(AUDIT_RE.findall(txt)) == 870
assert hashlib.md5(txt.encode()).hexdigest() == '8053593771515222f811a0d860703b75'
assert hashlib.md5(live.encode()).hexdigest() == '6c1fb27a83a07453951ea29314914baf'
assert txt.count('\u2014') == 0
assert 'run-1594-audit' not in txt

m1593 = re.search(r'<section id="run-1593-audit">.*?</section>', txt, re.S)
assert m1593 is not None
sec1593 = m1593.group(0)
p1593 = re.search(r'<p>(.*)</p>', sec1593, re.S).group(1)
CHAIN_START = 'and now the twenty-two remaining coverless non-verdict sentences'
cs = p1593.find(CHAIN_START)
assert cs > 0, "chain start not found"
nx = p1593.find(' Next open work is to be censused fresh by run 1594:')
assert nx > cs, "next-open-work tail not found"
assert p1593[nx:].endswith('Run 1594 next.'), "unexpected tail: %r" % p1593[nx:][-60:]
chain = p1593[cs:nx]
assert chain.startswith(CHAIN_START)
assert chain.rstrip().endswith('six covered...'), "chain tail unexpected: %r" % chain[-80:]
print("carried chain chars:", len(chain))

INTRO = ("Run 1593 left open the cross-window reading-name question the probe this run surfaced, "
"that the nine-seat itemization name appears in four sentences across four windows and the "
"bank-export reading name in two sentences in one window, to be checked fresh under run 1586's "
"collision rule, to confirm no covering clause anywhere names the nine-seat itemization, each "
"non-reach tail naming it sits beside a rule that pins its own window, and both names stay "
"confined as adjudicated here, which is a fresh-census question, not a claim made here. A fresh "
"census this run confirms all three, with no live-copy change needed. The census, audit sections "
"stripped, live copy verified byte-identical to the local file before the census (md5 "
"6c1fb27a83a07453951ea29314914baf, the run-1593 deployment), reproduces the counts exactly: "
"fifty-five sentences carrying a non-reach clause live, twenty-six verdict-family and twenty-nine "
"non-verdict, twenty-three coverless non-verdict, six covered non-verdict, twenty-nine "
"covering-clause sentences, twenty-eight distinct covering-clause reading names. No covering "
"clause anywhere names the nine-seat itemization: zero occurrences of covers this nine-seat "
"itemization on the live copy. The name appears in exactly four sentences, one per loss window, "
"before July 2, after the July 2 re-score and before the July 2 post, after the 0:20-0:35 marking "
"and before the 0:50-1:00 re-score, and before the 0:20-0:35 marking, three occurrences in each "
"sentence, twelve in total, all inside non-reach tails, and all twelve tails sit beside a rule "
"that pins its own window, since each tail reads the rule does not reach this nine-seat "
"itemization reading, since that rule covers the folder lost or damaged in that rule's own window, "
"with zero tails lacking the pinning phrase. Each of the four sentences names exactly the three "
"rules other than the rule for its own loss window, so the own-window rule is the one that reaches "
"and no other rule is missing. The bank-export confinement holds, with one probe correction "
"recorded here so the next run does not repeat it: a raw substring count returns three sentences "
"and eleven occurrences, but four of those eleven are the substring inside the distinct name "
"nine-seat bank-export reading, confined to the single sentence immediately following the "
"bank-export mirror, which carries the pre-marking covering clause under that distinct name, so "
"the standalone bank-export reading occurs seven times in exactly two sentences, the original and "
"its mirror, both in the before the 0:20-0:35 marking window, with the mirror carrying the "
"pre-marking covering clause and the original carrying none. The nine-seat pre-marking reading "
"stays confined to the one mirror sentence, four occurrences, and the nine-seat bank-export "
"reading to the one following sentence, four occurrences, so no covering clause anywhere names a "
"reading shared across two loss windows, ")

VERDICT = ("and now the cross-window reading names censused fresh this run and found confined as "
"adjudicated, with zero covering clauses naming the nine-seat itemization, all twelve non-reach "
"tails naming it pinned to their own windows, the standalone bank-export reading in exactly two "
"sentences in one window, and the counts holding stable at fifty-five non-reach, twenty-six "
"verdict-family, twenty-nine non-verdict, twenty-three coverless, and six covered... ")

NEXT = ("Next open work is to be censused fresh by run 1595: the sentence immediately following the "
"bank-export mirror, which carries the pre-marking covering clause under the distinct nine-seat "
"bank-export reading name, should be checked fresh against run 1589's mirror criteria, same loss "
"window, shared prefix of at least 250 characters, covering clause naming the rule for its own "
"window, and non-reach tails renamed to the same reading name, to confirm whether it is a second "
"mirror of the bank-export original and whether the five-mirror count should be six, and whether "
"its distinct reading name collides with the mirror's bank-export reading under run 1586's rule, "
"which is a fresh-census question, not a claim made here. Run 1595 next.")

PARA = INTRO + chain + VERDICT + NEXT
AUDIT = ('<section id="run-1594-audit"> <h2>The cross-window reading names stay confined, and no '
'covering clause names the nine-seat itemization.</h2> <p>' + PARA + '</p> </section>\n')

assert '\u2014' not in AUDIT, "em dash in audit text"
assert '</body>' in txt
new_txt = txt.replace('</body>', AUDIT + '</body>', 1)
assert len(AUDIT_RE.findall(new_txt)) == 871
assert new_txt.count('\u2014') == 0
# prior audit section byte-identical
m1593_new = re.search(r'<section id="run-1593-audit">.*?</section>', new_txt, re.S)
assert m1593_new.group(0) == sec1593, "run-1593-audit section changed"
# reverting reproduces the original byte for byte
reverted = new_txt.replace(AUDIT, '', 1)
assert reverted == txt, "revert mismatch"
# live copy unchanged
live_new = AUDIT_RE.sub('', new_txt)
assert live_new == live, "live copy changed"
open(PATH, 'w').write(new_txt)
print("post-edit audit sections:", len(AUDIT_RE.findall(new_txt)))
print("post-edit md5:", hashlib.md5(new_txt.encode()).hexdigest(), "bytes:", len(new_txt.encode()))
print("post-edit live md5:", hashlib.md5(live_new.encode()).hexdigest())
print("EDIT DONE")
