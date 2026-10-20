"""Check source coverage, EPUB navigation/XML and published local links."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import hashlib
import json
import posixpath

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'duplicate id {attrs["id"]}'
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.h1_count += 1
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])


manifest = json.loads((ROOT / 'docs/source-manifest.json').read_text())
expected = sorted((ROOT / 'manuscript').glob('*.md')) + [p for p in (ROOT / 'assets').rglob('*') if p.is_file()] + [ROOT / 'metadata.yaml', ROOT / 'scripts/build.py']
assert set(manifest) == {str(p.relative_to(ROOT)) for p in expected}, 'source manifest file list changed; rebuild'
for name, digest in manifest.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f'{name} changed; run scripts/build.py'
page = Page()
page.feed((ROOT / 'docs/index.html').read_text())
assert page.h1_count == 23, page.h1_count
for link in page.links:
    url = urlsplit(link)
    if url.scheme or url.netloc:
        continue
    if url.path:
        assert (ROOT / 'docs' / unquote(url.path)).is_file(), link
    elif url.fragment:
        assert unquote(url.fragment) in page.ids, link
chapters = sorted((ROOT / 'manuscript').glob('*.md'))
assert len(chapters) == 22
web = (ROOT / 'docs/index.html').read_text()
for chapter in chapters:
    title = chapter.read_text().splitlines()[0].removeprefix('# ')
    assert title in web, title
book = ROOT / 'downloads/redis-learning-handbook.epub'
assert book.read_bytes() == (ROOT / 'docs/downloads' / book.name).read_bytes()
with ZipFile(book) as archive:
    names = set(archive.namelist())
    first = archive.infolist()[0]
    assert first.filename == 'mimetype' and first.compress_type == 0
    assert archive.read('mimetype') == b'application/epub+zip'
    for name in names:
        if name.endswith(('.xml', '.opf', '.xhtml', '.ncx', '.svg')):
            xml = ET.fromstring(archive.read(name))
            for node in xml.iter():
                for attr in ('href', 'src'):
                    if attr not in node.attrib:
                        continue
                    link = urlsplit(node.attrib[attr])
                    if link.scheme or link.netloc or not link.path:
                        continue
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(link.path)))
                    assert target in names, (name, target)
    opf_name = next(name for name in names if name.endswith('.opf'))
    opf = ET.fromstring(archive.read(opf_name))
    ns = {'opf': 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/'}
    assert opf.find('.//dc:language', ns).text == 'zh-CN'
    assert len(opf.findall('.//opf:spine/opf:itemref', ns)) >= 22
print(f'PASS: {len(chapters)} sources, {page.h1_count} headings, local links, EPUB XML/spine/resources')
print('EPUB SHA256:', hashlib.sha256(book.read_bytes()).hexdigest())
