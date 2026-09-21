from pathlib import Path
import os,subprocess,concurrent.futures,json
R=Path('/Users/volneydouglas/Documents/FamilyHistory')
W=R/'tmp/george_douglas/revision'
P='/Users/volneydouglas/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
S='/Users/volneydouglas/.codex/plugins/cache/openai-primary-runtime/documents/26.909.12148/skills/documents/render_docx.py'
env=os.environ.copy();env['PATH']='/Users/volneydouglas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override:'+env['PATH']
jobs=[]
for kind,folder in [('annotated','george-douglas-archival'),('family','george-douglas-independent')]:
 for doc in sorted((R/'output'/folder).glob('*.docx')):
  dest=W/('render-'+doc.stem.split('-')[-1] if kind=='annotated' else 'family-'+doc.stem)
  jobs.append((doc,dest))
def run(job):
 doc,dest=job;dest.mkdir(exist_ok=True)
 with (dest/'render.log').open('w') as log:r=subprocess.run([P,S,str(doc),'--output_dir',str(dest),'--emit_pdf'],env=env,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(doc,dest/'render.log')
 print('Rendered '+doc.name,flush=True)
 return {'file':str(doc),'render':str(dest),'pages':len(list(dest.glob('page-*.png')))}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,jobs))
(W/'renders.json').write_text(json.dumps(results,indent=2))
