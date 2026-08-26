# Ensambla la landing del Cafe Napoli: galeria de renders + recorrido 360.
import json, os

SP = os.path.dirname(os.path.abspath(__file__))
imgs = json.load(open(f'{SP}/imgs.json'))
tour_json = open(f'{SP}/tour_str.json').read().replace('</', '<\\/')

GALERIA = [
    ('f_entrada', 'Desde la entrada', 'La barra de listones azul Napoli, las cartas y la cocina vista a través de la mampara.', 'ancha'),
    ('f_barra', 'Barra y estantería', 'Vitrinas curvas de obrador y el botellero retroiluminado tras la cafetera.', ''),
    ('f_vitrinas', 'Vitrinas de cristal curvo', 'Bollería sobre blondas con sus etiquetas de precio y el carro de panes al fondo.', ''),
    ('f_escaparate', 'Hacia el ventanal', 'El ventanal corrido abre la sala a la calle: aceras de losetas, árboles y los edificios de enfrente.', ''),
    ('f_escaparate2', 'Mesa junto al ventanal', 'El sol de la tarde entra por el soportal hasta la mesa del té.', ''),
    ('f_mampara', 'Cocina a la vista', 'La mampara de vidrio de borde negro deja ver la campana, los fuegos y la barra de utensilios.', ''),
    ('f_suroeste', 'La doble altura', 'La sala completa desde el rincón suroeste: pilar central, escalera con barandilla de cristal y planta alta.', 'ancha'),
]

tarjetas = []
for i, (key, titulo, texto, clase) in enumerate(GALERIA):
    tarjetas.append(f'''
      <figure class="tarjeta {clase}" data-idx="{i}" tabindex="0" role="button"
              aria-label="Ampliar: {titulo}">
        <img src="data:image/jpeg;base64,{imgs[key]}" alt="{titulo}" loading="lazy">
        <figcaption><strong>{titulo}</strong><span>{texto}</span></figcaption>
      </figure>''')
tarjetas_html = '\n'.join(tarjetas)

