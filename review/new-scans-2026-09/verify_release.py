"""Validate the version 2.0 release with Python 3 and Git; no third-party packages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUP = ROOT / 'editions/annotated/Supporting-files'
BASE = '05cf272634247db7f2b54c7b5e1cd3e13a5b0a07'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def old_bytes(path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{BASE}:{path}'])


def digest(data):
    return hashlib.sha256(data).hexdigest()


class HTML(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids, self.hrefs, self.articles, self.register_rows = {}, [], [], []
        self.active = []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, attrs['id']
            self.ids[attrs['id']] = []
        if 'href' in attrs:
            self.hrefs.append(attrs['href'])
        node = {'tag': tag, 'id': attrs.get('id'), 'text': []}
        if tag == 'article':
            self.articles.append(node['text'])
        if tag == 'tr' and any(n['tag'] == 'tbody' for n in self.active):
            self.register_rows.append(node['text'])
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.active.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.active) - 1, -1, -1):
            if self.active[i]['tag'] == tag:
                del self.active[i:]
                break

    def handle_data(self, text):
        for node in self.active:
            node['text'].append(text)
            if node['id']:
                self.ids[node['id']].append(text)


def verify():
    master = read_json(SUP / 'Transcripts.json')
    sources, pages = master['sources'], master['pages']
    assert len(sources) == 10 and sum(s['pages'] for s in sources) == 932
    assert master['version'] == '2.0' and master['scope_scan_pages'] == 932
    assert len(pages) == 932
    expected = [f"{s['id']}-{p:03}" for s in sources for p in range(1, s['pages'] + 1)]
    assert [p['id'] for p in pages] == expected
    paragraphs = {b['id']: b['text'] for p in pages for b in p['paragraphs']}
    assert len(paragraphs) == sum(len(p['paragraphs']) for p in pages) == 2183
    for page in pages:
        assert [b['id'] for b in page['paragraphs']] == [f"{page['id']}-P{n:02}" for n in range(1, len(page['paragraphs']) + 1)]
    assert read_json(SUP / 'Source-manifest.json') == sources

    old = json.loads(old_bytes('editions/annotated/Supporting-files/Transcripts.json'))
    assert pages[:387] == old['pages'] and sources[:6] == old['sources']
    register = rows(SUP / 'Unresolved-readings.tsv')
    old_register = list(csv.DictReader(io.StringIO(old_bytes('editions/annotated/Supporting-files/Unresolved-readings.tsv').decode()), delimiter='\t'))
    assert len(register) == 3415 and register[:1175] == old_register
    assert len({r['item'] for r in register}) == 3415
    for row in register:
        assert row['paragraph_id'] in paragraphs
        assert row['annotation'] in paragraphs[row['paragraph_id']], row['item']
        assert row['paragraph_id'].startswith(row['page_id'] + '-')

    reader = HTML((SUP / 'Complete-transcript.html').read_text())
    register_html = HTML((SUP / 'Unresolved-readings.html').read_text())
    assert len(reader.articles) == 932 and len(register_html.register_rows) == 3415
    plain = (SUP / 'Complete-transcript.txt').read_text()
    for pid, text in paragraphs.items():
        assert ''.join(reader.ids[pid]) == pid + ' ' + text, pid
        assert text in plain, pid
    for href in register_html.hrefs:
        if href.startswith('Complete-transcript.html#'):
            assert href.split('#')[1] in reader.ids
    for filename in ('Page-inventory.tsv', 'PDF-page-map.tsv'):
        assert [r['page_id'] for r in rows(SUP / filename)] == expected

    audit = read_json(HERE / 'export-audit.json')
    assert audit['pdf_paragraph_mismatches'] == 0 and audit['visually_inspected_new_pdf_pages'] == 584
    visual = read_json(HERE / 'visual-review.json')
    assert len(visual) == 584
    for record in visual.values():
        assert re.fullmatch(r'[0-9a-f]{64}', record['sha256'])
        assert record['status'] == 'visually inspected; clean'
    expected_visual = {f"{v['kind']}-{v['source']}/page-{n}.png" for v in audit['volumes'] for n in range(1, v['pdf_pages'] + 1)}
    assert set(visual) == expected_visual

    family = ROOT / 'editions/family'
    ledger = read_json(family / 'Source-ledger.json')
    old_ledger = json.loads(old_bytes('editions/family/Source-ledger.json'))
    assert ledger['entries'][:161] == old_ledger['entries'] and len(ledger['entries']) == 706
    assert ledger['source_page_count'] == 932
    coverage = []
    for entry in ledger['entries']:
        coverage.extend(f"{entry['source']}-{n:03}" for n in range(entry['start'], entry['end'] + 1))
    assert sorted(coverage) == expected
    for entry in ledger['entries'][161:]:
        assert f'<a id="{entry["anchor"]}"></a>' in (family / entry['file']).read_text()
    new_family = read_json(family / 'New-source-readings.json')
    assert new_family['pages'] == pages[387:] and new_family['sources'] == sources[6:]
    assert [r['page_id'] for r in rows(family / 'New-PDF-page-map.tsv')] == expected[387:]
    for page in pages[387:]:
        entry = ledger['entries'][161 + pages[387:].index(page)]
        assert page['family_text'] in (family / entry['file']).read_text(), page['id']

    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    stems = {'07': '05-Folder-4', '08': '06-Daybook', '09': '07-Folder-6', '10': '08-Poems-and-Other-Writings'}
    roman = {'07': 'V', '08': 'VI', '09': 'VII', '10': 'VIII'}
    for kind in ('annotated', 'family'):
        for sid in stems:
            stem = f'George-Douglas-Annotated-Transcription-Volume-{roman[sid]}' if kind == 'annotated' else stems[sid]
            path = ROOT / f'editions/{kind}/{stem}.docx'
            with zipfile.ZipFile(path) as z:
                tree = ET.fromstring(z.read('word/document.xml'))
            texts = [''.join(n.text or '' if n.tag.endswith('}t') else '\n' if n.tag.endswith('}br') else '\t' for n in para.iter() if n.tag in {f'{{{ns["w"]}}}{tag}' for tag in ('t', 'br', 'tab')}) for para in tree.findall('.//w:body/w:p', ns)]
            # Word line breaks remain explicit; paragraph separators are separate nodes.
            for page in (p for p in pages if p['source'] == sid):
                wanted = [b['id'] + '   ' + b['text'] for b in page['paragraphs']] if kind == 'annotated' else page['family_text'].split('\n\n')
                for text in wanted:
                    assert text in texts, (path.name, page['id'])

    preserved = read_json(HERE / 'preserved-files.json')
    assert preserved['baseline_commit'] == BASE and len(preserved['files']) == 398
    for filename, sha in preserved['files'].items():
        assert digest((ROOT / filename).read_bytes()) == sha, filename
        assert digest(old_bytes(filename)) == sha, filename

    packages = {}
    for kind, stem in [('annotated', 'George-Douglas-University-Transcription-Edition'), ('family', 'George-Douglas-Independent-Family-Edition')]:
        base = ROOT / 'editions' / kind
        names = {str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}
        assert set((base / 'manifest.txt').read_text().splitlines()) == names
        checksums = {}
        for line in (base / 'SHA256SUMS.txt').read_text().splitlines():
            sha, name = line.split('  ', 1)
            assert digest((base / name).read_bytes()) == sha, name
            checksums[name] = sha
        assert set(checksums) == names - {'SHA256SUMS.txt'}
        assert len(list(base.glob('*.docx'))) == len(list(base.glob('*.pdf'))) == 8
        archive = ROOT / 'downloads' / (stem + '.zip')
        with zipfile.ZipFile(archive) as z:
            assert not z.testzip()
            assert set(z.namelist()) == {stem + '/' + name for name in names}
            for name in names:
                assert z.read(stem + '/' + name) == (base / name).read_bytes(), name
        packages[archive.name] = {'sha256': digest(archive.read_bytes()), 'files': len(names), 'bytes': archive.stat().st_size}

    # Check only current release navigation; previous review prose is preserved.
    link_files = [ROOT / name for name in ('README.md', 'SOURCES.md', 'RIGHTS.md', 'REVIEW-STATUS.md')]
    link_files += [HERE / 'README.md'] + [ROOT / f'editions/{kind}/README.md' for kind in ('annotated', 'family')]
    for path in link_files:
        for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if urlsplit(href).scheme or href.startswith('#'):
                continue
            target = (path.parent / unquote(href.split('#')[0])).resolve()
            assert target.exists(), (str(path.relative_to(ROOT)), href)

    result = {'date': '2026-09-26', 'status': 'passed', 'source_scan_pages': 932, 'new_source_scan_pages': 545, 'annotated_blocks': 2183, 'uncertainty_entries': 3415, 'family_entries': 706, 'preserved_prior_files': 398, 'new_visual_review_records': 584, 'all_old_page_objects_and_uncertainty_rows_unchanged': True, 'new_docx_body_matches_master': True, 'html_and_plain_text_match_master': True, 'page_inventory_and_maps_complete': True, 'new_family_markdown_matches_master': True, 'current_relative_links_valid': True, 'packages': packages, 'limits': 'These checks verify release consistency; they do not repeat handwriting interpretation, PDF extraction checks or visual review.'}
    return result


if __name__ == '__main__':
    result = verify()
    if '--write-report' in sys.argv:
        (HERE / 'release-validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
