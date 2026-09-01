# Informe de reforma F26052703 con el sistema grafico del presupuesto:
# membrete de tinta, rotulos rojos, capitulos numerados. Texto literal
# del informe original; solo cambia la forma.
import base64, json, os

SP   = os.path.dirname(os.path.abspath(__file__))
logo = json.load(open(f'{SP}/logo.json'))
img1 = base64.b64encode(open(f'{SP}/info1.jpeg', 'rb').read()).decode()
img2 = base64.b64encode(open(f'{SP}/info2.jpeg', 'rb').read()).decode()

DATOS = [
    ('Empresa ejecutora', 'Grupo SUMA'),
    ('Domicilio social', 'Calle Eduardo de Palacio 14, 4.º piso B2, Málaga (España)'),
    ('Teléfono de contacto', '+34 680 75 74 91'),
    ('Correo electrónico', 'sebastian@gruposuma.eu'),
    ('N.º de referencia', 'F26052703'),
    ('Fecha de emisión', '31 de agosto de 2026'),
    ('Emplazamiento de la obra', 'Tienda — Calle Madre de Dios 22, Distrito Centro, Málaga'),
]

CAPITULOS = [
    ('01', 'Actuaciones previas', [
        'Limpieza del local y retirada de las luminarias existentes.',
        'Contratación de cuba para acopio de materiales y evacuación de escombros.']),
    ('02', 'Albañilería', [
        'Preparación de la pared para su alicatado en la zona de horno.',
        'Alicatado conforme al diseño aprobado.',
        'Demolición de los bancos de material existentes.',
        'Saneamiento de paredes.',
        'Pintura de paredes.',
        'Pintura del mueble de estanterías de la cocina.',
        'Revestimiento de la barra.',
        'Pintura de techos.',
        'Retirada de la falsa ventana, emparejamiento del paramento y pintura.',
        'Pintura exterior conforme al color establecido por la normativa aplicable.',
        'Pintura de las aberturas externas.']),
    ('03', 'Carpintería', [
        'Suministro y colocación de suelo de tarima de alto tránsito, de uso comercial, en salón y baño.',
        'Colocación de rodapiés.',
        'Ejecución de barras de madera en las zonas definidas en el diseño.']),
    ('04', 'Fontanería y saneamiento', [
        'Revisión de tuberías y desagües.']),
    ('05', 'Electricidad', [
        'Revisión de los circuitos existentes.',
        'Colocación de iluminación LED en la barra.',
        'Colocación de luminaria en techo.',
        'Ejecución de cableado oculto para luminarias.',
        'Ampliación de tomas de corriente en la zona de pizzería y modificaciones en la zona de cocina.']),
]

PRESTACIONES = [
    'Materiales necesarios para la ejecución de las partidas descritas.',
    'Mano de obra.', 'Seguimiento de obra.', 'Coordinación de obra.',
]

PIE1 = ('Infografía 1. Zona de horno y barra: revestimiento de azulejo blanco tipo '
        'metro, pilar de ladrillo visto, zócalo de listones en azul y blanco, suelo '
        'de tarima de madera e iluminación de apliques y colgantes.')
PIE2 = ('Infografía 2. Salón principal: distribución de mesas y barras perimetrales '
        'con taburetes, mobiliario blanco de estilo bistró, pilares de ladrillo '
        'visto e iluminación combinada de techo y pared.')

def bloque_cap(num, tit, items):
    lis = ''.join(f'<li>{x}</li>' for x in items)
    return (f'<section class="cap"><h3><span class="cnum">{num}</span>{tit}</h3>'
            f'<ul>{lis}</ul></section>')

caps_izq = ''.join(bloque_cap(*c) for c in CAPITULOS[:2])
caps_der = ''.join(bloque_cap(*c) for c in CAPITULOS[2:])
datos = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in DATOS)
prest = ''.join(f'<li>{x}</li>' for x in PRESTACIONES)

def membrete_con(detalle):
    return f'''<div class="membrete">
    <img src="data:image/png;base64,{logo}" alt="Grupo SUMA">
    <div class="emisor"><b>GRUPO SUMA</b><br>{detalle}</div>
  </div>'''

membrete  = membrete_con('Calle Eduardo de Palacio 14, 4.º piso B2 · Málaga, España<br>'
                         '+34 680 75 74 91 · sebastian@gruposuma.eu')
