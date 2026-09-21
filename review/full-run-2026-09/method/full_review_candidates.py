from full_review_helpers import *
import re,collections
def tokens(s):return re.findall(r"[a-z0-9]+(?:'[a-z]+)?",s.lower().replace('’',"'"))
pages={p['id']:p for p in B['transcripts']['pages']}
locs={}
for p in pages.values():
 seq=0
 for block in p['paragraphs']:
  for m in re.finditer(r'\[\[(.*?)\]\]',block['text'],re.S):
   a=m.group(1)
   if not ('?' in a or 'illegible' in a or a.startswith(('lost:','obscured:'))):continue
   seq+=1;locs[f"{p['id']}-U{seq:03}"]=(block['text'],m.start(),m.end())
report=[]
for item,r in ROWS.items():
 f=OUT/'ocr'/(r['page_id']+'.json')
 if not f.exists():continue
 d=json.loads(f.read_text());para,start,end=locs[item]
 left=tokens(re.split(r'\]\]',para[:start])[-1])[-2:]
 right=tokens(re.split(r'\[\[',para[end:])[0])[:2]
 target=tokens(r['annotation'][2:-2].rstrip('?')) if r['category']=='tentative reading' else []
 hits=[];fills=[]
 for n,run in enumerate(d['records']):
  recognized=' '.join(x['candidates'][0]['text'] for x in run.get('lines',[]) if x['candidates'])
  w=tokens(recognized);joined=' '+' '.join(w)+' '
  if target and ' '+' '.join(target)+' ' in joined:hits.append(n)
  if len(left)==2 and len(right)==2:
   for i in range(len(w)-len(left)):
    if w[i:i+2]!=left:continue
    for j in range(i+2,min(i+12,len(w)-1)):
     if w[j:j+2]==right and j>i+2:
      fills.append({'run':n,'reading':' '.join(w[i+2:j]),'left':' '.join(left),'right':' '.join(right)})
 report.append({'item':item,'page_id':r['page_id'],'annotation':r['annotation'],'runs':len(d['records']),'errors':sum('error' in x for x in d['records']),'literal_word_hits':hits,'anchor_candidates':fills,'status':'Machine triage only; no authority to remove uncertainty'})
(OUT/'machine-triage.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
pilot={r['item'] for r in json.loads((OUT.parent/'image-pilot-2026-09/decisions.json').read_text())['records']}
adjudicated={r['item'] for r in json.loads((OUT/'adjudications.json').read_text())}
for r in report:
 if r['item'] in pilot|adjudicated:continue
 counts=collections.Counter(x['reading'] for x in r['anchor_candidates'])
 if len(r['literal_word_hits'])>=3 or any(n>=2 for n in counts.values()):
  print(r['item'],r['annotation'],'hits',len(r['literal_word_hits']),'anchor',dict(counts))
print('PROCESSED',len(report),'items on',len({r['page_id'] for r in report}),'pages')
