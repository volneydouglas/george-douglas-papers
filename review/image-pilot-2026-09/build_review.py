"""Build the pilot overlay, portable HTML viewer, OCR diagnostic and PDF report.

Usage: python build_review.py --font-dir DIR [--pdf-output PATH]
Requires Pillow, reportlab. Readings are preserved in decisions.json, not generated here.
"""
import argparse, collections, csv, hashlib, html, json, re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image

ap=argparse.ArgumentParser(); ap.add_argument('--font-dir',type=Path,required=True); ap.add_argument('--pdf-output',type=Path)
args=ap.parse_args()
BASE=Path(__file__).resolve().parent; REPO=BASE.parents[1]
data=json.loads((BASE/'decisions.json').read_text()); rows=data['records']
manifest=json.loads((BASE/'image-manifest.json').read_text()); images={m['id']:m for m in manifest}
labels={'image_supported':'Image-supported reading','duplicate_witness':'Clearer duplicate witness','partial_reading':'Partial reading','context_only':'Conjectural completion','unresolved':'Unresolved'}
esc=html.escape

# Locate each original register item before making any changes. Repeated markers
# in one paragraph must be addressed by their position, never by global replace.
transcripts=json.loads((REPO/'editions/annotated/Supporting-files/Transcripts.json').read_text())
paragraphs={p['id']:p['text'] for page in transcripts['pages'] for p in page['paragraphs']}
register=list(csv.DictReader((REPO/'editions/annotated/Supporting-files/Unresolved-readings.tsv').open(),delimiter='\t'))
cursors=collections.defaultdict(int); locations={}
for r in register:
    pid=r['paragraph_id']; text=paragraphs[pid]
    start=text.find(r['annotation'],cursors[pid]); assert start>=0,r['item']
    end=start+len(r['annotation']); locations[r['item']]=(start,end); cursors[pid]=end
patches=[]
for r in rows:
    if r['replacement'] is None: continue
    pid=r['paragraph_id']; start,end=locations[r['item']]
    patches.append({'item':r['item'],'paragraph_id':pid,'paragraph_sha256':hashlib.sha256(paragraphs[pid].encode()).hexdigest(),'start':start,'end':end,'before':r['annotation'],'after':r['replacement'],'outcome':r['outcome'],'evidence_regions':r['evidence_regions']})
(BASE/'corrections.json').write_text(json.dumps({'status':'Applied only to corrected pilot excerpts; not to v1.0 edition exports','baseline_commit':'ae16c74','offset_unit':'Python Unicode code points, zero-based; end exclusive','patches':patches},indent=2,ensure_ascii=False)+'\n')
excerpts=['# Corrected pilot excerpts','', '**Draft AI-assisted overlay · 19 September 2026 · Original v1.0 files preserved**','', 'These selected paragraphs apply 16 image-supported literal readings and two partial surname recoveries. Unreviewed surrounding words retain their earlier status. Hidden or missing text stays marked; clearer-witness information is given in separate notes. This is not a certified transcript of each whole paragraph.','']
for pid in dict.fromkeys(r['paragraph_id'] for r in rows):
    original=paragraphs[pid]; revised=original
    for p in sorted((p for p in patches if p['paragraph_id']==pid),key=lambda p:p['start'],reverse=True):
        assert revised[p['start']:p['end']]==p['before']; revised=revised[:p['start']]+p['after']+revised[p['end']:]
    excerpts.extend([f'## {pid}','',revised,'','### Review notes',''])
    for r in [r for r in rows if r['paragraph_id']==pid]:
        excerpts.append(f"- **{r['item']} · {labels[r['outcome']]}:** {r['reading']}. {r['reason']}")
    excerpts.append('')
(BASE/'corrected-excerpts.md').write_text('\n'.join(excerpts).rstrip()+'\n')

# Small diagnostic, explicitly not a general OCR accuracy score.
ocr=json.loads((BASE/'vision-results.json').read_text())
assert len(ocr['records'])==76 and not any('error' in r for r in ocr['records'])
targets={'02-003-opening':('Of',r'\bOf\b'),'04-002-alfred':('Alfred',r'\bAlfred\b'),'04-017-denmark':('Denmark',r'\bDenmark\b'),'04-079-brushy':('Brushy',r'\bBrushy\b'),'04-080-build':('build',r'\bbuild\b'),'05-035-slip':('Sat',r'\bSat\b'),'05-037-chadsey':("Chadsey's",r"\bChad[\s-]*sey['’]?s\b"),'06-008-docket':('91',r'\b91\b'),'06-063-opening':('Claunch',r'\bClaunch\b')}
diagnostic=[]
for key,(target,pattern) in targets.items():
    variants=[]
    for r in ocr['records']:
        if not r['file'].startswith(key+'-'): continue
        top=' '.join(line['candidates'][0]['text'] for line in r['lines'])
        variants.append({'file':r['file'],'language_correction':r['usesLanguageCorrection'],'exact_target_in_top_ranked_output':bool(re.search(pattern,top,re.I))})
    assert len(variants)==4
    diagnostic.append({'region':key,'target':target,'match_expression':pattern,'runs':variants})
