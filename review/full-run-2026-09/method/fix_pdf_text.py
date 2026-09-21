from pathlib import Path
import re,json,unicodedata,zipfile
from lxml import etree
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,DecodedStreamObject
BASE=Path('/Users/volneydouglas/Documents/FamilyHistory')
QA=BASE/'tmp/george_douglas/revision'; FIX=QA/'family-fixed';FIX.mkdir(exist_ok=True)
OUT=BASE/'output/george-douglas-independent'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u00ad',''))
allfixes={}
for pdf in sorted(QA.glob('family-*/*.pdf')):
 if pdf.parent.name=='family-fixed':continue
 r=PdfReader(pdf);w=PdfWriter(clone_from=r);seen=set();fixes=[]
 for p in w.pages:
  for key,ref in p['/Resources']['/Font'].items():
   if ref.idnum in seen:continue
   seen.add(ref.idnum);f=ref.get_object()
   if 'Libertine' not in f['/BaseFont']:continue
   s=f['/ToUnicode'].get_data().decode()
   def correction(m):
    code,utf=m.groups()
    if len(utf)<=4:return m.group(0)
    value=bytes.fromhex(utf).decode('utf-16-be')
    assert value[:-1] in ['Th','tt','ff','fi','ft','ffi','fl','ffl','Qu'],(pdf,key,value)
    fixes.append([key,code,value,value[:-1]])
    return f'<{code}> <{value[:-1].encode("utf-16-be").hex().upper()}>'
   s=re.sub(r'^<([A-F0-9]{2})> <([A-F0-9]+)>$',correction,s,flags=re.M)
   if pdf.stem=='01-Guide-and-Church-Papers' and key=='/F11':
    assert '<03>' not in s
    s=re.sub(r'(\d+) beginbfchar',lambda m:f'{int(m.group(1))+1} beginbfchar',s,count=1)
    s=s.replace('endbfchar','<03> <0069>\nendbfchar');fixes.append([key,'03','unmapped','i'])
   if (pdf.stem,key) in [('01-Guide-and-Church-Papers','/F4'),('02-Folder-1','/F4')]:
    code,utf=('49','0036') if pdf.stem.startswith('01') else ('58','0035')
    assert f'<{code}> <{utf}>' in s
    s=s.replace(f'<{code}> <{utf}>',f'<{code}> <>');fixes.append([key,code,'duplicate layout glyph',''])
   if pdf.stem=='03-Folder-2' and key=='/F4':
    assert '<57>' not in s
    s=re.sub(r'(\d+) beginbfchar',lambda m:f'{int(m.group(1))+1} beginbfchar',s,count=1)
    s=s.replace('endbfchar','<57> <002E002E002E>\nendbfchar');fixes.append([key,'57','unmapped','...'])
   obj=DecodedStreamObject();obj.set_data(s.encode());f[NameObject('/ToUnicode')]=w._add_object(obj)
 allfixes[pdf.name]=fixes
 dest=FIX/pdf.name
 with dest.open('wb') as handle:w.write(handle)
 fixed=PdfReader(dest);combined='\n'.join(p.extract_text() or '' for p in fixed.pages)
 combined=re.sub(r'GEORGE DOUGLAS PAPERS\s*·\s*VOLUME [IVX]+','',combined)
 combined=re.sub(r'Independent reading edition\s*•\s*\d+','',combined)
 compact=norm(combined)
 with zipfile.ZipFile(OUT/(pdf.stem+'.docx')) as z:root=etree.fromstring(z.read('word/document.xml'))
 paras=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in root.xpath('.//w:body//w:p',namespaces=ns)]
 missing=[p for p in paras if p and norm(p) not in compact]
 (FIX/(pdf.stem+'.txt')).write_text(combined)
 (FIX/(pdf.stem+'-missing.json')).write_text(json.dumps(missing,ensure_ascii=False,indent=2))
 print(pdf.name,'fixes',len(fixes),'missing paragraphs',len(missing))
 for p in missing[:8]:print(repr(p[:200]))
(FIX/'font-map-corrections.json').write_text(json.dumps(allfixes,indent=2))