html = '''<title>Café Napoli Málaga</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Archivo:wght@400;500;600;700&display=swap">
<style>
  :root{
    /* Paleta provisional del proyecto — se sustituira por la de Grupo Suma */
    --brand:#3E6B99; --brand-hover:#33587F; --brand-tinta:#24405C;
    --oro:#C69E54;
    --papel:#FAF8F4; --superficie:#FFFFFF; --piedra:#EDE8DE;
    --tinta:#23262B; --tinta-suave:#5A5F66; --linea:#DDD6C9;
    --pizarra:#141A21; --pizarra-texto:#EDEBE4; --pizarra-suave:#97A4B4;
    --sombra:0 18px 50px rgba(20,26,33,.14);
  }
  :root:not([data-theme="light"]){ color-scheme: light dark; }
  @media (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
      --brand:#7CA6D2; --brand-hover:#94B9DF; --brand-tinta:#B9D2E9;
      --oro:#D6B26E;
      --papel:#14181E; --superficie:#1B2129; --piedra:#232B35;
      --tinta:#ECEDE9; --tinta-suave:#A7ADB5; --linea:#313A45;
      --pizarra:#0D1116; --pizarra-texto:#EDEBE4; --pizarra-suave:#8B98A8;
      --sombra:0 18px 50px rgba(0,0,0,.5);
    }
  }
  :root[data-theme="dark"]{
    --brand:#7CA6D2; --brand-hover:#94B9DF; --brand-tinta:#B9D2E9;
    --oro:#D6B26E;
    --papel:#14181E; --superficie:#1B2129; --piedra:#232B35;
    --tinta:#ECEDE9; --tinta-suave:#A7ADB5; --linea:#313A45;
    --pizarra:#0D1116; --pizarra-texto:#EDEBE4; --pizarra-suave:#8B98A8;
    --sombra:0 18px 50px rgba(0,0,0,.5);
  }
  *{box-sizing:border-box;margin:0}
  html{scroll-behavior:smooth}
  @media (prefers-reduced-motion: reduce){ html{scroll-behavior:auto} }
  body{
    background:var(--papel); color:var(--tinta);
    font-family:'Archivo',system-ui,-apple-system,'Segoe UI',sans-serif;
    line-height:1.55; -webkit-font-smoothing:antialiased;
  }
  .cuerpo{max-width:1180px;margin:0 auto;padding:0 clamp(18px,4vw,44px)}
  .ojal{
    font-size:12.5px;font-weight:600;letter-spacing:.24em;text-transform:uppercase;
    color:var(--brand);display:flex;align-items:center;gap:14px;
  }
  .ojal::after{content:"";height:1px;width:52px;background:var(--oro)}
  h1,h2{font-family:'Fraunces','Georgia',serif;text-wrap:balance;color:var(--tinta)}

  /* ------------------------------------------------------------- hero */
  .hero{position:relative;min-height:min(88vh,880px);display:flex;align-items:flex-end;
    background:var(--pizarra);overflow:hidden}
  .hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
    object-position:center 40%}
  .hero::after{content:"";position:absolute;inset:0;
    background:linear-gradient(180deg,rgba(20,26,33,.18) 0%,rgba(20,26,33,.06) 38%,rgba(20,26,33,.82) 100%)}
  .hero-texto{position:relative;z-index:2;width:100%;padding:clamp(28px,5vw,64px) 0}
  .hero-texto .ojal{color:#EDD9AC}
  .hero-texto .ojal::after{background:#EDD9AC}
  .hero h1{font-size:clamp(46px,8.5vw,104px);font-weight:600;line-height:1.02;
    color:#FDFCF9;margin:14px 0 10px;letter-spacing:-.01em}
  .hero p{max-width:52ch;color:#D9DDE2;font-size:clamp(15px,1.6vw,18px)}
  .hero-cta{display:flex;gap:14px;flex-wrap:wrap;margin-top:26px}
  .boton{
    display:inline-flex;align-items:center;gap:10px;
    font:600 15px/1 'Archivo',sans-serif;letter-spacing:.02em;
    padding:14px 26px;border-radius:4px;border:1px solid transparent;
    text-decoration:none;cursor:pointer;transition:background .18s,border-color .18s;
  }
  .boton:focus-visible{outline:2px solid var(--oro);outline-offset:3px}
  .boton-lleno{background:var(--brand);color:#fff}
  .boton-lleno:hover{background:var(--brand-hover)}
  .boton-borde{border-color:rgba(253,252,249,.55);color:#FDFCF9;background:rgba(20,26,33,.25)}
  .boton-borde:hover{border-color:#fff;background:rgba(20,26,33,.45)}

  /* ------------------------------------------------------------- ficha */
  .ficha{border-bottom:1px solid var(--linea)}
  .ficha-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
    gap:1px;background:var(--linea);border-left:1px solid var(--linea);
    border-right:1px solid var(--linea)}
  .dato{background:var(--papel);padding:26px 22px}
  .dato b{display:block;font-family:'Fraunces',serif;font-weight:600;
    font-size:clamp(26px,3vw,34px);color:var(--brand-tinta);
    font-variant-numeric:tabular-nums}
  .dato span{font-size:13.5px;color:var(--tinta-suave);letter-spacing:.04em}

  /* ------------------------------------------------------------- secciones */
  section{padding:clamp(52px,8vw,96px) 0}
  .cabecera-seccion{display:flex;flex-direction:column;gap:14px;margin-bottom:38px}
  .cabecera-seccion h2{font-size:clamp(30px,4.4vw,46px);font-weight:600}
  .cabecera-seccion p{max-width:62ch;color:var(--tinta-suave)}

  /* ------------------------------------------------------------- galeria */
  .galeria{display:grid;gap:clamp(14px,2vw,24px);grid-template-columns:1fr 1fr}
  .tarjeta{position:relative;overflow:hidden;border-radius:6px;cursor:zoom-in;
    box-shadow:var(--sombra);background:var(--pizarra)}
  .tarjeta.ancha{grid-column:1 / -1}
  .tarjeta img{display:block;width:100%;height:100%;object-fit:cover;
    aspect-ratio:16/9;transition:transform .5s ease, opacity .4s}
  @media (prefers-reduced-motion: no-preference){
    .tarjeta:hover img{transform:scale(1.025)}
  }
  .tarjeta:focus-visible{outline:3px solid var(--brand);outline-offset:3px}
  .tarjeta figcaption{position:absolute;inset:auto 0 0 0;padding:40px 20px 16px;
    background:linear-gradient(180deg,transparent,rgba(20,26,33,.78));
    color:#F4F2EC;display:flex;flex-direction:column;gap:2px}
  .tarjeta figcaption strong{font-family:'Fraunces',serif;font-weight:600;font-size:17px}
  .tarjeta figcaption span{font-size:13px;color:#CBD2D9;max-width:70ch}
  @media (max-width:720px){ .galeria{grid-template-columns:1fr} }

  /* ------------------------------------------------------------- visor */
  .visor{position:fixed;inset:0;background:rgba(13,17,22,.94);z-index:60;
    display:none;align-items:center;justify-content:center;flex-direction:column;gap:12px;
    padding:4vh 4vw}
  .visor.abierto{display:flex}
  .visor img{max-width:96vw;max-height:82vh;border-radius:4px;
    box-shadow:0 30px 80px rgba(0,0,0,.6)}
  .visor .pie{color:#E8E6DF;font-size:14.5px;text-align:center;max-width:80ch}
  .visor .pie strong{font-family:'Fraunces',serif;font-size:17px;display:block}
  .visor-nav{position:fixed;top:50%;transform:translateY(-50%);border:0;cursor:pointer;
    background:rgba(250,248,244,.12);color:#fff;font-size:26px;line-height:1;
    width:52px;height:52px;border-radius:50%;display:grid;place-items:center}
  .visor-nav:hover{background:rgba(250,248,244,.25)}
  .visor-nav.izq{left:18px}.visor-nav.der{right:18px}
  .visor-cerrar{position:fixed;top:18px;right:18px;border:0;cursor:pointer;
    background:rgba(250,248,244,.12);color:#fff;font-size:22px;width:46px;height:46px;
    border-radius:50%}
  .visor-cerrar:hover{background:rgba(250,248,244,.25)}

  /* ------------------------------------------------------------- recorrido */
  .banda-recorrido{background:var(--pizarra);color:var(--pizarra-texto)}
  .banda-recorrido .ojal{color:var(--oro)}
  .banda-recorrido h2{color:var(--pizarra-texto)}
  .banda-recorrido .cabecera-seccion p{color:var(--pizarra-suave)}
  .marco-tour{position:relative;border-radius:8px;overflow:hidden;
    aspect-ratio:16/9;background:#000;box-shadow:0 26px 70px rgba(0,0,0,.45)}
  .marco-tour.fullscreen{aspect-ratio:auto}
  .marco-tour iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
  .poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
    filter:brightness(.72)}
  .capa-poster{position:absolute;inset:0;display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:18px;z-index:2}
  .boton-play{display:inline-flex;align-items:center;gap:12px;cursor:pointer;
    background:var(--brand);border:0;color:#fff;font:600 17px 'Archivo',sans-serif;
    padding:18px 34px;border-radius:999px;box-shadow:0 14px 40px rgba(0,0,0,.4)}
  .boton-play:hover{background:var(--brand-hover)}
  .boton-play svg{width:16px;height:16px;fill:currentColor}
  .capa-poster small{color:#D5DAE0;font-size:13.5px;letter-spacing:.06em}
  .barra-tour{display:flex;justify-content:space-between;align-items:center;
    gap:14px;margin-top:16px;flex-wrap:wrap}
  .barra-tour .ayuda{font-size:13.5px;color:var(--pizarra-suave)}
  .boton-full{background:transparent;border:1px solid var(--pizarra-suave);
    color:var(--pizarra-texto);border-radius:4px;padding:11px 20px;cursor:pointer;
    font:600 14px 'Archivo',sans-serif;display:none;align-items:center;gap:9px}
  .boton-full:hover{border-color:var(--pizarra-texto)}
  .boton-full svg{width:14px;height:14px;fill:currentColor}

  footer{background:var(--pizarra);color:var(--pizarra-suave);
    border-top:1px solid rgba(151,164,180,.2)}
  footer .cuerpo{display:flex;justify-content:space-between;gap:18px;
    flex-wrap:wrap;padding-top:30px;padding-bottom:34px;font-size:13.5px}
  footer b{color:var(--pizarra-texto);font-weight:600}

  .aparece{opacity:0;transform:translateY(18px);
    transition:opacity .7s ease,transform .7s ease}
  .aparece.visto{opacity:1;transform:none}
  @media (prefers-reduced-motion: reduce){
    .aparece{opacity:1;transform:none;transition:none}
    .tarjeta img{transition:none}
  }
</style>

<header class="hero">
  <img src="data:image/jpeg;base64,__HERO__" alt="La sala del Café Napoli al atardecer, vista desde la entrada">
  <div class="cuerpo hero-texto">
    <p class="ojal">Grupo Suma · Proyecto de interiorismo</p>
    <h1>Café Napoli</h1>
    <p>Reforma integral de la planta baja de un local en Málaga: barra de obrador con vitrinas curvas, cocina a la vista y un ventanal corrido abierto a la calle. Visualización fotorrealista y recorrido virtual del proyecto.</p>
    <div class="hero-cta">
      <a class="boton boton-lleno" href="#galeria">Ver la galería</a>
      <a class="boton boton-borde" href="#recorrido">Recorrido virtual 360°</a>
    </div>
  </div>
</header>

<div class="ficha">
  <div class="cuerpo" style="padding-top:34px;padding-bottom:34px">
    <div class="ficha-grid">
      <div class="dato"><b>74,20 m²</b><span>Superficie útil de planta baja</span></div>
      <div class="dato"><b>5,50 m</b><span>Doble altura en la entrada</span></div>
      <div class="dato"><b>5,5 m</b><span>Ventanal corrido a la calle</span></div>
      <div class="dato"><b>8 puntos</b><span>Recorrido virtual 360°</span></div>
    </div>
  </div>
</div>

<section id="galeria">
  <div class="cuerpo">
    <div class="cabecera-seccion aparece">
      <p class="ojal">Galería del proyecto</p>
      <h2>Siete miradas a la planta baja</h2>
      <p>Renders fotorrealistas del modelo definitivo: materiales reales, luz de tarde malagueña y el local funcionando. Toca cualquier imagen para ampliarla.</p>
    </div>
    <div class="galeria">
__TARJETAS__
    </div>
  </div>
</section>

<section class="banda-recorrido" id="recorrido">
  <div class="cuerpo">
    <div class="cabecera-seccion aparece">
      <p class="ojal">Recorrido virtual</p>
      <h2>Camina por el café</h2>
      <p>Ocho posiciones renderizadas en 360°: entrada, sala, barra, cocina y hasta el pasillo de servicio. Arrastra para mirar, toca los anillos del suelo o usa W/S para caminar — y ponlo a pantalla completa.</p>
    </div>
    <div class="marco-tour aparece" id="marcoTour">
      <img class="poster" src="data:image/jpeg;base64,__POSTER__" alt="">
      <div class="capa-poster" id="capaPoster">
        <button class="boton-play" id="botonPlay">
          <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 1.8v12.4L14 8z"/></svg>
          Iniciar el recorrido
        </button>
        <small>Se carga al momento · funciona con ratón, teclado y táctil</small>
      </div>
    </div>
    <div class="barra-tour">
      <span class="ayuda">Arrastra para mirar · anillos del suelo o W/S para caminar · rueda para acercar · solo planta baja</span>
      <button class="boton-full" id="botonFull">
        <svg viewBox="0 0 14 14" aria-hidden="true"><path d="M1 5V1h4v1.6H2.6V5H1zm8-4h4v4h-1.6V2.6H9V1zM1 9h1.6v2.4H5V13H1V9zm11.4 0H14v4h-4v-1.6h2.4V9z"/></svg>
        Pantalla completa
      </button>
    </div>
  </div>
</section>

<footer>
  <div class="cuerpo">
    <span><b>Café Napoli</b> · Málaga — proyecto de reforma e interiorismo</span>
    <span>Grupo Suma · Visualización 3D fotorrealista</span>
  </div>
</footer>

<div class="visor" id="visor" role="dialog" aria-modal="true" aria-label="Imagen ampliada">
  <button class="visor-cerrar" id="visorCerrar" aria-label="Cerrar">✕</button>
  <button class="visor-nav izq" id="visorPrev" aria-label="Anterior">‹</button>
  <img id="visorImg" src="" alt="">
  <div class="pie"><strong id="visorTitulo"></strong><span id="visorTexto"></span></div>
  <button class="visor-nav der" id="visorNext" aria-label="Siguiente">›</button>
</div>

<script id="datosTour" type="application/json">__TOURJSON__</script>
<script>
(function(){
  'use strict';
  // aparición al hacer scroll
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('visto'); io.unobserve(e.target); } });
  }, {threshold:.12});
  document.querySelectorAll('.aparece').forEach(function(el){ io.observe(el); });

  // visor de la galería
  var tarjetas = Array.prototype.slice.call(document.querySelectorAll('.tarjeta'));
  var visor = document.getElementById('visor');
  var vImg = document.getElementById('visorImg');
  var vTit = document.getElementById('visorTitulo');
  var vTxt = document.getElementById('visorTexto');
  var actual = 0;
  function abrir(i){
    actual = (i + tarjetas.length) % tarjetas.length;
    var t = tarjetas[actual];
    vImg.src = t.querySelector('img').src;
    vTit.textContent = t.querySelector('strong').textContent;
    vTxt.textContent = t.querySelector('span').textContent;
    visor.classList.add('abierto');
  }
  function cerrar(){ visor.classList.remove('abierto'); }
  tarjetas.forEach(function(t, i){
    t.addEventListener('click', function(){ abrir(i); });
    t.addEventListener('keydown', function(e){
      if(e.key==='Enter'||e.key===' '){ e.preventDefault(); abrir(i); }
    });
  });
  document.getElementById('visorCerrar').addEventListener('click', cerrar);
  document.getElementById('visorPrev').addEventListener('click', function(){ abrir(actual-1); });
  document.getElementById('visorNext').addEventListener('click', function(){ abrir(actual+1); });
  visor.addEventListener('click', function(e){ if(e.target===visor) cerrar(); });
  addEventListener('keydown', function(e){
    if(!visor.classList.contains('abierto')) return;
    if(e.key==='Escape') cerrar();
    if(e.key==='ArrowLeft') abrir(actual-1);
    if(e.key==='ArrowRight') abrir(actual+1);
  });

  // recorrido 360: se monta al pulsar, pantalla completa opcional
  var marco = document.getElementById('marcoTour');
  var capa = document.getElementById('capaPoster');
  var botonFull = document.getElementById('botonFull');
  var iframeTour = null;
  document.getElementById('botonPlay').addEventListener('click', function(){
    if(iframeTour) return;
    var html = JSON.parse(document.getElementById('datosTour').textContent);
    iframeTour = document.createElement('iframe');
    iframeTour.setAttribute('title', 'Recorrido virtual Café Napoli');
    iframeTour.setAttribute('allowfullscreen', '');
    iframeTour.srcdoc = html;
    marco.appendChild(iframeTour);
    capa.style.display = 'none';
    marco.querySelector('.poster').style.display = 'none';
    botonFull.style.display = 'inline-flex';
  });
  botonFull.addEventListener('click', function(){
    if(document.fullscreenElement){ document.exitFullscreen(); return; }
    (marco.requestFullscreen || marco.webkitRequestFullscreen || function(){}).call(marco);
  });
  document.addEventListener('fullscreenchange', function(){
    var dentro = document.fullscreenElement === marco;
    marco.classList.toggle('fullscreen', dentro);
    botonFull.innerHTML = dentro
      ? '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M5 1v4H1V3.4h2.4V1H5zm8 2.4V5H9V1h1.6v2.4H13zM1 9h4v4H3.4v-2.4H1V9zm12 1.6h-2.4V13H9V9h4v1.6z"/></svg> Salir de pantalla completa'
      : '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M1 5V1h4v1.6H2.6V5H1zm8-4h4v4h-1.6V2.6H9V1zM1 9h1.6v2.4H5V13H1V9zm11.4 0H14v4h-4v-1.6h2.4V9z"></path></svg> Pantalla completa';
  });
})();
</script>
'''

html = html.replace('__HERO__', imgs['f_entrada'])
html = html.replace('__POSTER__', imgs['f_barra'])
html = html.replace('__TARJETAS__', tarjetas_html)
html = html.replace('__TOURJSON__', tour_json)
dst = '/home/user/modelo-2-italiano/docs/web'
os.makedirs(dst, exist_ok=True)
out = os.path.join(dst, 'cafe_napoli_landing.html')
open(out, 'w').write(html)
print('landing:', out, len(html) // 1024, 'KB')
