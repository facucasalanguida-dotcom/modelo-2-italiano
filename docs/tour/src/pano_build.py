# Ensambla el recorrido fotorrealista 360 en un HTML autocontenido.
import base64, io, json, os
from PIL import Image

SP = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(SP)

NODES = {
 'p_entrada':  [8.15, 1.55],
 'p_ventanal': [4.90, 2.20],
 'p_sala':     [3.05, 3.45],
 'p_mampara':  [2.30, 5.85],
 'p_barra':    [5.35, 6.10],
 'p_escalera': [7.55, 4.35],
 'p_tras_barra': [5.60, 7.95],
 'p_cocina':   [1.75, 7.55],
}
LINKS = {
 'p_entrada':  ['p_ventanal', 'p_escalera'],
 'p_ventanal': ['p_entrada', 'p_sala', 'p_escalera'],
 'p_sala':     ['p_ventanal', 'p_mampara', 'p_barra'],
 'p_mampara':  ['p_sala', 'p_barra', 'p_cocina'],
 'p_barra':    ['p_mampara', 'p_sala', 'p_escalera', 'p_tras_barra'],
 'p_escalera': ['p_barra', 'p_entrada', 'p_ventanal', 'p_tras_barra'],
 'p_tras_barra': ['p_barra', 'p_escalera', 'p_cocina'],
 'p_cocina':   ['p_tras_barra', 'p_mampara'],
}

panos = {}
for name in NODES:
    p = os.path.join(SCRATCH, name + '.png')
    im = Image.open(p).convert('RGB')
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=88, optimize=True)
    panos[name] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    print(name, len(panos[name]) // 1024, 'KB')

nap = {'panos': panos, 'nodes': NODES, 'links': LINKS,
       'start': 'p_entrada', 'yaw0': 0.6}
bundle = open(os.path.join(SP, 'pano_bundle.js')).read()

html = """<title>Recorrido Café Napoli</title>
<style>
  html,body{margin:0;height:100%;overflow:hidden;background:#0d1218;
    font-family:'Segoe UI',system-ui,sans-serif}
  #c{width:100vw;height:100vh;display:block;touch-action:none;cursor:grab}
  #c:active{cursor:grabbing}
  #start{position:fixed;inset:0;display:flex;align-items:center;
    justify-content:center;background:rgba(10,15,22,.72);z-index:10}
  #card{background:#151d27;color:#f2efe8;border-radius:14px;max-width:430px;
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
  <p class="sub">Málaga · recorrido fotorrealista</p>
  <ul>
    <li><b>arrastra</b> — mirar alrededor</li>
    <li><b>toca los anillos</b> del suelo — caminar a ese punto</li>
    <li><b>W / S</b> o <b>flechas</b> — avanzar y retroceder</li>
    <li><b>rueda</b> — acercar la vista</li>
  </ul>
  <button id="enter">Entrar al café</button>
  <p class="nota">Renderizado real (Cycles) · solo planta baja.</p>
</div></div>
<div id="hint">Arrastra para mirar · toca los anillos para caminar</div>
<script>window.NAP = __NAPDATA__;</script>
<script>__BUNDLE__</script>
"""
html = html.replace('__NAPDATA__', json.dumps(nap)).replace('__BUNDLE__', bundle)
dst = '/home/user/modelo-2-italiano/docs/tour'
os.makedirs(dst, exist_ok=True)
out = os.path.join(dst, 'cafe_napoli_tour.html')
open(out, 'w').write(html)
print('HTML:', out, len(html) // 1024, 'KB')
