"""Offline smoke checks for the generated site; does not claim external links work."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re

ROOT = Path('_site')

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        key = 'href' if tag in ('a', 'link') else 'src' if tag in ('img', 'script') else None
        if key and attrs.get(key):
            self.urls.append(attrs[key])

def check():
    required = ['index.html', 'daily/index.html', 'tags.html', 'time_line.html', 'remember_me.html', 'apples.html', '404.html', 'assets/css/music.css', 'assets/js/music-shelf.js', 'feed.xml']
    for file in required:
        assert (ROOT / file).is_file(), f'Missing output: {file}'
    index = (ROOT / 'index.html').read_text(encoding='utf-8')
    posts = list(Path('_posts').glob('*.md')) + list(Path('_posts').glob('*.markdown'))
    daily_dates = []
    legacy_count = 0
    for post in posts:
        text = post.read_text(encoding='utf-8')
        if re.search(r'^kind:\s*[\"\']?daily[\"\']?\s*$', text, re.M):
            match = re.search(r'^permalink:\s*[\"\']?(/daily/(\d{4}-\d{2}-\d{2})/)', text, re.M)
            assert match, f'Missing daily permalink: {post}'
            daily_dates.append(match[2])
            output = ROOT / match[1].lstrip('/') / 'index.html'
            assert output.is_file(), f'Missing daily page: {output}'
        elif not re.search(r'^published:\s*false\s*$', text, re.M):
            legacy_count += 1
    assert len(daily_dates) == len(set(daily_dates)), 'Duplicate daily date'
    assert index.count('data-record data-search=') == legacy_count, 'Daily entries leaked into permanent catalog, or a record is missing'
    assert '一首歌' in index and 'Minimal Mistakes' in index
    for relative in required[:7]:
        page = ROOT / relative
        text = page.read_text(encoding='utf-8')
        assert '{{' not in text and '{%' not in text, f'Unrendered Liquid: {relative}'
        assert 'client_secret' not in text, f'Secret field rendered: {relative}'
        parser = Links()
        parser.feed(text)
        for url in parser.urls:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = unquote(parsed.path)
            target = ROOT / path.lstrip('/') if path.startswith('/') else page.parent / path
            if path.endswith('/') or target.is_dir():
                target = target / 'index.html'
            assert target.is_file(), f'Broken local link in {relative}: {url}'
    print(f'PASS: {legacy_count} permanent records; {len(daily_dates)} daily entries; core pages and local links verified. External images/audio not tested.')

if __name__ == '__main__':
    check()
