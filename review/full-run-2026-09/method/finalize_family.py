from pathlib import Path
import json,collections,zipfile,shutil,hashlib,re,unicodedata
from PIL import Image,ImageChops
from pypdf import PdfReader
from lxml import etree
BASE=Path('/Users/volneydouglas/Documents/FamilyHistory')
OUT=BASE/'output/george-douglas-independent';QA=BASE/'tmp/george_douglas/qa3';FIX=BASE/'tmp/george_douglas/revision'
expected={'01-Guide-and-Church-Papers':10,'02-Folder-1':31,'03-Folder-2':48,'04-Folder-3':38}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u00ad',''))
ledger=json.loads((OUT/'Source-ledger.json').read_text())
for source,count in [('01',6),('02',4),('03',5),('04',96),('05',158),('06',118)]:
 coverage=collections.Counter(n for e in ledger['entries'] if e['source']==source for n in range(e['start'],e['end']+1))
 assert coverage==collections.Counter(range(1,count+1)),source
report={'source_pages':387,'entries':len(ledger['entries']),'source_coverage':'Each page accounted for exactly once','volumes':[]}
for stem,n in expected.items():
 pdf=FIX/'family-fixed'/(stem+'.pdf');r=PdfReader(pdf);assert len(r.pages)==n
 with zipfile.ZipFile(OUT/(stem+'.docx')) as z:root=etree.fromstring(z.read('word/document.xml'))
 paras=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in root.xpath('.//w:body//w:p',namespaces=ns)]
 combined='\n'.join(p.extract_text() or '' for p in r.pages)
 combined=re.sub(r'GEORGE DOUGLAS PAPERS\s*·\s*VOLUME [IVX]+','',combined)
 combined=re.sub(r'Independent reading edition\s*•\s*\d+','',combined)
 compact=norm(combined)
 missing=[p for p in paras if p and norm(p) not in compact]
 if missing:
  print('Using alternate PDF extractor for',stem,len(missing),'paragraphs')
  import pdfplumber
  with pdfplumber.open(pdf) as alt: alternate='\n'.join(p.extract_text() or '' for p in alt.pages)
  alternate=re.sub(r'GEORGE DOUGLAS PAPERS\s*·\s*VOLUME [IVX]+','',alternate)
  alternate=re.sub(r'Independent reading edition\s*•\s*\d+','',alternate)
  assert all(norm(p) in norm(alternate) for p in missing),(stem,'PDF text differs')
 starts=set(root.xpath('.//w:bookmarkStart/@w:name',namespaces=ns));links=root.xpath('.//w:hyperlink/@w:anchor',namespaces=ns)
 assert all(a in starts for a in links)
 ids={p.indirect_reference.idnum for p in r.pages};pdf_links=0
 for p in r.pages:
  assert len(p.extract_text() or '')>80
  for ref in p.get('/Annots',[]):
   a=ref.get_object()
   if a.get('/Subtype')=='/Link':
    dest=a.get('/Dest');assert dest and dest[0].idnum in ids;pdf_links+=1
 def outline_nodes(nodes):
  for item in nodes:
   if isinstance(item,list):yield from outline_nodes(item)
   else:yield item
 bookmarks=list(outline_nodes(r.outline))
 assert len(bookmarks)>=len(links)
 for node in bookmarks:assert 0<=r.get_destination_page_number(node)<n
 shutil.copy2(pdf,OUT/pdf.name)
 report['volumes'].append({'file':pdf.name,'pages':n,'visual_review':'See visual-review.json: changed pages inspected; unchanged bodies compared with previously inspected edition','pdf_paragraphs_match_docx':True,'word_contents_links':len(links),'pdf_link_annotations':pdf_links,'pdf_bookmarks':len(bookmarks),'broken_links':0,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()})
plaintext=OUT/'Plain-text';plaintext.mkdir(exist_ok=True)
for src in sorted((BASE/'book/george-douglas-independent').glob('[0-9][0-9]-*.md')):shutil.copy2(src,plaintext/src.name)
readme=OUT/'Read-me-first.txt';text=readme.read_text();extra='The Plain-text folder contains the same readings as Markdown text, organized by source file, for comparison and searching.\n\n'
if extra not in text:text=text.replace('Prepared for Volney Douglas',extra+'Prepared for Volney Douglas');readme.write_text(text)
report['total_reading_pages']=sum(expected.values())
(FIX/'family-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