(BASE/'ocr-diagnostic.json').write_text(json.dumps({'scope':'Nine selected, image-supported targets within 19 difficult crop regions. Case-insensitive exact target search in concatenated top-ranked lines. Not CER/WER or a full-page benchmark.','engine':ocr['engine'],'os':ocr['os'],'completed_runs':76,'diagnostic_cases':diagnostic},indent=2)+'\n')

# Offline, source-linked image viewer. All text is escaped; no external assets.
css='''body{margin:0;background:#f4f2ec;color:#252a2a;font:17px/1.6 Georgia,serif}main{max-width:1050px;margin:auto;padding:40px 25px}h1,h2,h3,label,select,button,.meta{font-family:Arial,sans-serif}h1{font-size:40px;line-height:1.15;margin:12px 0}h2{font-size:23px}a{color:#175d66}header{border-bottom:3px solid #175d66;padding-bottom:25px}.meta{font-size:13px;letter-spacing:.04em;color:#596365}.stats{display:flex;gap:14px;flex-wrap:wrap}.stats span{background:white;padding:12px 16px;border:1px solid #d7dbd7}.stats b{font-size:28px;display:block}.controls{margin:25px 0;display:flex;gap:16px;flex-wrap:wrap}input,select{font:16px Arial;padding:10px;border:1px solid #9aabaa;max-width:100%}article{padding:22px 26px;margin:24px 0;background:white;border:1px solid #d4d9d7;border-top:4px solid #78938b;overflow-wrap:anywhere}article[data-outcome=image_supported]{border-top-color:#175d66}article h2{margin:0}.tag{font:13px Arial;color:#475751}blockquote{border-left:3px solid #c4d3cb;margin:10px 0;padding:8px 15px;background:#f6f8f6;white-space:pre-wrap}details{margin-top:18px}summary{cursor:pointer;font:16px Arial;color:#175d66}figure{margin:25px 0;padding-top:15px;border-top:1px solid #ddd}img{display:block;max-width:100%;height:auto;border:1px solid #ddd}figcaption{font:13px/1.5 Arial;margin:7px 0}.variants{margin:8px 0}button{cursor:pointer;background:#eef4f1;border:1px solid #91aaa1;padding:7px;margin-right:6px}button[aria-pressed=true]{background:#175d66;color:white}.empty{display:none}.note{background:#e8efeb;padding:15px 20px}@media(max-width:600px){main{padding:25px 12px}h1{font-size:31px}article{padding:18px 14px}}@media print{.controls,.variants{display:none}body{background:white}article{break-inside:avoid}a{color:inherit}}'''
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>George Douglas Papers · Image review</title><style>'+css+'</style><main><header><p class="meta">GEORGE DOUGLAS PAPERS · PRIVATE REVIEW ADDENDUM · 19 SEPTEMBER 2026</p><h1>Reading the difficult passages</h1><p>Fifty uncertainty items checked against the scans. An AI-assisted editorial record, with source crops and an explanation for every decision.</p><p><a href="George-Douglas-50-Item-Image-Review.pdf">Printable report</a> · <a href="corrected-excerpts.md">Corrected pilot excerpts</a> · <a href="README.md">Method and limitations</a> · <a href="decisions.json">Decision data</a></p><div class="stats">']
for key in labels: parts.append(f'<span><b>{data["counts"][key]}</b>{esc(labels[key])}</span>')
parts.append('</div></header><p class="note">Original edition exports are unchanged. Duplicate-witness notes do not make missing or hidden letters readable on the damaged scan. This selected sample is not an estimate of the other 1,150 items. No independent human verification is claimed.</p><div class="controls"><label>Find an item or word<br><input id="query" type="search" placeholder="e.g. Guthrie or 06-008"></label><label>Show outcome<br><select id="outcome"><option value="">All 50 items</option>')
for key,label in labels.items(): parts.append(f'<option value="{key}">{esc(label)}</option>')
parts.append('</select></label></div><p id="shown" class="meta" aria-live="polite">50 items shown</p>')
for r in rows:
    parts.append(f'<article id="{r["item"]}" data-outcome="{r["outcome"]}"><h2>{r["item"]}</h2><p class="tag">{esc(labels[r["outcome"]])} · {r["paragraph_id"]} · source scan {r["scan_page"]}</p><p><b>Earlier annotation:</b> {esc(r["annotation"])}</p><blockquote>{esc(r["context"])}</blockquote><p><b>Text-only review proposal:</b> {esc(r["proposed_correction"] or "No proposal")}</p><p><b>Image review:</b> {esc(r["reading"])}</p><p>{esc(r["reason"])}</p><p class="meta">{esc(r["confidence_scope"])}</p><details><summary>Inspect {len(r["evidence_regions"])} source crop(s)</summary>')
    for i,key in enumerate(r['evidence_regions']):
        m=images[key]; original=m['files']['original']['path']; imageid=r['item']+'-'+str(i)
        parts.append(f'<figure><figcaption><b>{key}</b> · {esc(m["source"]["filename"])} · PDF scan {int(m["page"][3:])}<br>Native crop {m["box"]}, after {m["rotation_ccw"]}° counterclockwise rotation. <a href="{original}" target="_blank">Open original at full size</a></figcaption><div class="variants">')
        for name,f in m['files'].items(): parts.append(f'<button type="button" data-image="{imageid}" data-src="{f["path"]}" aria-pressed="{str(name=="original").lower()}">{name.title()}</button>')
        parts.append(f'</div><img id="{imageid}" src="{original}" loading="lazy" alt="Source crop {key}; see the evidence note above"></figure>')
    parts.append('</details></article>')
