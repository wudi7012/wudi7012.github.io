"""Install the exact regular/bold YaHei 5.00 files used by the approved English CV."""
from pathlib import Path
import hashlib,urllib.request,subprocess,tempfile,shutil
root=Path(__file__).resolve().parents[1];target=root/'en/fonts'
url='https://web.archive.org/web/20080520000000id_/https%3A//download.microsoft.com/download/c/7/e/c7e5397d-004f-468b-a441-dd0828dc1a17/VistaFont_CHS.EXE'
with tempfile.TemporaryDirectory(prefix='cv-fonts-') as d:
 p=Path(d)/'VistaFont_CHS.EXE';urllib.request.urlretrieve(url,p)
 if hashlib.sha1(p.read_bytes()).hexdigest()!='6a825eeb1a36628ef25fb777d259d0aff3749afb':raise RuntimeError('Font package checksum mismatch')
 subprocess.run(['cabextract','-q','-d',d,str(p)],check=True)
 target.mkdir(parents=True,exist_ok=True)
 for n in ['msyh.ttf','msyhbd.ttf']:shutil.copy2(Path(d)/n,target/n)
 shutil.copy2(Path(d)/'EULA.txt',target/'Microsoft-EULA.txt')
print('Exact English font files installed locally; ignored by Git.')
