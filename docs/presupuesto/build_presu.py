# Presupuesto y contrato de obra de Grupo SUMA, en dos hojas A4.
# Todo el contenido economico y de alcance procede del presupuesto original
# F26082502; aqui solo se reordena y se le da forma de documento firmable.
import json, os

SP = os.path.dirname(os.path.abspath(__file__))
logo = json.load(open(f'{SP}/logo.json'))
vistas = json.load(open(f'{SP}/vistas.json'))

# La cuenta, el DNI y la rubrica escaneada no se versionan: viven en
# privado.json, que queda fuera de git. Sin ese fichero el documento se
# genera igual, con la cuenta y las firmas en blanco para rellenar a mano.
CAMPOS_FIRMA = ['Nombre y apellidos', 'DNI / NIF', 'Lugar y fecha']
EN_BLANCO = {
    'banco': [['Banco', '[entidad]'], ['Titular', '[titular de la cuenta]'],
              ['IBAN', '[ES00 0000 0000 0000 0000 0000]'], ['SWIFT', '[XXXXXXXXXXX]']],
    'contratista': [], 'firma': None,
}
ruta_privado = f'{SP}/privado.json'
privado = (json.load(open(ruta_privado, encoding='utf-8'))
           if os.path.exists(ruta_privado) else EN_BLANCO)
BANCO, firma = privado['banco'], privado.get('firma')

CAPITULOS = [
    ('01', 'Actuaciones previas', [
        'Limpieza y retiro de luminarias',
        'Retiro de cartelería existente en frente',
        'Contratación de cuba para materiales y escombros',
        'Andamio para trabajo en altura']),
    ('02', 'Albañilería', [
        'Preparación de pared para pintura',
        'Saneamiento de paredes',
        'Pintura del mueble de estanterías detrás de barra',
        'Reparación y pintura de techos',
        'Pintura exterior según color de normativa',
        'Pintura de aberturas externas']),
    ('03', 'Carpintería', [
        'Suelo de tarima de alto tránsito de uso comercial en salones y escalera',
        'Rodapiés',
        'Palillería en columnas',
        'Adecuación de barra a nueva zona',
        'Revestimiento en barra',
        'Mampara separadora de cristal templado para cocina']),
    ('04', 'Fontanería y saneamiento', [
        'Revisión de tuberías y desagües']),
    ('05', 'Baños', [
        'Cambio de lavabos, griferías y mueble',
        'Pintura general']),
    ('06', 'Electricidad', [
        'Revisión de circuitos',
        'Adecuación de enchufes',
        'Colocación de led en barra',
        'Colocación de luminaria en techo',
        'Colocación de luz en escalera']),
]

NO_INCLUIDO = [
    'Revestimiento de acero inoxidable en paredes de cocina (ya solicitado)',
    'Mesas', 'Sillones', 'Sillas', 'Taburetes',
    'Elementos decorativos', 'Luminarias colgantes', 'Neveras',
    'Muebles, biblioteca',
    'Mobiliario y demás equipos de funcionamiento de cocina',
]

PAGOS = [
    ('30 %', '8.100,00 €', 'A la aceptación de la oferta y comienzo', '31 de agosto'),
    ('20 %', '5.400,00 €', 'Por avance de obra', '11 de septiembre'),
    ('20 %', '5.400,00 €', 'Por avance de obra', '18 de septiembre'),
    ('20 %', '5.400,00 €', 'Por avance de obra', '2 de octubre'),
    ('10 %', '2.700,00 €', 'A la entrega final', 'Fin de obra'),
]

def bloque_cap(num, tit, items):
    lis = ''.join(f'<li>{x}</li>' for x in items)
    return f'''<section class="cap">
      <h3><span class="cnum">{num}</span>{tit}</h3>
      <ul>{lis}</ul>
    </section>'''

# Se reparten a mano para dejar el hueco de la columna derecha libre
# para las vistas de referencia.
caps_izq = ''.join(bloque_cap(*c) for c in CAPITULOS[:3])
caps_der = ''.join(bloque_cap(*c) for c in CAPITULOS[3:])

vistas_html = ''.join(
    f'<figure><img src="data:image/jpeg;base64,{v["d"]}" alt="{v["t"]}">'
    f'<figcaption>{v["t"]}</figcaption></figure>' for v in vistas)

no_inc = ''.join(f'<li>{x}</li>' for x in NO_INCLUIDO)

banco = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in BANCO)

def campos(datos=None):
    """Los tres campos de un recuadro de firma, con valor o en blanco."""
    val = dict(datos or [])
    filas = []
    for i, lab in enumerate(CAMPOS_FIRMA):
        dato = ' dato' if i else ''
        v = val.get(lab, '')
        v = f'<span class="val">{v}</span>' if v else ''
        filas.append(f'<div class="campo{dato}"><div class="lab">{lab}</div>'
                     f'<div class="raya">{v}</div></div>')
    return ''.join(filas)

