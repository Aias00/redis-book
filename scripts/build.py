"""Build the online edition and EPUB from the same ordered manuscript."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = sorted((ROOT / 'manuscript').glob('*.md'))
BUILD = ROOT / '.build'
BUILD.mkdir(exist_ok=True)
BOOK = BUILD / 'book.md'
BOOK.write_text('\n\n'.join(p.read_text(encoding='utf-8').rstrip() for p in CHAPTERS) + '\n', encoding='utf-8')
common = ['pandoc', str(BOOK), '--from=markdown', '--metadata-file=' + str(ROOT / 'metadata.yaml'), '--toc', '--toc-depth=2', '--fail-if-warnings', '--data-dir=' + str(ROOT / 'assets/pandoc')]
subprocess.run(common + ['--to=epub3', '--split-level=1', '--epub-cover-image=' + str(ROOT / 'assets/cover.svg'), '--css=' + str(ROOT / 'assets/epub.css'), '--output=' + str(ROOT / 'downloads/redis-learning-handbook.epub')], check=True, cwd=ROOT)
subprocess.run(common + ['--to=html5', '--standalone', '--section-divs', '--template=' + str(ROOT / 'assets/reader.html'), '--output=' + str(ROOT / 'docs/index.html')], check=True, cwd=ROOT)
for name in ['reader.css', 'reader.js', 'cover.svg']:
    shutil.copyfile(ROOT / 'assets' / name, ROOT / 'docs' / name)
(ROOT / 'docs/downloads').mkdir(exist_ok=True)
shutil.copyfile(ROOT / 'downloads/redis-learning-handbook.epub', ROOT / 'docs/downloads/redis-learning-handbook.epub')
(ROOT / 'docs/.nojekyll').touch()
print(f'Built {len(CHAPTERS)} sections; {len(BOOK.read_text(encoding="utf-8")):,} characters')

sources = CHAPTERS + sorted((ROOT / 'assets').rglob('*')) + [ROOT / 'metadata.yaml', ROOT / 'scripts/build.py']
manifest = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources if path.is_file()}
(ROOT / 'docs/source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
