"""Read-only public-resource diagnostics. Network failures are reported, not hidden.
Artwork copies are short-lived review artifacts, NOT a permanent repository archive.
Only this site's public pages and the existing NetEase artwork hosts are requested.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import json
import os
import re
import time

ROOT = Path('_site')
OUT = Path('external-review')
ALLOWED = {'www.werogue.com', 'p1.music.126.net', 'p2.music.126.net'}
MAX_BYTES = 5 * 1024 * 1024

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.in_h1 = False
        self.h1 = ''
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])
        if tag == 'h1':
            self.in_h1 = True
    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
    def handle_data(self, data):
        if self.in_h1:
            self.h1 += data

def get(url):
    parsed = urlsplit(url)
    assert parsed.scheme == 'https' and parsed.hostname in ALLOWED
    assert not parsed.username and not parsed.password and parsed.port in (None, 443)
    request = Request(url, headers={'User-Agent': 'WeRogue-link-check/1.0'})
    with urlopen(request, timeout=12) as response:
        assert urlsplit(response.url).hostname in ALLOWED, 'Unexpected redirect'
        data = response.read(MAX_BYTES + 1)
        assert len(data) <= MAX_BYTES, 'Response exceeds review limit'
        return response.status, response.headers.get('Content-Type', ''), data

def cover(url):
    result = {'url': url, 'ok': False}
    try:
        status, mime, data = get(url)
        is_jpeg = data.startswith(b'\xff\xd8\xff')
        is_png = data.startswith(b'\x89PNG\r\n\x1a\n')
        is_webp = data.startswith(b'RIFF') and data[8:12] == b'WEBP'
        assert is_jpeg or is_png or is_webp, 'Not a supported raster image'
        suffix = '.jpg' if is_jpeg else '.png' if is_png else '.webp'
        local = 'covers/' + sha256(url.encode()).hexdigest()[:20] + suffix
        (OUT / local).write_bytes(data)
        result.update(ok=True, status=status, mime=mime, bytes=len(data), sha256=sha256(data).hexdigest(), review_file=local)
    except Exception as error:
        result['error'] = str(error)[:200]
    return result

def page(url, expected_heading=None):
    result = {'url': url, 'ok': False}
    try:
        status, mime, data = get(url)
        text = data.decode('utf-8')
        parsed = Page()
        parsed.feed(text)
        result.update(ok=status == 200, status=status, mime=mime, sha256=sha256(data).hexdigest(), music_layout='class="music-site"' in text, heading=parsed.h1.strip())
        if expected_heading is not None:
            result['heading_matches'] = parsed.h1.strip() == expected_heading
        return result, text
    except Exception as error:
        result['error'] = str(error)[:200]
        return result, ''

def main():
    (OUT / 'covers').mkdir(parents=True, exist_ok=True)
    parsed = Page()
    parsed.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
    urls = sorted({url for url in parsed.images if urlsplit(url).hostname in {'p1.music.126.net', 'p2.music.126.net'}})
    with ThreadPoolExecutor(max_workers=4) as pool:
        covers = list(pool.map(cover, urls))
    candidates = sorted((ROOT / 'daily').glob('20??-??-??/index.html'))
    latest = candidates[-1] if candidates else None
    date = latest.parent.name if latest else None
    heading = None
    if latest:
        song = Page()
        song.feed(latest.read_text(encoding='utf-8'))
        heading = song.h1.strip()
    attempts = []
    rounds = 12 if os.getenv('VERIFY_LIVE') == '1' else 1
    for attempt in range(rounds):
        home, text = page('https://www.werogue.com/')
        daily, _ = page('https://www.werogue.com/daily/' + date + '/', heading) if date else ({}, '')
        published = bool(home.get('ok') and home.get('music_layout') and daily.get('ok') and daily.get('music_layout') and daily.get('heading_matches') and ('/daily/' + date + '/') in text)
        attempts.append({'checked_at': datetime.now(timezone.utc).isoformat(), 'home': home, 'latest_daily': daily, 'new_layout_and_latest_daily_verified': published})
        if published or attempt == rounds - 1:
            break
        time.sleep(10)
    report = {'schema': 1, 'source_sha': os.getenv('GITHUB_SHA'), 'latest_daily_date': date, 'covers': covers, 'attempts': attempts, 'note': 'Read-only checks from GitHub Actions runner. Cover copies are temporary review artifacts. Success here does not verify every geographic network or audio playback.'}
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'covers_ok': sum(c['ok'] for c in covers), 'covers_total': len(covers), 'last_live_check': attempts[-1]}, ensure_ascii=False, indent=2))
    if not attempts[-1]['new_layout_and_latest_daily_verified']:
        print('::warning::New layout/latest daily not verified on the public domain; consult external-review/report.json. Build success is not publication success.')
    if not all(c['ok'] for c in covers):
        print('::warning::One or more artwork links could not be verified. The page retains accessible placeholders.')

if __name__ == '__main__':
    main()