rubrica_suma = (f'<img class="rub" src="data:image/png;base64,{firma}" alt="Firma">'
                if firma else '')

pagos = ''.join(
    f'<tr><td class="pct">{p}</td><td class="imp">{i}</td>'
    f'<td>{c}</td><td class="fec">{f}</td></tr>'
    for p, i, c, f in PAGOS)

html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Presupuesto F26082502</title>
<style>
  @page {{ size: A4; margin: 14mm 16mm 12mm; }}
  :root {{
    --tinta:#1B2733; --suave:#5A6472; --tenue:#8A929B;
    --linea:#D7D2C8; --linea-f:#EDEAE3; --rojo:#E3000F; --fondo:#F7F5F1;
  }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{
    font-family:'Liberation Sans', Arial, sans-serif;
    color:var(--tinta); font-size:8.8pt; line-height:1.47;
    -webkit-print-color-adjust:exact; print-color-adjust:exact;
  }}
  h1,h2,h3 {{ font-family:'Bitstream Charter', Charter, Georgia, serif; font-weight:700; }}
  .hoja {{ page-break-after:always; }}
  .hoja:last-child {{ page-break-after:auto; }}

  /* ---------------------------------------------------------- membrete */
  .membrete {{ display:flex; justify-content:space-between; align-items:flex-end;
    padding-bottom:3mm; border-bottom:1.6pt solid var(--tinta); }}
  .membrete img {{ height:9mm; }}
  .emisor {{ text-align:right; font-size:7.2pt; color:var(--suave); line-height:1.5; }}
  .emisor b {{ color:var(--tinta); font-size:7.6pt; letter-spacing:.04em; }}

  /* ------------------------------------------------------------ titulo */
  .titulo {{ margin-top:6mm; display:flex; justify-content:space-between;
    align-items:flex-start; gap:8mm; }}
  .titulo h1 {{ font-size:21pt; line-height:1.12; letter-spacing:-.01em; }}
  .titulo .sub {{ margin-top:1.5mm; font-size:10.4pt; color:var(--suave); }}
  .refline {{ margin-top:2.5mm; font-size:9pt; color:var(--suave);
    letter-spacing:.02em; }}
  .refline b {{ color:var(--tinta); letter-spacing:.04em; }}
  /* ------------------------------------------------------------ bloques */
  .rot {{ font-size:7.8pt; letter-spacing:.16em; text-transform:uppercase;
    color:var(--rojo); font-weight:700; margin-bottom:2mm;
    padding-bottom:1.2mm; border-bottom:.6pt solid var(--linea); }}
  .objeto {{ margin-top:5mm; }}
  .objeto p {{ font-family:'Bitstream Charter', Charter, Georgia, serif;
    font-size:11.5pt; line-height:1.5; }}

  .caps {{ margin-top:5mm; display:grid; grid-template-columns:1fr 1fr;
    gap:0 8mm; align-items:start; }}
  .caps > div {{ min-width:0; }}
  .cap {{ break-inside:avoid; margin-bottom:3.8mm; }}
  .cap h3 {{ font-size:9.4pt; display:flex; align-items:baseline; gap:2mm;
    padding-bottom:1mm; border-bottom:.6pt solid var(--linea-f); margin-bottom:1.4mm; }}
  .cnum {{ font-family:'Liberation Sans',Arial,sans-serif; font-size:7.4pt;
    color:#fff; background:var(--tinta); padding:.5mm 1.4mm; border-radius:1pt;
    letter-spacing:.04em; }}
  .cap ul {{ margin:0; padding-left:3.4mm; list-style:none; }}
  .cap li {{ position:relative; margin-bottom:.8mm; color:var(--suave); }}
  .cap li::before {{ content:"—"; position:absolute; left:-3.4mm;
    color:var(--linea); }}

  /* --------------------------------------------- vistas de referencia */
  .vistas {{ margin-top:5mm; break-inside:avoid; }}
  .vistas .rejilla {{ display:grid; grid-template-columns:1fr 1fr; gap:2.6mm; }}
  .vistas figure {{ margin:0; }}
  .vistas img {{ width:100%; display:block; aspect-ratio:16/9;
    object-fit:cover; border:.5pt solid var(--linea); }}
  .vistas figcaption {{ font-size:6.4pt; color:var(--tenue); margin-top:.9mm;
    letter-spacing:.03em; }}

  /* ---------------------------------------------------------- economico */
  .dos {{ display:grid; grid-template-columns:1fr 1fr; gap:8mm; margin-top:5mm; }}
  .noinc ul {{ margin:0; padding-left:3.4mm; list-style:none; column-count:2;
    column-gap:5mm; }}
  .noinc li {{ position:relative; margin-bottom:.5mm; color:var(--suave);
    break-inside:avoid; }}
  .noinc li::before {{ content:"×"; position:absolute; left:-3.4mm;
    color:var(--linea); }}
  .incluye {{ background:var(--fondo); border-left:1.6pt solid var(--rojo);
    padding:2.6mm 3.4mm; margin-top:3mm; color:var(--suave); }}

  .importe {{ border:.6pt solid var(--tinta); margin-top:4mm; }}
  .importe .fila {{ display:flex; justify-content:space-between;
    align-items:baseline; padding:3mm 4mm; }}
  .importe .fila + .fila {{ border-top:.6pt solid var(--linea); }}
  .importe .et {{ font-size:7pt; letter-spacing:.12em; text-transform:uppercase;
    color:var(--tenue); }}
  .importe .cifra {{ font-family:'Bitstream Charter',Charter,Georgia,serif;
    font-size:15pt; font-weight:700; font-variant-numeric:tabular-nums; }}
  .importe .nota {{ font-size:7.4pt; color:var(--suave); }}

  table.pagos {{ width:100%; border-collapse:collapse; margin-top:3mm; }}
  table.pagos th {{ font-size:6.6pt; letter-spacing:.1em; text-transform:uppercase;
    color:var(--tenue); text-align:left; font-weight:700;
    border-bottom:.6pt solid var(--linea); padding:0 2mm 1.2mm 0; }}
  table.pagos td {{ padding:1.5mm 2mm 1.5mm 0; border-bottom:.5pt solid var(--linea-f);
    color:var(--suave); vertical-align:baseline; }}
  table.pagos .pct {{ font-weight:700; color:var(--tinta); width:11mm; }}
  table.pagos .imp {{ font-weight:700; color:var(--tinta); width:22mm;
    font-variant-numeric:tabular-nums; }}
  table.pagos .fec {{ text-align:right; white-space:nowrap; }}

  /* ------------------------------------------------------ datos banco */
  .banco {{ margin-top:5mm; }}
  .banco dl {{ margin:0; display:grid; grid-template-columns:auto 1fr;
    gap:1.2mm 3.4mm; }}
  .banco dt {{ font-size:6.6pt; letter-spacing:.08em; text-transform:uppercase;
    color:var(--tenue); align-self:center; }}
  .banco dd {{ margin:0; color:var(--tinta); font-variant-numeric:tabular-nums;
    letter-spacing:.01em; }}

  /* ------------------------------------------------------------ firmas */
  .conformidad {{ margin-top:5mm; }}
  .conformidad p {{ color:var(--suave); max-width:none; }}
  .firmas {{ display:grid; grid-template-columns:1fr 1fr; gap:10mm; margin-top:5mm; }}
  .firma {{ border:.6pt solid var(--linea); padding:3mm 4mm 2.6mm; }}
  .firma h4 {{ font-family:'Bitstream Charter',Charter,Georgia,serif;
    font-size:9pt; margin-bottom:1mm; }}
  .firma .rolet {{ font-size:6.6pt; letter-spacing:.1em; text-transform:uppercase;
    color:var(--tenue); margin-bottom:3mm; }}
  .campo {{ margin-bottom:2.8mm; }}
  .campo .lab {{ font-size:6.6pt; letter-spacing:.08em; text-transform:uppercase;
    color:var(--tenue); }}
  .campo .raya {{ border-bottom:.6pt solid var(--tinta); height:4.2mm;
    display:flex; align-items:flex-end; }}
  .campo.dato .raya {{ border-bottom-style:dotted; }}
  .campo .val {{ font-size:9pt; line-height:1.1; padding-bottom:.5mm;
    white-space:nowrap; }}
  .rubrica {{ height:14mm; border-bottom:.6pt solid var(--tinta);
    display:flex; align-items:flex-end; justify-content:center; }}
  .rubrica .rub {{ height:12.5mm; width:auto; display:block;
    margin-bottom:.5mm; }}
  .rubrica-lab {{ font-size:6.6pt; letter-spacing:.08em; text-transform:uppercase;
    color:var(--tenue); margin-top:1mm; }}

  footer {{ margin-top:6mm; padding-top:2.4mm; border-top:.6pt solid var(--linea);
    display:flex; justify-content:space-between; font-size:6.6pt;
    color:var(--tenue); letter-spacing:.04em; }}
