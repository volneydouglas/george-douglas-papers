"""Read-only audit; Python 3 standard library and git. Run from any directory."""
from pathlib import Path
import collections, csv, hashlib, json, re, zipfile
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
def read(name):return json.loads((HERE/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=read('baseline.json');ledger=read('item-ledger.json');manifest=read('image-manifest.json');summary=read('summary.json')
assert len(baseline['items'])==len(ledger)==1200
assert {r['item'] for r in ledger}=={r['item'] for r in baseline['items']}
assert len(manifest)==len({r['page_id'] for r in manifest})==193
assert {i for p in manifest for i in p['items']}=={r['item'] for r in ledger}
assert all(r['machine_processing']=='complete' and r['ocr_runs_for_page']==7 for r in ledger)
assert sum(r['image_adjudicated'] for r in ledger)==81
assert dict(collections.Counter(r['outcome'] for r in ledger))==summary['outcomes']
runs=0
for p in manifest:
 result=read('ocr/'+p['page_id']+'.json');assert result['page_id']==p['page_id'];assert len(result['records'])==7
 assert all(not r.get('error') for r in result['records']);runs+=len(result['records'])
assert runs==1351
new=read('adjudications.json');assert len(new)==31
for r in new:
 assert sha(HERE/r['evidence']['image'])==r['evidence']['sha256']
 assert not r['human_verified']
for r in read('support-image-provenance.json'):assert sha(HERE/r['image'])==r['sha256']
for r in ledger:
 if r['review_record']:assert (HERE.parent/r['review_record']).is_file()
current=json.loads((REPO/'editions/annotated/Supporting-files/Transcripts.json').read_text())
old={p['id']:p for p in baseline['transcripts']['pages']};changes=read('page-changes.json')
for change in changes:
 assert old[change['page_id']]==change['before'];old[change['page_id']]=change['after']
assert list(old.values())==current['pages']
assert len(current['pages'])==387
assert current['sources']==baseline['transcripts']['sources']
blocks={b['id']:b['text'] for p in current['pages'] for b in p['paragraphs']};assert len(blocks)==971
assert all('%GD[' not in t for t in blocks.values())
register=list(csv.DictReader((REPO/'editions/annotated/Supporting-files/Unresolved-readings.tsv').open(),delimiter='\t'))
assert len(register)==len({r['item'] for r in register})==1175
assert sum(r['item'] is None for r in read('applied-changes.json'))==6
assert len(read('applied-changes.json'))==36
assert len(read('family-changes.json'))==11
# Validate every edited paragraph by replaying the declared exact changes.
oldblocks={b['id']:b['text'] for p in baseline['transcripts']['pages'] for b in p['paragraphs']}
for edit in read('applied-changes.json'):
 text=oldblocks[edit['paragraph_id']]
 assert edit['before'] in text,(edit['paragraph_id'],edit['before'])
 oldblocks[edit['paragraph_id']]=text.replace(edit['before'],edit['after'],1)
assert oldblocks==blocks
for change in read('editorial-note-changes.json'):
 now=next(p for p in current['pages'] if p['id']==change['page_id'])
 assert now['editorial_notes']==change['after']
# Reapply family edits to the recorded pre-revision files from git history.
import subprocess
for filename in {e['file'] for e in read('family-changes.json')}:
 path='editions/family/Plain-text/'+filename
 text=subprocess.check_output(['git','show',baseline['commit']+':'+path],cwd=REPO).decode()
 for edit in read('family-changes.json'):
  if edit['file']==filename:
   assert edit['before'] in text; text=text.replace(edit['before'],edit['after'],1)
 assert text==(REPO/path).read_text(),filename
# Hashes and archives; checksums deliberately exclude the checksum file itself.
for folder in [HERE,REPO/'editions/annotated',REPO/'editions/family']:
 checksum=folder/'SHA256SUMS.txt'
 for line in checksum.read_text().splitlines():
  digest,name=line.split('  ',1);assert sha(folder/name)==digest,name
for name in ['George-Douglas-University-Transcription-Edition','George-Douglas-Independent-Family-Edition']:
 with zipfile.ZipFile(REPO/'downloads'/(name+'.zip')) as z:
  assert z.testzip() is None
  checks=[n for n in z.namelist() if n.endswith('/SHA256SUMS.txt')];assert len(checks)==1
  root=checks[0].rsplit('/',1)[0]+'/'
  for line in z.read(checks[0]).decode().splitlines():
   digest,p=line.split('  ',1);assert hashlib.sha256(z.read(root+p)).hexdigest()==digest,p
print(json.dumps({'original_items':1200,'ocr_pages':193,'ocr_runs':runs,'focused_image_decisions':81,'remaining_uncertainties':1175,'source_pages':387,'transcript_blocks':971,'exact_changes_and_package_checksums':'passed'},indent=2))
