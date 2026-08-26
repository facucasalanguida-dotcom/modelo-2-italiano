# Ensambla el HTML autocontenido del recorrido virtual.
import base64, io, json, struct, os
from PIL import Image

SP = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(SP)
TEXDIR = os.path.join(SCRATCH, 'tex')

blob = open(os.path.join(SCRATCH, 'walk.bin'), 'rb').read()
jlen = struct.unpack('<I', blob[4:8])[0]
meta = json.loads(blob[8:8 + jlen])
offsets = json.load(open(os.path.join(SCRATCH, 'walk.bin.offsets.json')))

# texturas usadas por los materiales, reescaladas a JPEG
SIZES = {'floor_diff': 640, 'wall_diff': 384, 'wood_diff': 512,
         'wood_diff_v': 512, 'latte': 192, 'diario': 384, 'carta': 192,
         'art_0': 256, 'art_1': 256, 'art_2': 256}
used = sorted({m['spec']['tex'] for m in meta['mats'] if m['spec']['tex']})
tex = {}
for name in used:
    p = os.path.join(TEXDIR, name + '.png')
    if not os.path.exists(p):
        print('SIN TEXTURA:', name); continue
    im = Image.open(p).convert('RGB')
    s = SIZES.get(name, 384)
    im.thumbnail((s, s), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=72, optimize=True)
    tex[name] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
print('texturas:', {k: len(v) // 1024 for k, v in tex.items()}, 'KB')

nap = {'bin': base64.b64encode(blob).decode(), 'offsets': offsets, 'tex': tex}
bundle = open(os.path.join(SP, 'bundle.js')).read()

html = """<title>Recorrido Café Napoli</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#0d1218;
    font-family:'Segoe UI',system-ui,sans-serif}
  #c{width:100vw;height:100vh;display:block;touch-action:none;cursor:crosshair}
  #start{position:fixed;inset:0;display:flex;align-items:center;
    justify-content:center;background:rgba(10,15,22,.72);z-index:10}
  #card{background:#151d27;color:#f2efe8;border-radius:14px;max-width:420px;
    padding:30px 34px;box-shadow:0 24px 60px rgba(0,0,0,.5);text-align:center}
  #card h1{margin:0 0 4px;font-size:24px;letter-spacing:.14em;color:#e8b768}
  #card p.sub{margin:0 0 18px;color:#8fa3b8;font-size:13px;
    letter-spacing:.28em;text-transform:uppercase}
  #card ul{list-style:none;margin:0 0 20px;padding:0;font-size:14.5px;
    line-height:2;color:#cfd8e0;text-align:left}
  #card b{color:#f2efe8;background:#22303f;border-radius:5px;
    padding:1px 7px;font-weight:600}
  #enter{background:#e8b768;color:#1a1408;border:0;border-radius:9px;
    font-size:16px;font-weight:700;padding:11px 34px;cursor:pointer}
  #enter:hover{background:#f2c67e}
  #card p.nota{margin:14px 0 0;font-size:12px;color:#8fa3b8}
  #hint{position:fixed;left:14px;bottom:12px;color:#e9eef2;font-size:12.5px;
    background:rgba(13,18,24,.55);border-radius:8px;padding:6px 12px;
    z-index:5;opacity:.85;pointer-events:none}
</style>
<canvas id="c"></canvas>
<div id="start"><div id="card">
  <h1>CAFÉ NAPOLI</h1>
  <p class="sub">Málaga · recorrido virtual</p>
  <ul>
    <li><b>W A S D</b> o <b>flechas</b> — caminar</li>
    <li><b>ratón</b> — mirar (clic para capturar el cursor)</li>
    <li><b>Shift</b> — caminar más rápido</li>
    <li><b>móvil</b> — pulgar izq. mueve · pulgar dcho. mira</li>
  </ul>
  <button id="enter">Entrar al café</button>
  <p class="nota">Solo planta baja — la planta superior está cerrada.</p>
</div></div>
<div id="hint">WASD caminar · ratón mirar · Shift correr</div>
<script>window.NAP = __NAPDATA__;</script>
<script>__BUNDLE__</script>
"""
html = html.replace('__NAPDATA__', json.dumps(nap)).replace('__BUNDLE__', bundle)
dst = '/home/user/modelo-2-italiano/docs/tour'
os.makedirs(dst, exist_ok=True)
out = os.path.join(dst, 'cafe_napoli_tour.html')
open(out, 'w').write(html)
print('HTML:', out, len(html) // 1024, 'KB')