</style></head><body>

<!-- ============================ HOJA 1 ============================ -->
<div class="hoja">
  <div class="membrete">
    <img src="data:image/png;base64,{logo}" alt="Grupo SUMA">
    <div class="emisor">
      <b>GRUPO SUMA</b><br>
      Calle Eduardo de Palacio 14, 4.º piso B2 · Málaga, España<br>
      +34 680 75 74 91 · sebastian@gruposuma.eu
    </div>
  </div>

  <div class="titulo">
    <div>
      <h1>Presupuesto y contrato de obra</h1>
      <p class="sub">Reforma y ambientación de local comercial</p>
      <p class="refline">Presupuesto n.º <b>F26082502</b> &nbsp;·&nbsp; 29 de agosto de 2026</p>
    </div>
  </div>

  <div class="objeto">
    <div class="rot">Objeto del contrato</div>
    <p><strong>Reforma y ambientación de la tienda, según diseño.</strong>
    Café Napoli — Ciudad de la Justicia, Málaga.</p>
  </div>

  <div style="margin-top:5mm">
    <div class="rot">Trabajos incluidos en la cotización</div>
    <div class="caps">
      <div>{caps_izq}</div>
      <div>{caps_der}
        <div class="vistas">
          <div class="rot">Vistas de referencia</div>
          <div class="rejilla">{vistas_html}</div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    <span>Presupuesto F26082502 · Café Napoli, Málaga</span>
    <span>Página 1 de 2</span>
  </footer>