parts.append('''<footer><p>Source: George Douglas Papers, CRS MS 5, ACU Special Collections and Archives, Brown Library. Crops retained in this private review copy for verification. No ACU endorsement is implied.</p></footer></main><script>
const cards=[...document.querySelectorAll('article')],q=document.querySelector('#query'),s=document.querySelector('#outcome');
function filter(){let n=0;for(const c of cards){const show=(!s.value||c.dataset.outcome===s.value)&&c.textContent.toLowerCase().includes(q.value.toLowerCase());c.hidden=!show;if(show)n++;}document.querySelector('#shown').textContent=n+' items shown';}
q.addEventListener('input',filter);s.addEventListener('change',filter);
for(const b of document.querySelectorAll('[data-image]'))b.addEventListener('click',()=>{document.getElementById(b.dataset.image).src=b.dataset.src;for(const other of b.parentElement.children)other.setAttribute('aria-pressed',String(other===b));});
</script></html>''')
(BASE/'evidence.html').write_text(''.join(parts))

# Printable report, containing full decisions but not the entire image gallery.
for name,suffix in [('Review','Regular'),('ReviewBold','Bold'),('ReviewItalic','Italic')]: pdfmetrics.registerFont(TTFont(name,str(args.font_dir/f'LiberationSans-{suffix}.ttf')))
pdfmetrics.registerFontFamily('Review',normal='Review',bold='ReviewBold',italic='ReviewItalic',boldItalic='ReviewBold')
styles={
 'title':ParagraphStyle('title',fontName='ReviewBold',fontSize=27,leading=31,textColor=colors.HexColor('#174d54'),spaceAfter=15),
 'h':ParagraphStyle('h',fontName='ReviewBold',fontSize=14,leading=18,spaceBefore=13,spaceAfter=8,textColor=colors.HexColor('#174d54'),keepWithNext=True),
 'p':ParagraphStyle('p',fontName='Review',fontSize=10.4,leading=14.5,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Review',fontSize=8.5,leading=11.5,spaceAfter=7,textColor=colors.HexColor('#526162')),
 'case':ParagraphStyle('case',fontName='ReviewBold',fontSize=11,leading=15,spaceAfter=6,textColor=colors.HexColor('#174d54'))}
def norm(t): return str(t).replace('–','-').replace('—','-').replace('‑','-')
def P(t,style='p'): return Paragraph(esc(norm(t)).replace('\n','<br/>'),styles[style])
story=[P('George Douglas Papers','small'),P('Fifty difficult readings\nAn image-review pilot','title'),P('Private review addendum | 19 September 2026','small'),P('The pilot confirms that useful work remains. Direct image inspection supports sixteen literal readings, verifies twelve links to clearer overlapping scans, and partly recovers two names. Two missing-letter completions remain conjectural; eighteen items remain unresolved.'),P('These are register items, not unique words. Some refer to the same signature or duplicate leaf. The deliberate sample cannot estimate the recovery rate for the remaining 1,150 items.')]
table=[[P('Outcome','small'),P('Items','small')]]+[[P(label),P(data['counts'][key])] for key,label in labels.items()]
t=Table(table,colWidths=[410,70],hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8efeb')),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#90a7a0')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),3)]));story+=[t]
story += [P('What changed','h'),P('Brushy and build become readable through letter forms and same-hand comparison. The Hancock initials read Wm L. The initial immediately before Hawkins reads F; the preceding word still needs checking. Guthrie is recoverable, but the notary’s given name is not.'),P('Two proposed harmonizations fail the image check: the later slip visibly says Sat, and the deed docket says 91 while the separate recording certificate says 92. Preserve those distinctions.'),P('Status and how to use this report','h'),P('This is an AI-assisted editorial review, not an independently human-verified scholarly edition. The original v1.0 files are preserved. The companion corrected-excerpts.md applies the sixteen literal changes and two partial surname recoveries only to an explicitly labeled draft overlay. Missing and obscured text stays marked, with separate witness notes.'),P('For full-size source crops and original/contrast comparisons, open evidence.html from the downloaded addendum folder. decisions.json and corrections.json retain the item-level decisions and reversible changes. All fifty decisions follow in this report.'),P('Source credit: George Douglas Papers, 1830-1939, CRS MS 5, ACU Special Collections and Archives, Brown Library, Abilene Christian University. This is a private family contribution; no ACU endorsement or review is represented.','small'),PageBreak()]
story += [P('Method and practical limits','title'),P('Sample and provenance','h'),P('Fifty items were selected before adjudication: 29 tentative readings, nine unread spans, nine losses and three obstructions, across nineteen selected scan pages. The other agent’s text-only review was read first, so this was not a blinded comparison. Agreement between the AI-assisted family and annotated editions is not independent human confirmation.'),P('Image evidence','h'),P('Four supplied source PDFs were verified by SHA-256. Native embedded images were extracted, rotated in exact 90-degree steps as needed and cropped without upscaling. Forty-three original RGB regions and their grayscale/1% autocontrast variants are provided. Six also have documented gamma adjustments. No generative restoration was used. The manifest records sources, coordinates, rotation, processing and checksums.'),P('Overlaps were matched by handwriting, line breaks, signatures and layout. Words supplied by a clearer duplicate are identified as such. Tonal changes cannot recover physically missing paper or ink.'),P('Local OCR diagnostic','h'),P('Apple Vision completed 76 local runs: nineteen regions, two image variants, language correction on and off. Nine image-supported target readings were checked in the top-ranked output. Each configuration recovered only Sat (one of nine). No additional accepted reading came from OCR. This is a small difficult-crop diagnostic, not a character-error rate or a benchmark of trained handwriting recognition.'),P('Transkribus and Kraken were not tested. A handwriting-specific model remains an option, after establishing checked reference text and a held-out evaluation set. The pilot does not show that every useful tool has been exhausted.'),P('Recommended sequence','h'),P('First map the remaining duplicate leaves, then prepare letter-form examples by writer. Audit entire lines around dense uncertainty clusters: on 06-063 and 06-116, some previously confident surrounding words also need checking. Obtain independent human paleographic review before treating the changes as a university reference contribution.'),P('Methods background','h')]
for label,url in [('Smithsonian historical handwriting guide','https://transcription.si.edu/sites/default/files/uploads/transcribing_historical_handwriting_in_the_smithsonian_transcription_center_1.pdf'),('Transkribus data preparation','https://help.transkribus.org/data-preparation'),('Kraken documentation','https://kraken.re/main/index.html'),('OCR-D workflows','https://ocr-d.de/en/workflows')]:
    story.append(Paragraph(f'<link href="{url}" color="#175d66">{label}</link>',styles['small']))
