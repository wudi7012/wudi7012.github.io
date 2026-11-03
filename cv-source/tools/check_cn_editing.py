"""End-to-end check: UTF-8 edits affect PDF text; unseen glyphs fail explicitly."""
from pathlib import Path
import shutil,subprocess,sys,tempfile
import pymupdf
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='cv-edit-check-') as t:
 work=Path(t)/'zh';shutil.copytree(root/'zh',work,ignore=shutil.ignore_patterns('generated','*.pdf','*.aux','*.log'))
 f=work/'Di_Wu_CV_CN.tex';s=f.read_text().replace(r'\CVText{t002}{24岁}',r'\CVText{t002}{25岁}');f.write_text(s)
 subprocess.run([sys.executable,str(root/'tools/prepare_cn.py'),str(work)],check=True,capture_output=True)
 subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Di_Wu_CV_CN.tex'],cwd=work,check=True,capture_output=True)
 with pymupdf.open(work/'Di_Wu_CV_CN.pdf') as d:
  text=d[0].get_text();assert '25岁' in text and '24岁' not in text
 f.write_text(s.replace(r'\CVText{t001}{吴笛}',r'\CVText{t001}{龘笛}'))
 result=subprocess.run([sys.executable,str(root/'tools/prepare_cn.py'),str(work)],capture_output=True,text=True)
 assert result.returncode!=0 and 'font subset lacks' in result.stderr
print('Passed: editable text changes the PDF; missing glyphs are rejected; no reference PDF needed to build.')
