from pathlib import Path
import json,hashlib
from PIL import Image,ImageOps
ROOT=Path('/Users/volneydouglas/Documents/FamilyHistory')
OUT=ROOT/'repositories/george-douglas-papers/review/full-run-2026-09'
TMP=ROOT/'tmp/george_douglas/full-run'
B=json.loads((OUT/'baseline.json').read_text())
ROWS={r['item']:r for r in B['items']}
def record(item,reading,reason,rotation=0,box=None,outcome=None,witness=None):
 path=OUT/'adjudications.json'
 records=json.loads(path.read_text()) if path.exists() else []
 assert item in ROWS
 page=ROWS[item]['page_id'];im=Image.open(TMP/(page+'-original.png')).rotate(rotation,expand=True)
 if box is None:box=[0,0,im.width,im.height]
 region=im.crop(box);target=OUT/'evidence';target.mkdir(exist_ok=True)
 key=item;filename=key+'.png';region.save(target/filename)
 entry={'item':item,'page_id':page,'paragraph_id':ROWS[item]['paragraph_id'],'before':ROWS[item]['annotation'],'replacement':reading,'outcome':outcome or ('image_supported' if reading is not None else 'unresolved'),'reason':reason,'date':'2026-09-20','reviewer':'Codex AI-assisted image review','human_verified':False,'evidence':{'image':'evidence/'+filename,'rotation_counterclockwise':rotation,'box_after_rotation':box,'sha256':hashlib.sha256((target/filename).read_bytes()).hexdigest()}}
 if witness:entry['witness_note']=witness
 records=[r for r in records if r['item']!=item]+[entry]
 path.write_text(json.dumps(sorted(records,key=lambda r:r['item']),indent=2,ensure_ascii=False)+'\n')
def preview(key,rotation=0):
 im=Image.open(TMP/(key+'-original.png')).rotate(rotation,expand=True)
 im.thumbnail((1450,1900));im.save(TMP/(key+'-view.png'))
