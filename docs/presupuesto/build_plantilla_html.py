# Plantilla rellenable en el navegador, con el mismo diseno del presupuesto.
# Se escribe encima de los campos marcados y se imprime con Ctrl+P -> PDF.
import os, re

SP = os.path.dirname(os.path.abspath(__file__))
base = open(os.path.join(SP, 'presupuesto.html')).read()

# --------------------------------------------------- campos rellenables
def campo(txt, ancho=None):
    est = f' style="min-width:{ancho}"' if ancho else ''
    return f'<span class="campo-edit" contenteditable="true"{est}>{txt}</span>'

REEMPLAZOS = [
    ('<p class="sub">Reforma y ambientación de local comercial</p>',
     f'<p class="sub">{campo("[Reforma y ambientación de local comercial]")}</p>'),
    ('Presupuesto n.º <b>F26082502</b> &nbsp;·&nbsp; 29 de agosto de 2026',
     f'Presupuesto n.º <b>{campo("[F00000000]", "10ch")}</b> &nbsp;·&nbsp; '
     f'{campo("[00 de mes de 0000]", "18ch")}'),
    ("""<p><strong>Reforma y ambientación de la tienda, según diseño.</strong>
    Café Napoli — Ciudad de la Justicia, Málaga.</p>""",
     f'<p><strong>{campo("[Reforma y ambientación del local, según diseño.]")}</strong> '
     f'{campo("[Nombre del establecimiento] — [dirección], [ciudad].")}</p>'),
    ('<span class="cifra">27.000,00 €</span>',
     f'<span class="cifra">{campo("[00.000,00 €]", "11ch")}</span>'),
    ('<strong style="color:var(--tinta)">45 días</strong>',
     f'<strong style="color:var(--tinta)">{campo("[00 días]", "8ch")}</strong>'),
    ('la base imponible de 27.000,00 €, IVA aparte.',
     f'la base imponible indicada, IVA aparte.'),
    ('<span>Presupuesto F26082502 · Café Napoli, Málaga</span>',
     '<span>Grupo SUMA · presupuesto de obra</span>'),
]
for viejo, nuevo in REEMPLAZOS:
    assert viejo in base, viejo[:50]
    base = base.replace(viejo, nuevo, 1)

# las vistas de referencia son fotos de un proyecto concreto: fuera de la plantilla
import re as _re
base, n = _re.subn(r'\n\s*<div class="vistas">.*?</div>\n\s*</div>\n',
                   '\n', base, flags=_re.S)
assert n == 1, f'bloque de vistas no encontrado ({n})'

# capitulos, no incluidos y tabla de pagos: bloques editables enteros
base = base.replace('<div class="caps">', '<div class="caps" contenteditable="true">', 1)
base = base.replace('<div class="rot">Materiales y elementos no incluidos</div>\n      <ul>',
                    '<div class="rot">Materiales y elementos no incluidos</div>\n      <ul contenteditable="true">', 1)
base = base.replace('<tbody>', '<tbody contenteditable="true">', 1)
for viejo_imp in ('8.100,00 €', '5.400,00 €', '2.700,00 €'):
    base = base.replace(viejo_imp, '[0.000,00 €]')
for viejo_fec in ('31 de agosto', '11 de septiembre', '18 de septiembre', '2 de octubre'):
    base = base.replace(viejo_fec, '[fecha]')

# --------------------------------------------------- estilos y ayudas
extra = '''
<style>
  /* --- solo en pantalla: marcan donde se escribe ------------------- */
  @media screen {
    body { background:#EFECE6; padding:8mm 0 20mm; }
    .hoja { background:#fff; width:210mm; min-height:297mm; margin:0 auto 8mm;
      padding:14mm 16mm 12mm; box-shadow:0 2mm 8mm rgba(0,0,0,.16); }
    .campo-edit, [contenteditable="true"] { outline:none; }
    .campo-edit { background:#FFF8E1; border-bottom:1px dashed #C9A227;
      display:inline-block; min-width:4ch; }
    .caps[contenteditable], ul[contenteditable], tbody[contenteditable] {
      background:#FFFCF2; outline:1px dashed #DCC98A; outline-offset:3mm; }
    .campo-edit:focus, [contenteditable]:focus { background:#FFF3C4; }
    .ayuda { position:fixed; left:0; right:0; top:0; z-index:99;
      background:#1B2733; color:#EDE7DA; font:13px/1.5 Arial, sans-serif;
      padding:9px 16px; display:flex; justify-content:space-between;
      align-items:center; gap:16px; }
    .ayuda b { color:#F0C24B; }
    .ayuda button { font:inherit; background:#E3000F; color:#fff; border:0;
      border-radius:3px; padding:6px 14px; cursor:pointer; }
    .ayuda button.sec { background:transparent; border:1px solid #6B7681; }
    body { padding-top:56px; }
  }
  /* --- al imprimir: ni rastro de las marcas ------------------------ */
  @media print {
    .ayuda { display:none !important; }
    .campo-edit { background:none !important; border-bottom:none !important; }
    [contenteditable] { outline:none !important; background:none !important; }
  }
</style>
<div class="ayuda">
  <span>Escribe encima de los <b>campos marcados</b>. Puedes añadir o borrar
    líneas dentro de los bloques con recuadro. Lo que escribas se guarda solo
    en este navegador.</span>
  <span style="display:flex;gap:8px;white-space:nowrap">
    <button onclick="window.print()">Guardar como PDF</button>
    <button class="sec" onclick="if(confirm('¿Volver a la plantilla vacía?'))
      { localStorage.removeItem('napoli_presu'); location.reload(); }">Empezar de cero</button>
  </span>
</div>
<script>
(function () {
  'use strict';
  var CLAVE = 'napoli_presu';
  var zonas = document.querySelectorAll('[contenteditable="true"]');
  try {
    var guardado = JSON.parse(localStorage.getItem(CLAVE) || 'null');
    if (guardado && guardado.length === zonas.length) {
      zonas.forEach(function (z, i) { z.innerHTML = guardado[i]; });
    }
  } catch (e) { /* navegador sin almacenamiento: se sigue sin recuperar */ }
  function guardar() {
    try {
      localStorage.setItem(CLAVE, JSON.stringify(
        Array.prototype.map.call(zonas, function (z) { return z.innerHTML; })));
    } catch (e) { /* sin espacio o en privado: no se guarda, no pasa nada */ }
  }
  zonas.forEach(function (z) { z.addEventListener('input', guardar); });
})();
</script>
'''
base = base.replace('</body>', extra + '</body>', 1)
base = base.replace('<title>Presupuesto F26082502</title>',
                    '<title>Plantilla de presupuesto · Grupo SUMA</title>', 1)

out = os.path.join(SP, 'Plantilla_Presupuesto_GrupoSUMA.html')
open(out, 'w').write(base)
print('plantilla html:', out, len(base) // 1024, 'KB')
