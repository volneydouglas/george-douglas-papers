from pathlib import Path
import json
R=Path('/Users/volneydouglas/Documents/FamilyHistory');B=R/'book/george-douglas-archival/pages'; O=R/'repositories/george-douglas-papers/review/full-run-2026-09'
changes={
'04-079':('The place name following “enjoyed in” is unresolved.','The place name following “enjoyed in” reads Brushy after image review.'),
'04-080':('The surname before “a large Livery Stable” is uncertain.','Image review reads the verb build before “a large Livery Stable”; the earlier proposed surname has been withdrawn.'),
'05-044':('Source order is retained; the surname is uncertain.','Source order is retained. Image review supports Chadsey’s as the surname.'),
'05-052':('Two names remain uncertain.','Timmons is supported by image review; the other marked name remains uncertain.'),
'05-064':('Two words at the end of the fourth line of the second stanza are uncertain.','Image review supports door in the second stanza; the preceding marked word remains tentative.'),
'05-157':('Deputy signature is uncertain.','Image review supports the deputy signature H. C. Wise.'),
'06-008':('The final digit of the record-book number is uncertain.','The docket’s record-book number reads 91 after image review.'),
}
log=[]
for page,(a,z) in changes.items():
 p=B/(page+'.json');d=json.loads(p.read_text());assert a in d['editorial_notes'];before=d['editorial_notes'];d['editorial_notes']=before.replace(a,z);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');log.append({'page_id':page,'before':before,'after':d['editorial_notes'],'reason':'Synchronize editorial explanation with applied image-supported reading.'})
(O/'editorial-note-changes.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
p=R/'book/george-douglas-independent/05-folder2.md';s=p.read_text();a="[Reading note: The envelope's August postmark differs from the date on the following letter.]";z='[Reading note: The envelope has an August postmark. The following letter’s heading does not establish a month; its date is not reconciled with the envelope.]';assert a in s;p.write_text(s.replace(a,z))
p=O/'family-changes.json';d=json.loads(p.read_text());print(type(d));d.append({'file':'05-folder2.md','before':a,'after':z,'reason':'Withdraw the month comparison after correcting Sep to literal Sat.'});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