story += [P('These method references do not validate the readings. Full citations, rights information and reproduction instructions are in README.md. Nathaniel Lynn Douglas’s father remains unestablished.','small'),PageBreak(),P('Decisions and evidence','title'),P('Locators name the source PDF and its one-based scan page, followed by the existing transcript paragraph/item. They are not original manuscript page numbers. Evidence region names locate PNG crops in the companion images folder.','small')]
for r in rows:
    block=[P(r['item']+' | '+labels[r['outcome']],'case'),P(r['paragraph_id']+' | '+r['annotation']+' → '+r['reading']),P(r['reason']),P('Evidence: '+', '.join(r['evidence_regions'])+'.','small'),Spacer(1,9)]
    story.append(KeepTogether(block))
pdfout=args.pdf_output or BASE/'George-Douglas-50-Item-Image-Review.pdf'; pdfout.parent.mkdir(parents=True,exist_ok=True)
def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#c4d0cc'));canvas.line(54,43,558,43)
    canvas.setFont('Review',8);canvas.setFillColor(colors.HexColor('#526162'))
    canvas.drawString(54,30,'George Douglas Papers | AI-assisted private review | 19 September 2026');canvas.drawRightString(558,30,str(doc.page))
doc=SimpleDocTemplate(str(pdfout),pagesize=(612,792),leftMargin=54,rightMargin=54,topMargin=47,bottomMargin=57,title='George Douglas Papers - 50-item image review',author='AI-assisted editorial review prepared for Volney Douglas')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(json.dumps({'items':len(rows),'patches':len(patches),'selected_paragraphs':len({r['paragraph_id'] for r in rows}),'regions':len(images),'pdf':str(pdfout)}))
