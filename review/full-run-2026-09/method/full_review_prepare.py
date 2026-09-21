from pathlib import Path
import json,csv,hashlib,collections
from pypdf import PdfReader
from PIL import Image,ImageOps
ROOT=Path('/Users/volneydouglas/Documents/FamilyHistory')
REPO=ROOT/'repositories/george-douglas-papers'
OUT=REPO/'review/full-run-2026-09'
TMP=ROOT/'tmp/george_douglas/full-run'
SRC=Path('/Users/volneydouglas/Library/Mobile Documents/com~apple~CloudDocs/George Douglas')
OUT.mkdir(exist_ok=True);TMP.mkdir(exist_ok=True)
baseline=OUT/'baseline.json'
if not baseline.exists():
 rows=list(csv.DictReader((REPO/'editions/annotated/Supporting-files/Unresolved-readings.tsv').open(),delimiter='\t'))
 master=json.loads((REPO/'editions/annotated/Supporting-files/Transcripts.json').read_text())
 baseline.write_text(json.dumps({'commit':'ef7651971ca60e27cf1d18695ab3d376311c4a64','items':rows,'transcripts':master},ensure_ascii=False,indent=2)+'\n')
b=json.loads(baseline.read_text());rows=b['items'];sources=b['transcripts']['sources']
manifest=[];paths=[]
for s in sources:
 selected=sorted({r['page_id'] for r in rows if r['page_id'].startswith(s['id']+'-')})
 if not selected:continue
 src=SRC/s['filename'];assert hashlib.sha256(src.read_bytes()).hexdigest()==s['sha256']
 reader=PdfReader(src)
 for key in selected:
  page=reader.pages[int(key[3:])-1]
  substantive=[x for x in page.images if x.image.width>1 and x.image.height>1];assert len(substantive)==1,key
  embedded=substantive[0]
  im=embedded.image.convert('RGB'); original=TMP/(key+'-original.png');contrast=TMP/(key+'-contrast.png')
  if not original.exists():im.save(original)
  if not contrast.exists():ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=1).save(contrast)
  paths.append(str(original))
  manifest.append({'page_id':key,'source_filename':s['filename'],'source_sha256':s['sha256'],'native_size':list(im.size),'embedded_image':embedded.name,'ignored_one_pixel_objects':[x.name for x in page.images if x.image.width==1 or x.image.height==1],'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'contrast_sha256':hashlib.sha256(contrast.read_bytes()).hexdigest(),'processing':'Native embedded image to RGB; contrast variant grayscale with 1% autocontrast per tail. No generated strokes.','items':[r['item'] for r in rows if r['page_id']==key]})
(OUT/'image-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(TMP/'inputs.txt').write_text('\n'.join(paths)+'\n')
print(json.dumps({'pages':len(manifest),'items':len(rows),'categories':dict(collections.Counter(r['category'] for r in rows))}))
