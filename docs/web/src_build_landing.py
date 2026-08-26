# Ensambla la landing del Cafe Napoli — rediseno "cuaderno de obra":
# pagina oscura cinematografica (carbon con sesgo del azul Napoli de la barra),
# tipografia Marcellus / Hanken Grotesk / IBM Plex Mono (voz de plano tecnico),
# galeria editorial V.01–V.07, cinta panoramica 360 en movimiento y cajetin.
import base64, json, os

SP = os.path.dirname(os.path.abspath(__file__))
imgs = json.load(open(f'{SP}/imgs.json'))
tour_json = open(f'{SP}/tour_str.json').read().replace('</', '<\\/')
tira = base64.b64encode(open(f'{SP}/tira_pano.jpg', 'rb').read()).decode()

GALERIA = [
    ('f_entrada',    'V.01', 'La entrada',            'Los árboles del soportal, el pilar de listones y la barra encendida al fondo.', 'llena'),
    ('f_escaparate', 'V.02', 'Hacia la calle',        'El ventanal corrido abre la sala a la acera, los árboles y los edificios de enfrente.', 'par'),
    ('f_escaparate2','V.03', 'Mesa junto al ventanal','La luz de la tarde entra por el soportal hasta la mesa del té.', 'par'),
    ('f_barra',      'V.04', 'La barra',              'Frente de listones azul Napoli, vitrinas curvas de obrador y botellero retroiluminado.', 'llena'),
    ('f_vitrinas',   'V.05', 'Vitrinas de obrador',   'Bollería sobre blondas, etiquetas de precio y el carro de panes al fondo.', 'par'),
    ('f_mampara',    'V.06', 'Cocina a la vista',     'La mampara de vidrio deja ver la campana, los fuegos y la barra de utensilios.', 'par'),
    ('f_suroeste',   'V.07', 'La doble altura',       'La sala completa: pilar central, escalera con barandilla de cristal y planta alta.', 'llena'),
]

PARADAS = ['Entrada', 'Ventanal', 'Sala', 'Mampara', 'Barra', 'Escalera', 'Tras la barra', 'Cocina']

tarjetas = []
for i, (k, cod, tit, txt, clase) in enumerate(GALERIA):
    tarjetas.append(f'''
      <figure class="tarjeta {clase} aparece" data-idx="{i}" tabindex="0" role="button"
              aria-label="Ampliar {cod} — {tit}">
        <img src="data:image/jpeg;base64,{imgs[k]}" alt="{tit}" loading="lazy">
        <figcaption>
          <span class="codigo">{cod}</span>
          <span class="pie"><strong>{tit}</strong><span>{txt}</span></span>
        </figcaption>
      </figure>''')
tarjetas_html = '\n'.join(tarjetas)

paradas_html = '\n'.join(
    f'      <li><span class="num">{i+1:02d}</span>{n}</li>' for i, n in enumerate(PARADAS))

