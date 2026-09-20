"""Rebuild lossless evidence crops. Usage: python reproduce_images.py SOURCE_PDF_DIR [OUTPUT_DIR]"""
import hashlib, json, sys
from pathlib import Path
from PIL import ImageOps
from pypdf import PdfReader

base=Path(__file__).resolve().parent
source_dir=Path(sys.argv[1])
destination=Path(sys.argv[2]) if len(sys.argv)>2 else base
manifest=json.loads((base/'image-manifest.json').read_text())
readers={}
for m in manifest:
    s=m['source']; key=s['id']
    if key not in readers:
        path=source_dir/s['filename']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==s['sha256'],f'Source checksum mismatch: {path}'
        readers[key]=PdfReader(path)
    page=readers[key].pages[int(m['page'][3:])-1]
    assert len(page.images)==1
    im=page.images[0].image.convert('RGB')
    assert list(im.size)==m['native_size']
    im=im.rotate(m['rotation_ccw'],expand=True).crop(m['box'])
    variants={'original':im,'contrast':ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=1)}
    if m['gamma_exponent']:
        g=m['gamma_exponent']
        variants['gamma']=ImageOps.grayscale(im).point([round(255*(i/255)**g) for i in range(256)])
    for name,pixels in variants.items():
        target=destination/m['files'][name]['path']; target.parent.mkdir(parents=True,exist_ok=True)
        pixels.save(target)
        # PNG byte encoding can vary by Pillow version. Compare decoded pixels
        # as well when reproducing with different library versions.
        print(m['id'],name,hashlib.sha256(target.read_bytes()).hexdigest())