</div>

<!-- ============================ HOJA 2 ============================ -->
<div class="hoja">
  <div class="membrete">
    <img src="data:image/png;base64,{logo}" alt="Grupo SUMA">
    <div class="emisor">
      <b>GRUPO SUMA</b><br>
      Presupuesto F26082502 · 29·08·2026
    </div>
  </div>

  <div class="dos">
    <div>
      <div class="rot">Alcance económico</div>
      <div class="incluye" style="margin-top:0">
        <strong>Incluido:</strong> los materiales, la mano de obra, el seguimiento
        y la coordinación de obra están incluidos en el presupuesto.
      </div>
      <div class="importe">
        <div class="fila">
          <span class="et">Importe total</span>
          <span class="cifra">27.000,00 €</span>
        </div>
        <div class="fila">
          <span class="nota">IVA no incluido; se aplicará el vigente al facturar.</span>
        </div>
      </div>
      <div style="margin-top:5mm">
        <div class="rot">Plazo de ejecución</div>
        <p style="color:var(--suave)">Tiempo de ejecución aproximado de
        <strong style="color:var(--tinta)">45 días</strong> desde el comienzo de
        los trabajos.</p>
      </div>
    </div>

    <div>
      <div class="noinc">
        <div class="rot">Materiales y elementos no incluidos</div>
        <ul>{no_inc}</ul>
      </div>
      <div class="banco">
        <div class="rot">Datos bancarios</div>
        <dl>{banco}</dl>
      </div>
    </div>
  </div>

  <div style="margin-top:5mm">
    <div class="rot">Calendario de pagos</div>
    <table class="pagos">
      <thead><tr><th>%</th><th>Importe</th><th>Concepto</th><th style="text-align:right">Fecha</th></tr></thead>
      <tbody>{pagos}</tbody>
    </table>
    <p style="font-size:6.8pt;color:var(--tenue);margin-top:1.6mm">
      Importes calculados sobre la base imponible de 27.000,00 €, IVA aparte.</p>
  </div>

  <div class="conformidad">
    <div class="rot">Conformidad y aceptación</div>
    <p>Las partes que suscriben manifiestan su conformidad con el alcance de los
    trabajos, el importe, el calendario de pagos y el plazo de ejecución
    recogidos en el presente documento, que firman por duplicado y a un solo
    efecto en el lugar y la fecha indicados.</p>

    <div class="firmas">
      <div class="firma">
        <h4>Grupo SUMA</h4>
        <div class="rolet">La empresa contratista</div>
        {campos(privado['contratista'])}
        <div class="rubrica">{rubrica_suma}</div>
        <div class="rubrica-lab">Firma</div>
      </div>
      <div class="firma">
        <h4>La propiedad</h4>
        <div class="rolet">El cliente</div>
        {campos()}
        <div class="rubrica"></div>
        <div class="rubrica-lab">Firma</div>
      </div>
    </div>
  </div>

  <footer>
    <span>Grupo SUMA · Calle Eduardo de Palacio 14, 4.º B2 · Málaga · +34 680 75 74 91</span>
    <span>Página 2 de 2</span>
  </footer>
</div>
</body></html>
'''

out = os.path.join(SP, 'presupuesto.html')
open(out, 'w').write(html)
print('html:', out, len(html) // 1024, 'KB')
