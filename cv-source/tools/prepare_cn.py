"""Encode editable UTF-8 LaTeX runs using the original PDF font resources."""
from pathlib import Path
import re,json,argparse
ap=argparse.ArgumentParser();ap.add_argument('directory');a=ap.parse_args();p=Path(a.directory)
m=json.loads((p/'layout.json').read_text());g=p/'generated';g.mkdir(exist_ok=True)
source=(p/'Di_Wu_CV_CN.tex').read_text()
def unescape(s):
 for a,b in [(r'\textbackslash{}','\\'),(r'\{','{'),(r'\}','}'),(r'\%','%'),(r'\&','&'),(r'\#','#'),(r'\_','_'),(r'\$','$')]:s=s.replace(a,b)
 return s
texts={}
for line in source.splitlines():
 if line.startswith(r'\CVText{'):
  match=re.fullmatch(r'\\CVText\{(t\d+)\}\{(.*)\}',line)
  if not match:raise ValueError('Keep each CVText command on one source line: '+line)
  key,s=match.groups();assert key not in texts; texts[key]=unescape(s)
assert set(texts)=={r['id'] for r in m['runs']},'Text run IDs must match layout.json.'
# Reserve object IDs before writing any references; raw streams retain original filters.
lines=[r'\pdfpagewidth=615bp',r'\pdfpageheight=870bp',r'\pdfcompresslevel=0',r'\pdfobjcompresslevel=0']
for o in m['objects']:
 lines.append(r'\pdfobj reserveobjnum\expandafter\edef\csname CVObj'+str(o['id'])+r'\endcsname{\the\pdflastobj}')
def refs(s):return re.sub(r'(\d+) 0 R',lambda x:r'\csname CVObj'+x[1]+r'\endcsname\space 0 R',s.replace('\n',' '))
for o in m['objects']:
 n=r'\csname CVObj'+str(o['id'])+r'\endcsname'
 if 'stream' in o:
  attr=re.sub(r'/Length\s+\d+(?:\s+0\s+R)?\b','',o['dictionary'][2:-2]);lines.append(r'\immediate\pdfobj useobjnum '+n+' stream attr {'+refs(attr)+'} file {assets/'+o['stream']+'}')
 else:lines.append(r'\immediate\pdfobj useobjnum '+n+' {'+refs(o['dictionary'])+'}')
resources=next(o['dictionary'] for o in m['objects'] if o['id']==m['resource'])[2:-2]
lines += [r'\pdfpageresources{'+refs(resources)+'}',r'\newcommand{\CVText}[2]{\input{generated/#1.tex}}',r'\newcommand{\CVFinish}{\input{generated/tail.tex}}']
expanded=[]
for line in lines:
 if line.startswith(r'\immediate\pdfobj'):
  line=r'\edef\CVWrite{'+line.replace(r'\immediate\pdfobj',r'\noexpand\immediate\noexpand\pdfobj',1)+r'}\CVWrite'
 elif line.startswith(r'\pdfpageresources'):
  line=r'\edef\CVWrite{\noexpand'+line+r'}\CVWrite'
 expanded.append(line)
(g/'resources.tex').write_text('\n'.join(expanded))
changed=[]
for run in m['runs']:
 text=texts[run['id']];block=run['block'];font=run['font'];size=run['size']
 if text!=run['original']:
  changed.append(run['id']);rev={v:k for k,v in m['fontmaps'][font].items()}
  missing=sorted(set(text)-set(rev))
  if missing:raise ValueError(f"{run['id']}: font subset lacks {''.join(missing)!r}. Import matching full font before adding new glyphs; substitution is forbidden.")
  widths=m['metrics'][font][size]
  def chain(match):
   first=re.match(r'([-\d.]+) ([-\d.]+) Td',match[0]);parts=[]
   for i,char in enumerate(text):
    if i==0:pos=first[1]+' '+first[2]
    else:
     prev=rev[text[i-1]]
     if prev not in widths:raise ValueError(f'No original advance for {text[i-1]!r} at size {size}; explicit layout adjustment required.')
     pos=widths[prev]+' 0'
    parts.append(f'{pos} Td <{rev[char]}> Tj\n')
   return ''.join(parts)
  block=re.sub(r'(?:[-\d.]+ [-\d.]+ Td <[0-9A-Fa-f]{4}> Tj\s*)+',chain,block)
 (g/(run['id']+'.tex')).write_text('\\pdfliteral page {\n'+(run['prefix']+block).replace('\n',' ')+'}%\n')
(g/'tail.tex').write_text('\\pdfliteral page {\n'+m['tail'].replace('\n',' ')+'}%\n')
print('Prepared 100 text runs. Edited runs:',', '.join(changed) or 'none (exact original placement)')
