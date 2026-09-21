from pathlib import Path
import json,zipfile,hashlib,shutil
R=Path('/Users/volneydouglas/Documents/FamilyHistory');REPO=R/'repositories/george-douglas-papers';O=REPO/'review/full-run-2026-09'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checksum(folder):
 files=sorted(p for p in folder.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt' and not p.name.startswith('.') and '__pycache__' not in p.parts)
 (folder/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(folder)}\n' for p in files))
packages=[]
for local,kind,stem in [('george-douglas-archival','annotated','George-Douglas-University-Transcription-Edition'),('george-douglas-independent','family','George-Douglas-Independent-Family-Edition')]:
 folder=R/'output'/local
 if kind=='annotated':dest=folder/'Supporting-files'
 else:dest=folder
 for name in ['visual-review.json','font-repair-visual-check.json']:shutil.copy2(O/name,dest/name)
 files=sorted(set(str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() and not p.name.startswith('.'))|{'manifest.txt','SHA256SUMS.txt'})
 (folder/'manifest.txt').write_text('\n'.join(files)+'\n');checksum(folder)
 archive=R/'output'/(stem+'.zip')
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in files:z.write(folder/p,stem+'/'+p)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None;assert z.namelist()==[stem+'/'+p for p in files]
  for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
   digest,name=line.split('  ',1);assert hashlib.sha256(z.read(stem+'/'+name)).hexdigest()==digest
  assert sum(p.endswith('.pdf') for p in files)==sum(p.endswith('.docx') for p in files)==4
 shutil.copytree(folder,REPO/'editions'/kind,dirs_exist_ok=True);shutil.copy2(archive,REPO/'downloads'/archive.name)
 packages.append({'file':archive.name,'files':len(files),'bytes':archive.stat().st_size,'sha256':sha(archive),'zip_integrity':'passed','all_payload_checksums_verified':True})
(O/'package-validation.json').write_text(json.dumps(packages,indent=2)+'\n');checksum(O)
print(json.dumps(packages,indent=2))
