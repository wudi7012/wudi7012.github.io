from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parents[1]/'en/fonts'
for name,expected in json.loads((p/'checksums.json').read_text()).items():
 f=p/name
 if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=expected:
  raise SystemExit(f'Missing or different font: {name}. Run make fonts. Font substitution is disabled.')
print('Approved English font files verified.')
