from pathlib import Path
import json,shutil
ROOT=Path('/Users/volneydouglas/Documents/FamilyHistory')
REPO=ROOT/'repositories/george-douglas-papers'
REV=REPO/'review/full-run-2026-09'
WORK=ROOT/'tmp/george_douglas/revision';WORK.mkdir(exist_ok=True)
p=ROOT/'tmp/george_douglas/archival/build_archival.py'
s=p.read_text().replace('1.0','1.1')
s=s.replace("register=[]", "index=json.loads((BOOK/'uncertainty-index.json').read_text())\nindex_by_block=collections.defaultdict(list)\nfor row in index:index_by_block[row['paragraph_id']].append(row)\nregister=[]")
s=s.replace("seq+=1\n   category=", "seq+=1\n   indexed=index_by_block[p['id']].pop(0)\n   assert indexed['annotation']==m.group(0),(p['id'],indexed,m.group(0))\n   category=")
s=s.replace("'item':f\"{d['id']}-U{seq:03}\"", "'item':indexed['item']")
s=s.replace("'proposed_correction':'','reviewer_and_date':'','evidence':''", "'proposed_correction':indexed.get('proposed_correction',''),'reviewer_and_date':indexed.get('reviewer_and_date',''),'evidence':indexed.get('evidence','')")
s=s.replace("This transcription was prepared separately from the plain-English family edition, which modernized wording and summarized some repetitive forms. The other agent’s work was not consulted.","The first edition was prepared separately from the plain-English family edition. For version 1.1, the other agent’s contextual review and the family edition were consulted to guide image checks; this revision is not a blinded comparison.")
s=s.replace("Each scan received an initial reading; selected doubtful passages received a focused second reading.","Each scan received an initial reading. Version 1.1 adds local OCR processing of all 193 pages containing the original 1,200 uncertainties, and applies selected image-checked corrections. OCR completion is not a complete new visual check; the item ledger records which passages were individually adjudicated.")
s=s.replace("The register includes tentative readings, unread text, loss and obstruction;", "The register retains the original uncertainty IDs; resolved IDs are retired and new IDs use higher numbers. The review ledger preserves all 1,200 baseline items. The register includes tentative readings, unread text, loss and obstruction;")
s=s.replace('The matching TSV has blank columns for corrections, reviewers and evidence.','The matching TSV preserves proposed readings, reviewers and evidence.\nReview-summary.txt explains the revision and points to its item ledger.')
s=s.replace('The TSV copy has empty correction, reviewer and evidence columns for future work.', 'The TSV copy retains contextual proposals and review evidence. Original uncertainty IDs remain stable; retired IDs appear in the revision ledger.')
# Carry retained proposal/evidence text into the human-readable register too.
s=s.replace("+E(r['context'])+'</td></tr>'", "+E(r['context'])+'<br><em>Proposal:</em> '+E(r['proposed_correction'])+'<br><em>Review:</em> '+E(r['evidence'])+'</td></tr>'")
(WORK/'build_archival.py').write_text(s)
s=(ROOT/'tmp/george_douglas/build_independent.py').read_text()
s=s.replace('An independent reading in plain English','A revised reading in plain English')
s=s.replace("d.add_paragraph('Prepared for Volney Douglas\\nSeptember 2026')","d.add_paragraph('Prepared for Volney Douglas\\nRevision 1.1 September 2026')")
s=s.replace('The other agent’s work was not consulted. Part of the older transcription was seen during initial inventory, before the independent-reading request, then excluded. This is an independent reading in execution, not a blind comparison. See Volume I for the full reading guide and source list.', 'The first reading was prepared separately. Revision 1.1 incorporates selected source-image checks informed by comparison with the annotated edition and another agent’s contextual review. It is AI-assisted and has not been independently human verified. See Volume I for the method and limits.')
(WORK/'build_family.py').write_text(s)

# Preserve original authoring text before making local, exact family-edition changes.
edits={
'04-folder1.md':[
 ('He died on May 5 from a wound received on April 18.','He died on June 5 from a wound received on May 18.'),
 ('Allie leaves tomorrow for [Gunter?]','Allie leaves tomorrow for Gunter')],
'05-folder2.md':[
 ('by [B.?] Hawkins, Clerk.','[uncertain abbreviation] F. Hawkins, Clerk.'),
 ('Bardsdale, California, September 29, 1893.','Bardsdale, California, [written “Sat 29, 1893”; the month is not established].'),
 ('Bardsdale, September 29, 1893','Bardsdale, [written “Sat, 29th, 1893”; month uncertain]'),
 ('[Reese?] Guthrie','[given name unread] Guthrie'),
 ('by [A. Lasswell?], deputy','by A. Lasswell, deputy'),
 ('through H. C. [Ware?], deputy','through H. C. Wise, deputy')],
'06-folder3.md':[
 ('Mrs. [Claunch?] by her daughter.','Mrs. Claunch by her daughter.'),
 ('The page 8 docket gives the same filing and recording dates,','[The page 8 docket reads volume 91, while the page 11 certificate reads 92; this disagreement is preserved.] The page 8 docket gives the same filing and recording dates,')]
}
family_log=[]
for fn,changes in edits.items():
 text=(REPO/'editions/family/Plain-text'/fn).read_text()
 for a,b in changes:
  assert text.count(a)==1,(fn,a,text.count(a));text=text.replace(a,b);family_log.append({'file':fn,'before':a,'after':b})
 (ROOT/'book/george-douglas-independent'/fn).write_text(text)
guide=(REPO/'editions/family/Plain-text/00-reading-guide.md').read_text()
guide=guide.replace('These readings were made from the scanned manuscript images, without consulting the other agent\'s work.', 'The first edition was read from the scanned manuscript images without consulting the other agent’s work. Revision 1.1 applies selected image-checked corrections after consulting the other agent’s contextual review and comparing the annotated and family editions. This revision is not a blinded comparison; neither AI-assisted edition has been independently human verified.')
guide=guide.replace('This is therefore an independent reading in execution, but it is not a blind comparison.', 'The original version is preserved in the private repository for comparison. The full run processed the 193 pages containing the original 1,200 uncertain items; it did not independently verify every word. Only selected, image-supported corrections were applied.')
(ROOT/'book/george-douglas-independent/00-reading-guide.md').write_text(guide)
(REV/'family-changes.json').write_text(json.dumps(family_log,ensure_ascii=False,indent=2)+'\n')
print('Prepared revision builders and',len(family_log),'family text changes')
