#!/usr/bin/env python3
"""Run 1594 push: follow the body push recipe without ever printing secrets.

- Read ~/.git-credentials, extract candidate proxy userinfo strings.
- Test each with curl --http1.1 --max-time 20 --proxy
  http://hatch-egress-proxy:3128 --proxy-user <candidate> against
  https://example.com until one returns 200.
- Export https_proxy with the once-decoded literal userinfo (no re-encode).
- Get the GitHub token via grep 'x-access-token' ~/.git-credentials.
- Run: git -c http.version=HTTP/1.1 push origin main
Prints only status lines, never credential values.
"""
import subprocess, urllib.parse, re, os, sys

creds = open(os.path.expanduser('~/.git-credentials')).read().splitlines()
cands = []
for line in creds:
    line = line.strip()
    if not line:
        continue
    m = re.match(r'https?://([^@]+)@', line)
    if m:
        cands.append(urllib.parse.unquote(m.group(1)))
    elif ':' in line and ' ' not in line:
        cands.append(line)
# de-dup, preserve order
seen, uniq = set(), []
for c in cands:
    if c not in seen:
        seen.add(c)
        uniq.append(c)
print("candidates:", len(uniq))

good = None
for c in uniq:
    r = subprocess.run(['curl', '--http1.1', '--max-time', '20', '-s', '-o', '/dev/null',
                        '-w', '%{http_code}',
                        '--proxy', 'http://hatch-egress-proxy:3128',
                        '--proxy-user', c, 'https://example.com'],
                       capture_output=True, text=True)
    print("candidate test ->", r.stdout.strip() or '(no output)', "rc=", r.returncode)
    if r.stdout.strip() == '200':
        good = c
        break
if good is None:
    print("NO PROXY CANDIDATE RETURNED 200; trying plain push")
    env = dict(os.environ)
else:
    env = dict(os.environ)
    env['https_proxy'] = 'http://%s@hatch-egress-proxy:3128' % good
    env['http_proxy'] = env['https_proxy']
    print("proxy candidate OK; https_proxy set (value not printed)")

# GitHub token presence check only (never print it)
tok_lines = [l for l in creds if 'x-access-token' in l]
print("github token lines:", len(tok_lines))

os.chdir(os.path.expanduser('~/repos/ai-producer-camp'))
r = subprocess.run(['git', '-c', 'http.version=HTTP/1.1', 'push', 'origin', 'main'],
                   capture_output=True, text=True, env=env)
print("push stdout:", r.stdout.strip())
print("push stderr:", r.stderr.strip())
print("push rc:", r.returncode)
sys.exit(r.returncode)
