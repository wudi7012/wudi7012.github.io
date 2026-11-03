"""Import editable text runs and exact drawing resources; never embeds a PDF page."""
from pathlib import Path
import argparse, re, json, hashlib
import pymupdf

ap=argparse.ArgumentParser();ap.add_argument('pdf');ap.add_argument('destination');args=ap.parse_args()
out=Path(args.destination)
if out.exists() and any(out.iterdir()):raise SystemExit('Destination must be empty; refusing to overwrite existing source.')
(out/'assets').mkdir(parents=True,exist_ok=True)
pdf=pymupdf.open(args.pdf);assert len(pdf)==1
page=pdf[0];raw=page.read_contents().decode('latin1')
fontmaps={}
for xref,_,_,_,name,*_ in page.get_fonts():
 obj=pdf.xref_object(xref);tu=int(re.search(r'/ToUnicode (\d+)',obj).group(1));cm=pdf.xref_stream(tu).decode()
 mapping={}
 for a,b,vals in re.findall(r'<([\dA-F]+)>\s*<([\dA-F]+)>\s*\[(.*?)\]',cm,re.S):
  for cid,u in zip(range(int(a,16),int(b,16)+1),re.findall(r'<([\dA-F]+)>',vals)):
   mapping[f'{cid:04X}']=bytes.fromhex(u).decode('utf-16-be')
 fontmaps[name]=mapping
# Preserve the original indirect object graph (fonts, image, color and graphics state).
resource=int(pdf.xref_get_key(page.xref,'Resources')[1].split()[0]);seen=set();objects=[]
def visit(x):
 if x in seen:return
 seen.add(x);s=pdf.xref_object(x)
 for child in re.findall(r'(\d+) 0 R',s):visit(int(child))
 entry={'id':x,'dictionary':s}
 if pdf.xref_is_stream(x):
  name=f'object-{x}.bin';(out/'assets'/name).write_bytes(pdf.xref_stream_raw(x));entry['stream']=name
 objects.append(entry)
visit(resource)
blocks=[];cursor=0;source=[];metrics={}
def decode(chain,font):return ''.join(fontmaps[font][h.upper()] for h in re.findall(r'<([0-9A-Fa-f]{4})> Tj',chain))
def escape(s):
 for a,b in [('\\',r'\textbackslash{}'),('{',r'\{'),('}',r'\}'),('%',r'\%'),('&',r'\&'),('#',r'\#'),('_',r'\_'),('$',r'\$')]:s=s.replace(a,b)
 return s
chain_re=r'(?:[-\d.]+ [-\d.]+ Td <[0-9A-Fa-f]{4}> Tj\s*)+'
for i,m in enumerate(re.finditer(r'BT\n(.*?)\nET',raw,re.S),1):
 block=m.group(0);font=re.search(r'/(F\d+) ',block).group(1);size=re.search(r'/F\d+ ([\d.]+) Tf',block).group(1)
 chains=list(re.finditer(chain_re,block));texts=[decode(c.group(0),font) for c in chains];assert texts
 assert all(t==texts[0] for t in texts),texts
 key=f't{i:03d}';text=texts[0]
 for chain in chains:
  entries=re.findall(r'([-\d.]+) ([-\d.]+) Td <([0-9A-Fa-f]{4})> Tj',chain.group(0))
  for prev,nxt in zip(entries,entries[1:]):
   metrics.setdefault(font,{}).setdefault(size,{})[prev[2].upper()]=nxt[0]
 blocks.append({'id':key,'prefix':raw[cursor:m.start()],'block':block,'font':font,'size':size,'original':text})
 source.append(r'\CVText{'+key+'}{'+escape(text)+'}')
 cursor=m.end()
manifest={'width':page.rect.width,'height':page.rect.height,'resource':resource,'objects':objects,'fontmaps':fontmaps,'metrics':metrics,'runs':blocks,'tail':raw[cursor:],'reference_sha256':hashlib.sha256(Path(args.pdf).read_bytes()).hexdigest()}
(out/'layout.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(out/'Di_Wu_CV_CN.tex').write_text(r'''% Fixed-layout, editable Chinese CV. Build using `make`, not standalone pdflatex.
% Text is real selectable PDF text; no whole-page PDF or screenshot is included.
% Each CVText corresponds to one original styled text run. Keep explicit line breaks.
\documentclass{article}
\input{generated/resources.tex}
\pagestyle{empty}
\begin{document}
\noindent\hbox{}%
'''+'\n'.join(source)+r'''
\CVFinish
\end{document}
''')
print(f'Imported {len(blocks)} editable runs, {len(objects)} resources, {len(fontmaps)} exact embedded font subsets.')
