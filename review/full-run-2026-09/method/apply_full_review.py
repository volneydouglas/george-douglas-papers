from full_review_helpers import *
import re,collections,copy,shutil
BOOK=ROOT/'book/george-douglas-archival'
pilot=json.loads((OUT.parent/'image-pilot-2026-09/decisions.json').read_text())['records']
new=json.loads((OUT/'adjudications.json').read_text())
decisions={r['item']:r for r in pilot+new}
extra=[
 ('05-024','By %GD[05-024-U001]% Hawkins','[[By?]] %GD[05-024-U001]% Hawkins','The initial F is secure; the preceding abbreviation may be Benj rather than By. Preserve uncertainty instead of silently choosing the full name.'),
 ('05-036','Bardsdale, Sep, 29th, 1893.','Bardsdale, Sat, 29th, 1893.','The manuscript heading has the terminal tall t and no descending p; read Sat literally, as on the separate identifying slip. Do not expand this to a month or reconcile its calendar date.'),
 ('05-157','Per H. E. %GD[05-157-U001]% Deputy.','Per H. C. %GD[05-157-U001]% Deputy.','The deputy signature reads H. C. Wise, with C rather than the earlier E. Compare 04-045.'),
 ('06-063','tale to recount this week','tale to narrate this week','The opening verb shows narrate at native resolution.'),
 ('06-063','was here in the spring','[[was here in the spring?]]','Whole-line inspection does not support this previously confident surrounding phrase. It may instead describe where the family lived; retain the old wording only as tentative.'),
 ('06-116','a literary %GD[06-116-U004]% discourse','a [[literary?]] %GD[06-116-U004]% discourse','The earlier confident literary is not secure; the wider clause may describe the preacher rather than a discourse. Mark the word and flag the whole passage for re-transcription.')
]
annotation_index=[];applied=[];pages_out=[]
for old in B['transcripts']['pages']:
 d=copy.deepcopy(old);seq=0;newseq=max([int(x.split('U')[-1]) for x in ROWS if x.startswith(d['id']+'-')]+[0]);bindings={};blocks=[]
 for block in old['paragraphs']:
  def substitute(m):
   global seq
   a=m.group(1)
   if not ('?' in a or 'illegible' in a or a.startswith(('lost:','obscured:'))):return m.group(0)
   seq+=1;item=f"{d['id']}-U{seq:03}";assert ROWS[item]['annotation']==m.group(0)
   r=decisions.get(item,{});replacement=r.get('replacement')
   # Use placeholders even for resolved words so whole-line edits remain auditable.
   bindings[item]=replacement if replacement is not None else m.group(0)
   if replacement is not None:applied.append({'item':item,'paragraph_id':block['id'],'before':m.group(0),'after':replacement,'evidence_review':'image-pilot-2026-09' if item in {x['item'] for x in pilot} else 'full-run-2026-09'})
   return '%GD['+item+']%'
  text=re.sub(r'\[\[(.*?)\]\]',substitute,block['text'],flags=re.S)
  for page,a,z,why in extra:
   if page==d['id'] and a in text:
    assert text.count(a)==1;text=text.replace(a,z)
    applied.append({'item':None,'paragraph_id':block['id'],'before':a,'after':z,'reason':why,'evidence_review':'full-run-2026-09'})
  def expand(m):
   global newseq
   if m.group(1):
    item=m.group(1);value=bindings[item]
    if re.fullmatch(r'\[\[.*?\]\](?:.*)',value,re.S):
     ann=re.search(r'\[\[.*?\]\]',value,re.S).group(0)
     r=copy.deepcopy(ROWS[item]);r['annotation']=ann;annotation_index.append(r)
    return value
   value=m.group(0);a=value[2:-2]
   if '?' in a or 'illegible' in a or a.startswith(('lost:','obscured:')):
    newseq+=1;item=f"{d['id']}-U{newseq:03}"
    annotation_index.append({'item':item,'page_id':d['id'],'paragraph_id':block['id'],'annotation':value,'proposed_correction':'','reviewer_and_date':'2026-09-20 AI-assisted image review','evidence':'New uncertainty recorded during whole-line review; see full-run-2026-09/applied-changes.json.'})
   return value
  text=re.sub(r'%GD\[([^]]+)\]%|\[\[.*?\]\]',expand,text,flags=re.S)
  blocks.append(text)
 d['text']='\n\n'.join(blocks)
 notes=[]
 for item,r in decisions.items():
  if r.get('page_id')!=d['id']:continue
  if r['outcome']=='duplicate_witness':
   notes.append(r.get('witness_note') or (r['paragraph_id']+': '+r['reading']+'. '+r['reason']))
  elif r['outcome']=='partial_reading':notes.append(r['paragraph_id']+': Guthrie is legible; the notary given name remains unread.')
 if d['id']=='04-054':d['editorial_notes']='Additional closing page. Image review supports Gunter as the destination.'
 if d['id']=='05-024':d['editorial_notes']='The initial before Hawkins reads F. The preceding abbreviation is uncertain and may be Benj; it is not silently expanded.'
 if d['id']=='05-036':notes.append('The heading reads Sat literally. The earlier Sep and its expansion to September have been withdrawn; the month is not established by this heading.')
 if d['id']=='06-008':notes.append('The docket reads volume 91; the separate recording certificate on 06-011 reads 92. Both readings are preserved.')
 if d['id']=='06-063':notes.append('Whole-line review also questions previously unbracketed wording around the first location clause. The remaining narrative requires further image or human review; this revision does not certify all surrounding words.')
 if d['id']=='06-116':notes.append('Whole-line inspection raises doubts about the surrounding sentence framework in P02, including the earlier literary discourse wording. P02 and P03 remain provisional as whole passages; the marked gaps are not the only potential errors.')
 if notes:d['editorial_notes']+=' Image review September 2026. '+' '.join(notes)
 if any(r.get('page_id')==d['id'] for r in decisions.values()):d['review']='selected_passages_image_adjudicated_2026_09'
 if d['text']!=old['text'] or d['editorial_notes']!=old['editorial_notes'] or d['review']!=old['review']:
  d.pop('paragraphs',None)
  (BOOK/'pages'/(d['id']+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 pages_out.append(d)
assert sum(x.get('item') is None for x in applied)==len(extra),(extra,applied)
(BOOK/'uncertainty-index.json').write_text(json.dumps(annotation_index,ensure_ascii=False,indent=2)+'\n')
(OUT/'applied-changes.json').write_text(json.dumps(applied,ensure_ascii=False,indent=2)+'\n')
triage={r['item']:r for r in json.loads((OUT/'machine-triage.json').read_text())};assert len(triage)==1200
ledger=[]
for item,r in ROWS.items():
 decision=decisions.get(item)
 ledger.append({'item':item,'page_id':r['page_id'],'paragraph_id':r['paragraph_id'],'machine_processing':'complete','ocr_runs_for_page':triage[item]['runs'],'image_adjudicated':decision is not None,'outcome':decision['outcome'] if decision else 'retained_without_new_image_adjudication','replacement':decision.get('replacement') if decision else None,'review_record':('image-pilot-2026-09/decisions.json' if item in {x['item'] for x in pilot} else 'full-run-2026-09/adjudications.json') if decision else None})
(OUT/'item-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
summary={'baseline_items':1200,'source_pages_processed':193,'ocr_runs':1351,'ocr_errors':sum(r['errors'] for r in triage.values()),'image_adjudicated_items_including_pilot':sum(x['image_adjudicated'] for x in ledger),'outcomes':dict(collections.Counter(x['outcome'] for x in ledger)),'annotation_replacements':sum(x['item'] is not None for x in applied),'additional_whole_line_changes':len(extra),'current_uncertainties':len(annotation_index),'unresolved_IDs':'Original IDs retained; newly introduced uncertainties use numbers above the old maximum on their page. Resolved IDs are retired, not reassigned.'}
# Count errors by unique page, not by number of items on that page.
summary['ocr_errors']=sum('error' in r for f in (OUT/'ocr').glob('*.json') for r in json.loads(f.read_text())['records'])
assert summary['ocr_errors']==0
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
