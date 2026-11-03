"""Compare actual PDF pixels, text, geometry and embedded resources, fail on differences."""
from pathlib import Path
import argparse,json,hashlib,re,subprocess,tempfile
import numpy as np
import pymupdf
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('reference');ap.add_argument('candidate');ap.add_argument('--report',required=True);a=ap.parse_args()
ref=pymupdf.open(a.reference);new=pymupdf.open(a.candidate)
result={'reference_sha256':hashlib.sha256(Path(a.reference).read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(Path(a.candidate).read_bytes()).hexdigest(),'renderers':{'MuPDF':pymupdf.VersionBind,'Poppler':subprocess.run(['pdftoppm','-v'],capture_output=True,text=True).stderr.splitlines()[0]},'page_count_equal':len(ref)==len(new),'pages':[]}
assert len(ref)==len(new),'Different page count'
for i,(p,q) in enumerate(zip(ref,new)):
 row={'page':i+1,'page_box_equal':list(p.rect)==list(q.rect),'text_equal':p.get_text()==q.get_text(),'mupdf':[]}
 for dpi in [72,144,300,600]:
  x=p.get_pixmap(dpi=dpi);y=q.get_pixmap(dpi=dpi)
  assert (x.width,x.height,x.n)==(y.width,y.height,y.n)
  xx=np.frombuffer(x.samples,dtype=np.uint8).reshape(-1,x.n);yy=np.frombuffer(y.samples,dtype=np.uint8).reshape(-1,y.n)
  row['mupdf'].append({'dpi':dpi,'different_pixels':int(np.any(xx!=yy,axis=1).sum())})
 with tempfile.TemporaryDirectory(prefix='cv-verify-') as t:
  imgs=[]
  for n,f in enumerate([a.reference,a.candidate]):
   dest=str(Path(t)/str(n));subprocess.run(['pdftoppm','-f',str(i+1),'-l',str(i+1),'-singlefile','-r','300','-png',f,dest],check=True,capture_output=True)
   imgs.append(np.array(Image.open(dest+'.png').convert('RGB')))
  row['poppler']={'dpi':300,'different_pixels':int(np.any(imgs[0]!=imgs[1],axis=2).sum())}
 def font_hashes(doc,pg):return sorted(hashlib.sha256(doc.extract_font(x[0])[3]).hexdigest() for x in pg.get_fonts())
 row['font_bytes_equal']=font_hashes(ref,p)==font_hashes(new,q)
 row['image_bytes_equal']=sorted(hashlib.sha256(ref.xref_stream_raw(x[0])).hexdigest() for x in p.get_images())==sorted(hashlib.sha256(new.xref_stream_raw(x[0])).hexdigest() for x in q.get_images())
 row['normalized_drawing_operators_equal']=re.sub(rb'\s+',b' ',p.read_contents()).strip()==re.sub(rb'\s+',b' ',q.read_contents()).strip()
 result['pages'].append(row)
result['visual_and_text_match']=all(p['page_box_equal'] and p['text_equal'] and all(v['different_pixels']==0 for v in p['mupdf']) and p['poppler']['different_pixels']==0 for p in result['pages'])
Path(a.report).parent.mkdir(parents=True,exist_ok=True);Path(a.report).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));assert result['visual_and_text_match'],'PDF differs; see report'