html = '''<title>Café Napoli Málaga</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus&family=Hanken+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  /* Paleta derivada de los materiales del proyecto (azul de la barra, laton
     de las lamparas, marfil de los muros). Pendiente de sustituir por la de
     Grupo Suma cuando el cliente facilite sus codigos. Diseno dark-first. */
  :root{
    --fondo:#0F161C; --fondo2:#151E26; --panel:#1A242E;
    --texto:#EDE7DA; --texto2:#9FAAB1;
    --napoli:#33627E; --napoli-claro:#7FB0CB;
    --laton:#C29A5B; --laton-claro:#D9B87E;
    --linea:rgba(237,231,218,.16); --linea-suave:rgba(237,231,218,.08);
    --sombra:0 24px 70px rgba(0,0,0,.5);
  }
  @media (prefers-color-scheme: light){
    :root:not([data-theme="dark"]){
      --fondo:#F2EEE6; --fondo2:#E9E3D7; --panel:#FBF9F4;
      --texto:#1D262E; --texto2:#5C6870;
      --napoli:#2F5D77; --napoli-claro:#2F5D77;
      --laton:#9A7434; --laton-claro:#8A6527;
      --linea:rgba(29,38,46,.2); --linea-suave:rgba(29,38,46,.1);
      --sombra:0 24px 60px rgba(29,38,46,.14);
    }
  }
  :root[data-theme="light"]{
    --fondo:#F2EEE6; --fondo2:#E9E3D7; --panel:#FBF9F4;
    --texto:#1D262E; --texto2:#5C6870;
    --napoli:#2F5D77; --napoli-claro:#2F5D77;
    --laton:#9A7434; --laton-claro:#8A6527;
    --linea:rgba(29,38,46,.2); --linea-suave:rgba(29,38,46,.1);
    --sombra:0 24px 60px rgba(29,38,46,.14);
  }

  *{box-sizing:border-box;margin:0}
  html{scroll-behavior:smooth}
  @media (prefers-reduced-motion: reduce){ html{scroll-behavior:auto} }
  body{
    background:var(--fondo); color:var(--texto);
    font-family:'Hanken Grotesk',system-ui,-apple-system,'Segoe UI',sans-serif;
    line-height:1.6; -webkit-font-smoothing:antialiased;
  }
  img{max-width:100%}
  ::selection{background:var(--laton);color:#10151B}
  :focus-visible{outline:2px solid var(--laton);outline-offset:3px}
  h1,h2{font-family:'Marcellus','Georgia',serif;font-weight:400;text-wrap:balance;color:var(--texto)}
  .mono{font-family:'IBM Plex Mono',ui-monospace,monospace}
  .cuerpo{max-width:1240px;margin:0 auto;padding:0 clamp(20px,4.5vw,48px)}
  [id]{scroll-margin-top:76px}

  /* ------------------------------------------------------------ nav */
  .barra-nav{
    position:fixed;top:0;left:0;right:0;z-index:50;
    display:flex;justify-content:space-between;align-items:center;gap:20px;
    padding:15px clamp(18px,4vw,40px);
    border-bottom:1px solid var(--linea-suave);
    background:var(--fondo);
    background:color-mix(in srgb, var(--fondo) 80%, transparent);
    backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
  }
  .marca{font-family:'Marcellus',serif;font-size:16px;letter-spacing:.24em;
    color:var(--texto);text-decoration:none;white-space:nowrap}
  .barra-nav ul{display:flex;gap:clamp(16px,3vw,34px);list-style:none;padding:0}
  .barra-nav ul a{font-family:'IBM Plex Mono',monospace;font-size:11.5px;
    letter-spacing:.18em;text-transform:uppercase;text-decoration:none;
    color:var(--texto2);transition:color .2s}
  .barra-nav ul a:hover{color:var(--texto)}
  .barra-nav ul a.activo{color:var(--laton-claro)}
  @media (max-width:680px){ .barra-nav ul{display:none} }

  /* ------------------------------------------------------------ hero */
  .hero{position:relative;min-height:100svh;display:flex;align-items:flex-end;
    overflow:hidden;background:var(--fondo2)}
  .hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
    object-position:center 42%}
  .hero::after{content:"";position:absolute;inset:0;background:
    linear-gradient(78deg,rgba(10,14,18,.68) 0%,rgba(10,14,18,.3) 32%,rgba(10,14,18,0) 58%),
    linear-gradient(180deg,rgba(10,14,18,.55) 0%,rgba(10,14,18,.08) 30%,
                    rgba(10,14,18,.18) 62%,rgba(10,14,18,.9) 100%)}
  .hero-texto{position:relative;z-index:2;width:100%;
    padding-top:clamp(90px,12vh,140px)}
  .ojal{font-family:'IBM Plex Mono',monospace;font-size:11.5px;letter-spacing:.3em;
    text-transform:uppercase;color:var(--laton-claro);
    display:flex;align-items:center;gap:14px}
  .ojal::before{content:"";width:30px;height:1px;background:var(--laton)}
  .hero .ojal{color:#E8C688;text-shadow:0 1px 14px rgba(10,14,18,.9),0 0 3px rgba(10,14,18,.6)}
  .hero .ojal::before{background:#E8C688;box-shadow:0 1px 8px rgba(10,14,18,.8)}
  .hero h1{font-size:clamp(58px,11vw,148px);line-height:.98;letter-spacing:.045em;
    text-transform:uppercase;color:#F5F1E6;margin:20px 0 14px;
    text-shadow:0 3px 30px rgba(10,14,18,.6)}
  .hero .dek{max-width:52ch;color:#DEDBD0;font-size:clamp(15.5px,1.7vw,19px);
    text-shadow:0 1px 12px rgba(10,14,18,.7)}
  .hero-cta{display:flex;gap:14px;flex-wrap:wrap;margin:30px 0 46px}
  .boton{display:inline-flex;align-items:center;gap:10px;
    font:600 14.5px/1 'Hanken Grotesk',sans-serif;letter-spacing:.03em;
    padding:15px 28px;border-radius:2px;border:1px solid transparent;
    text-decoration:none;cursor:pointer;transition:background .2s,border-color .2s,color .2s}
  .boton-lleno{background:var(--napoli);color:#F5F1E6}
  .boton-lleno:hover{background:var(--laton);color:#10151B}
  .boton-borde{border-color:rgba(242,237,226,.5);color:#F2EDE2;background:rgba(13,20,26,.28)}
  .boton-borde:hover{border-color:#F2EDE2;background:rgba(13,20,26,.5)}
  .hero-meta{border-top:1px solid rgba(242,237,226,.22);
    display:flex;flex-wrap:wrap;gap:10px 34px;padding:18px 0 26px;
    font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;
    text-transform:uppercase;color:#CFCBC0}

  /* ------------------------------------------------------------ secciones */
  section{padding:clamp(76px,11vw,150px) 0}
  .cabeza{display:flex;flex-direction:column;gap:16px;
    margin-bottom:clamp(34px,5vw,58px)}
  .cabeza h2{font-size:clamp(34px,5vw,58px);letter-spacing:.02em}
  .cabeza p{max-width:64ch;color:var(--texto2)}

  .manifiesto{display:grid;grid-template-columns:1.25fr .9fr;
    gap:clamp(28px,5vw,72px);align-items:start}
  .manifiesto .grande{font-size:clamp(19px,2.4vw,26px);line-height:1.5;
    color:var(--texto);text-wrap:pretty}
  .manifiesto .apoyo{display:flex;flex-direction:column;gap:18px;
    color:var(--texto2);font-size:15.5px}
  @media (max-width:820px){ .manifiesto{grid-template-columns:1fr} }

  /* ------------------------------------------------------------ galeria */
  .galeria{display:grid;grid-template-columns:1fr 1fr;
    gap:clamp(26px,4vw,52px) clamp(16px,2.5vw,30px)}
  .tarjeta{margin:0;display:flex;flex-direction:column;cursor:zoom-in;border-radius:2px}
  .tarjeta.llena{grid-column:1 / -1}
  .tarjeta img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;
    border-radius:2px;background:var(--fondo2);transition:filter .4s}
  .tarjeta:hover img{filter:brightness(1.07)}
  .tarjeta figcaption{display:grid;grid-template-columns:auto 1fr;gap:16px;
    border-top:1px solid var(--linea);margin-top:14px;padding-top:12px}
  .codigo{font-family:'IBM Plex Mono',monospace;font-size:12px;
    color:var(--laton-claro);letter-spacing:.08em;padding-top:2px}
  .tarjeta .pie{display:flex;flex-direction:column;gap:2px}
  .tarjeta .pie strong{font-weight:600;font-size:15.5px}
  .tarjeta .pie span{font-size:13.5px;color:var(--texto2);max-width:72ch}
  @media (max-width:720px){ .galeria{grid-template-columns:1fr} }

  /* ------------------------------------------------------------ visor */
  .visor{position:fixed;inset:0;background:rgba(8,12,16,.95);z-index:60;
    display:none;align-items:center;justify-content:center;flex-direction:column;
    gap:14px;padding:4vh 4vw}
  .visor.abierto{display:flex}
  .visor img{max-width:92vw;max-height:76vh;border-radius:2px;
    box-shadow:0 30px 90px rgba(0,0,0,.65)}
  .visor .pie-visor{display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;
    justify-content:center;max-width:88vw;color:#E8E6DF;font-size:14px}
  .visor .pie-visor .codigo{color:#D9B87E}
  .visor .pie-visor strong{font-weight:600;font-size:15.5px;color:#F2EFE8}
  .visor .pie-visor span.txt{color:#AEB8BF}
  .visor .pie-visor .cuenta{font-family:'IBM Plex Mono',monospace;font-size:12px;
    color:#8B98A3;letter-spacing:.12em}
  .visor-nav{position:fixed;top:50%;transform:translateY(-50%);cursor:pointer;
    background:transparent;border:1px solid rgba(242,237,226,.35);color:#F2EDE2;
    font-size:24px;line-height:1;width:50px;height:50px;border-radius:50%;
    display:grid;place-items:center;transition:background .2s,border-color .2s}
  .visor-nav:hover{background:rgba(242,237,226,.14);border-color:#F2EDE2}
  .visor-nav.izq{left:18px}.visor-nav.der{right:18px}
  .visor-cerrar{position:fixed;top:18px;right:18px;cursor:pointer;
    background:transparent;border:1px solid rgba(242,237,226,.35);color:#F2EDE2;
    font-size:20px;width:46px;height:46px;border-radius:50%;
    transition:background .2s,border-color .2s}
  .visor-cerrar:hover{background:rgba(242,237,226,.14);border-color:#F2EDE2}

  /* ------------------------------------------------------------ recorrido */
  .escenario{background:#0D141A;color:#EDE7DA;
    border-top:1px solid rgba(237,231,218,.08);
    border-bottom:1px solid rgba(237,231,218,.08)}
  .escenario .cabeza h2{color:#EDE7DA}
  .escenario .cabeza p{color:#9FB0BC}
  .cinta{height:clamp(120px,20vw,220px);overflow:hidden;position:relative;
    margin-bottom:14px}
  .rollo{display:flex;height:100%;width:max-content;
    animation:rodar 75s linear infinite}
  .rollo img{height:100%;width:auto;max-width:none;display:block;
    filter:saturate(.92) brightness(.94)}
  @keyframes rodar{to{transform:translateX(-50%)}}
  .cinta::before,.cinta::after{content:"";position:absolute;top:0;bottom:0;
    width:12%;z-index:2;pointer-events:none}
  .cinta::before{left:0;background:linear-gradient(90deg,#0D141A,transparent)}
  .cinta::after{right:0;background:linear-gradient(270deg,#0D141A,transparent)}
  .pie-cinta{font-family:'IBM Plex Mono',monospace;font-size:10.5px;
    letter-spacing:.24em;text-transform:uppercase;color:#7C8B96;
    margin:0 0 clamp(40px,6vw,64px);text-align:right}
  @media (prefers-reduced-motion: reduce){ .rollo{animation:none} }

  .paradas{display:flex;flex-wrap:wrap;gap:12px 30px;list-style:none;
    padding:0;margin:0 0 clamp(30px,4vw,48px)}
  .paradas li{display:flex;gap:10px;align-items:baseline;font-size:14.5px;color:#C8CFD4}
  .paradas .num{font-family:'IBM Plex Mono',monospace;font-size:11.5px;
    color:#D9B87E;letter-spacing:.06em}

  .marco-tour{position:relative;aspect-ratio:16/9;background:#000;overflow:hidden;
    border:1px solid rgba(237,231,218,.16);border-radius:3px;
    box-shadow:0 30px 80px rgba(0,0,0,.5)}
  .marco-tour.fullscreen{aspect-ratio:auto}
  .marco-tour iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
  .poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
    filter:brightness(.6) saturate(.92)}
  .capa-poster{position:absolute;inset:0;display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:18px;z-index:2}
  .boton-play{display:flex;flex-direction:column;align-items:center;gap:16px;
    background:none;border:0;cursor:pointer;color:#F2EDE2}
  .boton-play .aro{width:88px;height:88px;border-radius:50%;
    border:1px solid rgba(242,237,226,.7);display:grid;place-items:center;
    background:rgba(13,20,26,.4);backdrop-filter:blur(4px);
    transition:background .25s,border-color .25s;transform:none}
  .boton-play svg{width:22px;height:22px;fill:#F2EDE2;transition:fill .25s;margin-left:4px}
  .boton-play:hover .aro{background:#C29A5B;border-color:#C29A5B}
  .boton-play:hover svg{fill:#10151B}
  .boton-play .rotulo{font-family:'IBM Plex Mono',monospace;font-size:11.5px;
    letter-spacing:.26em;text-transform:uppercase}
  .capa-poster small{color:#9FB0BC;font-size:12.5px;letter-spacing:.05em}
  .barra-tour{display:flex;justify-content:space-between;align-items:center;
    gap:14px;margin-top:16px;flex-wrap:wrap}
  .barra-tour .ayuda{font-size:13px;color:#8FA0AC}
  .boton-full{background:transparent;border:1px solid rgba(237,231,218,.35);
    color:#EDE7DA;border-radius:2px;padding:11px 20px;cursor:pointer;
    font:500 12px 'IBM Plex Mono',monospace;letter-spacing:.14em;
    text-transform:uppercase;display:none;align-items:center;gap:9px;
    transition:border-color .2s,background .2s}
  .boton-full:hover{border-color:#EDE7DA;background:rgba(237,231,218,.08)}
  .boton-full svg{width:13px;height:13px;fill:currentColor}

  /* ------------------------------------------------------------ cajetin */
  .cajetin{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;
    background:var(--linea);border:1px solid var(--linea)}
  .celda{background:var(--fondo);padding:24px 26px;display:flex;
    flex-direction:column;gap:8px}
  .celda .etiqueta{font-family:'IBM Plex Mono',monospace;font-size:10.5px;
    letter-spacing:.22em;text-transform:uppercase;color:var(--texto2)}
  .celda .valor{font-weight:600;font-size:clamp(19px,2.2vw,25px);
    font-variant-numeric:tabular-nums;line-height:1.25}
  .celda .nota{font-size:13px;color:var(--texto2)}
  @media (max-width:860px){ .cajetin{grid-template-columns:1fr 1fr} }
  @media (max-width:560px){ .cajetin{grid-template-columns:1fr} }

  footer{border-top:1px solid var(--linea-suave)}
  footer .cuerpo{display:flex;justify-content:space-between;gap:14px;
    flex-wrap:wrap;padding-top:26px;padding-bottom:32px;
    font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.18em;
    text-transform:uppercase;color:var(--texto2)}

  .aparece{opacity:0;transform:translateY(16px);
    transition:opacity .8s ease,transform .8s ease}
  .aparece.visto{opacity:1;transform:none}
  @media (prefers-reduced-motion: reduce){
    .aparece{opacity:1;transform:none;transition:none}
    .tarjeta img{transition:none}
  }
</style>

<nav class="barra-nav" aria-label="Secciones">
  <a class="marca" href="#inicio">CAFÉ NAPOLI</a>
  <ul>
    <li><a href="#proyecto" data-sec="proyecto">Proyecto</a></li>
    <li><a href="#galeria" data-sec="galeria">Galería</a></li>
    <li><a href="#recorrido" data-sec="recorrido">Recorrido 360</a></li>
    <li><a href="#ficha" data-sec="ficha">Ficha</a></li>
  </ul>
</nav>

<header class="hero" id="inicio">
  <img src="data:image/jpeg;base64,__HERO__" alt="La sala del Café Napoli al atardecer, vista desde la entrada">
  <div class="cuerpo hero-texto">
    <p class="ojal">Grupo Suma · Reforma e interiorismo · Málaga</p>
    <h1>Café<br>Napoli</h1>
    <p class="dek">Un obrador italiano a pie de calle: barra de listones azul Napoli, cocina a la vista y cinco metros y medio de ventanal abiertos a la acera.</p>
    <div class="hero-cta">
      <a class="boton boton-lleno" href="#galeria">Ver los renders</a>
      <a class="boton boton-borde" href="#recorrido">Entrar al recorrido 360°</a>
    </div>
    <div class="hero-meta">
      <span>Planta baja · 74,20 m²</span>
      <span>Doble altura · 5,50 m</span>
      <span>Visualización · Cycles</span>
      <span>7 vistas + 8 paradas 360°</span>
    </div>
  </div>
</header>

<section id="proyecto">
  <div class="cuerpo">
    <div class="cabeza aparece">
      <p class="ojal">El proyecto</p>
      <h2>Reforma integral de la planta baja</h2>
    </div>
    <div class="manifiesto aparece">
      <p class="grande">El local se organiza alrededor de una barra de obrador con vitrinas curvas y un frente de listones en azul Napoli. La cocina queda a la vista tras una mampara de vidrio de canto negro, y un ventanal corrido de 5,5 metros convierte la acera en el cuarto muro de la sala.</p>
      <div class="apoyo">
        <p>La doble altura de la entrada ordena el espacio: el pilar central revestido de listones de madera, la escalera con barandilla de cristal y la galería de la planta alta enmarcan la sala sin dividirla.</p>
        <p>Todas las imágenes de esta página son renders fotorrealistas del modelo definitivo — materiales reales, luz de tarde malagueña y el local en funcionamiento.</p>
      </div>
    </div>
  </div>
</section>

<section id="galeria">
  <div class="cuerpo">
    <div class="cabeza aparece">
      <p class="ojal">Galería · siete vistas</p>
      <h2>El proyecto, vista a vista</h2>
      <p>Serie completa de la planta baja, numerada como el juego de láminas del proyecto. Toca cualquier imagen para verla a pantalla completa.</p>
    </div>
    <div class="galeria">
__TARJETAS__
    </div>
  </div>
</section>

<section class="escenario" id="recorrido">
  <div class="cinta" aria-hidden="true">
    <div class="rollo">
      <img src="data:image/jpeg;base64,__TIRA__" alt="">
      <img src="data:image/jpeg;base64,__TIRA__" alt="">
    </div>
  </div>
  <div class="cuerpo">
    <p class="pie-cinta">Panorámica equirectangular · posición 01 — entrada</p>
    <div class="cabeza aparece">
      <p class="ojal">Recorrido virtual</p>
      <h2>Camina por el café</h2>
      <p>Ocho posiciones renderizadas en 360°. Arrastra para mirar alrededor, toca los anillos del suelo o usa W/S para avanzar — y ponlo a pantalla completa.</p>
    </div>
    <ol class="paradas aparece">
__PARADAS__
    </ol>
    <div class="marco-tour aparece" id="marcoTour">
      <img class="poster" src="data:image/jpeg;base64,__POSTER__" alt="">
      <div class="capa-poster" id="capaPoster">
        <button class="boton-play" id="botonPlay">
          <span class="aro"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 1.8v12.4L14 8z"/></svg></span>
          <span class="rotulo">Iniciar el recorrido</span>
        </button>
        <small>Se carga al momento · ratón, teclado y táctil · solo planta baja</small>
      </div>
    </div>
    <div class="barra-tour">
      <span class="ayuda">Arrastra para mirar · anillos del suelo o W/S para caminar · rueda para acercar</span>
      <button class="boton-full" id="botonFull">
        <svg viewBox="0 0 14 14" aria-hidden="true"><path d="M1 5V1h4v1.6H2.6V5H1zm8-4h4v4h-1.6V2.6H9V1zM1 9h1.6v2.4H5V13H1V9zm11.4 0H14v4h-4v-1.6h2.4V9z"/></svg>
        Pantalla completa
      </button>
    </div>
  </div>
</section>

<section id="ficha">
  <div class="cuerpo">
    <div class="cabeza aparece">
      <p class="ojal">Ficha técnica</p>
      <h2>Datos del proyecto</h2>
    </div>
    <div class="cajetin aparece">
      <div class="celda"><span class="etiqueta">Proyecto</span><span class="valor">Café Napoli</span><span class="nota">Reforma integral e interiorismo</span></div>
      <div class="celda"><span class="etiqueta">Emplazamiento</span><span class="valor">Málaga</span><span class="nota">Local a pie de calle, con soportal</span></div>
      <div class="celda"><span class="etiqueta">Superficie útil</span><span class="valor">74,20 m²</span><span class="nota">Planta baja</span></div>
      <div class="celda"><span class="etiqueta">Altura libre</span><span class="valor">5,50 m</span><span class="nota">Doble altura en la entrada</span></div>
      <div class="celda"><span class="etiqueta">Ventanal</span><span class="valor">5,5 m</span><span class="nota">Frente acristalado corrido a la calle</span></div>
      <div class="celda"><span class="etiqueta">Visualización</span><span class="valor">7 + 8</span><span class="nota">Vistas fotorrealistas + paradas del recorrido 360°</span></div>
    </div>
  </div>
</section>

<footer>
  <div class="cuerpo">
    <span>Café Napoli — Málaga</span>
    <span>Grupo Suma · Visualización 3D</span>
  </div>
</footer>

<div class="visor" id="visor" role="dialog" aria-modal="true" aria-label="Imagen ampliada">
  <button class="visor-cerrar" id="visorCerrar" aria-label="Cerrar">✕</button>
  <button class="visor-nav izq" id="visorPrev" aria-label="Anterior">‹</button>
  <img id="visorImg" src="" alt="">
  <div class="pie-visor">
    <span class="codigo" id="visorCod"></span>
    <strong id="visorTitulo"></strong>
    <span class="txt" id="visorTexto"></span>
    <span class="cuenta" id="visorNum"></span>
  </div>
  <button class="visor-nav der" id="visorNext" aria-label="Siguiente">›</button>
</div>

<script id="datosTour" type="application/json">__TOURJSON__</script>
<script>
(function(){
  'use strict';
  // aparicion al hacer scroll
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('visto'); io.unobserve(e.target); } });
  }, {threshold:.12});
  document.querySelectorAll('.aparece').forEach(function(el){ io.observe(el); });

  // seccion activa en la navegacion
  var enlaces = {};
  document.querySelectorAll('.barra-nav a[data-sec]').forEach(function(a){
    enlaces[a.getAttribute('data-sec')] = a;
  });
  var ioNav = new IntersectionObserver(function(es){
    es.forEach(function(e){
      var a = enlaces[e.target.id];
      if(!a) return;
      if(e.isIntersecting){
        Object.keys(enlaces).forEach(function(k){ enlaces[k].classList.remove('activo'); });
        a.classList.add('activo');
      }
    });
  }, {rootMargin:'-38% 0px -55% 0px'});
  ['proyecto','galeria','recorrido','ficha'].forEach(function(id){
    var s = document.getElementById(id); if(s) ioNav.observe(s);
  });

  // visor de la galeria
  var tarjetas = Array.prototype.slice.call(document.querySelectorAll('.tarjeta'));
  var visor = document.getElementById('visor');
  var vImg = document.getElementById('visorImg');
  var vCod = document.getElementById('visorCod');
  var vTit = document.getElementById('visorTitulo');
  var vTxt = document.getElementById('visorTexto');
  var vNum = document.getElementById('visorNum');
  var actual = 0;
  function abrir(i){
    actual = (i + tarjetas.length) % tarjetas.length;
    var t = tarjetas[actual];
    vImg.src = t.querySelector('img').src;
    vCod.textContent = t.querySelector('.codigo').textContent;
    vTit.textContent = t.querySelector('strong').textContent;
    vTxt.textContent = t.querySelector('.pie span').textContent;
    vNum.textContent = (actual + 1) + ' / ' + tarjetas.length;
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
html = html.replace('__TIRA__', tira)
html = html.replace('__TARJETAS__', tarjetas_html)
html = html.replace('__PARADAS__', paradas_html)
html = html.replace('__TOURJSON__', tour_json)
dst = '/home/user/modelo-2-italiano/docs/web'
os.makedirs(dst, exist_ok=True)
out = os.path.join(dst, 'cafe_napoli_landing.html')
open(out, 'w').write(html)
print('landing:', out, len(html) // 1024, 'KB')