membrete2 = membrete_con('Informe de reforma · Ref. F26052703 · 31·08·2026')

html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Informe de reforma F26052703</title>
<style>
  @page {{ size: A4; margin: 14mm 16mm 12mm; }}
  :root {{
    --tinta:#1B2733; --suave:#5A6472; --tenue:#8A929B;
    --linea:#D7D2C8; --linea-f:#EDEAE3; --rojo:#E3000F; --fondo:#F7F5F1;
  }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{ font-family:'Liberation Sans', Arial, sans-serif; color:var(--tinta);
    font-size:8.8pt; line-height:1.47;
    -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  h1,h2,h3 {{ font-family:'Bitstream Charter', Charter, Georgia, serif; font-weight:700; }}
  .hoja {{ page-break-after:always; }}
  .hoja:last-child {{ page-break-after:auto; }}
  .membrete {{ display:flex; justify-content:space-between; align-items:flex-end;
    padding-bottom:3mm; border-bottom:1.6pt solid var(--tinta); }}
  .membrete img {{ height:9mm; }}
  .emisor {{ text-align:right; font-size:7.2pt; color:var(--suave); line-height:1.5; }}
  .emisor b {{ color:var(--tinta); font-size:7.6pt; letter-spacing:.04em; }}
  .titulo {{ margin-top:6mm; }}
  .titulo h1 {{ font-size:21pt; line-height:1.12; letter-spacing:-.01em; }}
  .titulo .sub {{ margin-top:1.5mm; font-size:10.4pt; color:var(--suave); }}
  .refline {{ margin-top:2.5mm; font-size:9pt; color:var(--suave); letter-spacing:.02em; }}
  .refline b {{ color:var(--tinta); letter-spacing:.04em; }}
  .rot {{ font-size:7.8pt; letter-spacing:.16em; text-transform:uppercase;
    color:var(--rojo); font-weight:700; margin-bottom:2mm;
    padding-bottom:1.2mm; border-bottom:.6pt solid var(--linea); }}
  .bloque {{ margin-top:5mm; }}

  .datos {{ display:grid; grid-template-columns:auto 1fr; gap:1.1mm 6mm; margin:0; }}
  .datos dt {{ font-size:6.8pt; letter-spacing:.09em; text-transform:uppercase;
    color:var(--tenue); align-self:baseline; padding-top:.4mm; }}
  .datos dd {{ margin:0; }}
  .datos dd b {{ letter-spacing:.02em; }}

  .objeto p {{ font-family:'Bitstream Charter', Charter, Georgia, serif;
    font-size:10.6pt; line-height:1.5; }}

  .caps {{ margin-top:3mm; display:grid; grid-template-columns:1fr 1fr;
    gap:0 8mm; align-items:start; }}
  .caps > div {{ min-width:0; }}
  .cap {{ break-inside:avoid; margin-bottom:3.6mm; }}
  .cap h3 {{ font-size:9.4pt; display:flex; align-items:baseline; gap:2mm;
    padding-bottom:1mm; border-bottom:.6pt solid var(--linea-f); margin-bottom:1.4mm; }}
  .cnum {{ font-family:'Liberation Sans',Arial,sans-serif; font-size:7.4pt;
    color:#fff; background:var(--tinta); padding:.5mm 1.4mm; border-radius:1pt;
    letter-spacing:.04em; }}
  .cap ul {{ margin:0; padding-left:3.4mm; list-style:none; }}
  .cap li {{ position:relative; margin-bottom:.8mm; color:var(--suave); }}
  .cap li::before {{ content:"—"; position:absolute; left:-3.4mm; color:var(--linea); }}

  .dos {{ display:grid; grid-template-columns:1fr 1fr; gap:8mm; margin-top:4mm; }}
  .incluye {{ background:var(--fondo); border-left:1.6pt solid var(--rojo);
    padding:2.6mm 3.4mm; color:var(--suave); }}
  .incluye ul {{ margin:0; padding-left:3.4mm; list-style:none; }}
  .incluye li {{ position:relative; margin-bottom:.6mm; }}
  .incluye li::before {{ content:"—"; position:absolute; left:-3.4mm; color:var(--linea); }}

  .figura {{ width:80%; margin:2mm auto 0; }}
  .figura img {{ width:100%; display:block; border:.5pt solid var(--linea); }}
  .figura figcaption {{ font-size:7.2pt; color:var(--tenue); margin-top:1.2mm;
    line-height:1.45; }}
  .figura figcaption b {{ color:var(--suave); }}
  .cierre {{ margin-top:2.6mm; font-family:'Bitstream Charter',Charter,Georgia,serif;
    font-size:9.6pt; color:var(--suave); font-style:italic; }}

  footer {{ margin-top:4mm; padding-top:2.4mm; border-top:.6pt solid var(--linea);
    display:flex; justify-content:space-between; font-size:6.6pt;
    color:var(--tenue); letter-spacing:.04em; }}
</style></head><body>

<!-- ============================ HOJA 1 ============================ -->
<div class="hoja">
  {membrete}
  <div class="titulo">
    <h1>Informe de reforma</h1>
    <p class="sub">Local comercial destinado a pizzería-bar — Calle Madre de Dios 22,
      Distrito Centro, Málaga</p>
    <p class="refline">Referencia <b>F26052703</b> &nbsp;·&nbsp; Málaga, a 31 de agosto de 2026</p>
  </div>

  <div class="bloque">
    <div class="rot">1 · Datos identificativos</div>
    <dl class="datos">{datos}</dl>
  </div>

  <div class="bloque objeto">
    <div class="rot">2 · Objeto del informe</div>
    <p>El presente documento tiene por objeto informar del alcance de los trabajos
    que se ejecutarán en la <strong>reforma y ambientación integral del local
    comercial destinado a pizzería-bar</strong>, situado en Calle Madre de Dios 22
    (Distrito Centro, Málaga), conforme al diseño elaborado específicamente para
    dicha finalidad.</p>
  </div>

  <div class="bloque">
    <div class="rot">3 · Alcance de los trabajos</div>
    <p style="color:var(--suave)">Las actuaciones previstas se estructuran en cinco
    capítulos, que se detallan a continuación.</p>
    <div class="caps">
      <div>{caps_izq}</div>
      <div>{caps_der}</div>
    </div>
  </div>

  <footer>
    <span>Informe de reforma · Ref. F26052703</span>
    <span>Página 1 de 2</span>
  </footer>
</div>

<!-- ============================ HOJA 2 ============================ -->
<div class="hoja">
  {membrete2}

  <div class="dos">
    <div>
      <div class="rot">4 · Prestaciones incluidas en la ejecución</div>
      <div class="incluye">
        <p style="margin-bottom:1.4mm"><strong style="color:var(--tinta)">La ejecución
        de la obra comprende los siguientes conceptos:</strong></p>
        <ul>{prest}</ul>
      </div>
    </div>
    <div>
      <div class="rot">5 · Plazo de ejecución</div>
      <p style="color:var(--suave)">El tiempo de ejecución estimado para la totalidad
      de los trabajos descritos es de aproximadamente
      <strong style="color:var(--tinta)">30 días</strong>.</p>
    </div>
  </div>

  <div class="bloque">
    <div class="rot">6 · Documentación gráfica</div>
    <p style="color:var(--suave)">Se adjuntan las infografías del proyecto, que
    reflejan el resultado previsto de la reforma y ambientación del local.</p>
    <figure class="figura">
      <img src="data:image/jpeg;base64,{img1}" alt="Infografía 1">
      <figcaption><b>Infografía 1.</b> {PIE1[13:]}</figcaption>
    </figure>
    <figure class="figura">
      <img src="data:image/jpeg;base64,{img2}" alt="Infografía 2">
      <figcaption><b>Infografía 2.</b> {PIE2[13:]}</figcaption>
    </figure>
    <p class="cierre">El presente informe recoge las actuaciones previstas por
    Grupo SUMA para la reforma del local descrito, con carácter meramente
    informativo.</p>
  </div>

  <footer>
    <span>Grupo SUMA · Calle Eduardo de Palacio 14, 4.º B2 · Málaga · +34 680 75 74 91</span>
    <span>Página 2 de 2</span>
  </footer>
</div>
</body></html>
'''
open(f'{SP}/informe.html', 'w').write(html)
print('html:', len(html)//1024, 'KB')
