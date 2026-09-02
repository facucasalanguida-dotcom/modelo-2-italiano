# Pipeline de render "nivel superior" (recursos reales de Poly Haven, CC0)

Sobre la escena base `blender_scene.py` se aplican, sin tocarla:

- **Luz**: HDRI `wide_street_01` 8K (sol real desde el sur, orientado con el
  ventanal); fuera el sol sintetico y los paneles que fingian la luz de dia.
  Fuerza 3,0 para iluminar y 1,4 para lo que ve la camara.
- **Materiales escaneados 4K**: suelo `wood_floor`, tableros y listones
  `oak_veneer_01`, paredes `white_plaster_02`, hormigon `plastered_wall`,
  pilar `granite_tile`, acera `large_floor_tiles_02`, soportal
  `concrete_floor_worn_001`, calzada `asphalt_02`, toldo `denim_fabric`.
  Acero cepillado anisotropo y laton con velo de uso; variacion de
  rugosidad (desgaste) en suelo, barra y listones; oclusion escaneada.
- **Modelos reales**: `potted_plant_01/02` (plantas), `tree_small_02`
  (arboles de la acera), `wine_bottles_01` (botellero), `dining_chair_02`
  recoloreado a tela crema/arena (sillas), `metal_stool_01` (taburetes).
  Los edificios de caja se retiran: la calle real del HDRI hace de fondo.
- **Sillas y mesas**: cada silla se recentra con su mesa y se mete 7 cm
  bajo el tablero (correlacion silla-mesa en todas las vistas).
- **Barra ordenada**: cafetera en esmalte negro y acero cepillado con
  manometros, placa y lanzas de vapor que nacen del cuerpo; tazas de
  porcelana `tea_set_01` en el calientatazas, pila de platillos anidados con
  taza y azucarero; molinillo con base, aro y salida cromados; pantalla del
  TPV encendida; `carrot_cake` real en los dos soportes; croissants
  fotogrametricos (`croissant`) en las vitrinas.
- **Nada flotando**: se sondea la altura real de cada mostrador (la tabla
  alta esta a 0,98 m, no a 1,04) y se baja todo lo parametrico; los soportes
  de tarta pasan del hueco de las vitrinas a la tabla baja; un pase de
  "asentado" lanza un rayo desde cada objeto contra sus posibles apoyos
  (sin contar su propia geometria) y corrige huecos de 0,5 a 15 mm.
  `PH_CHECK=1` imprime el informe de huecos y sale sin renderizar
  (`PH_CHECK=2` lista todos los objetos).
- **Bisel global** de 2,5 mm en toda la geometria que no lo tenia.
- **Render**: 2560x1440, 1536 muestras adaptativas (umbral 0,005), 12
  rebotes, OIDN con albedo y normal, camara identica a la vista original.

Uso: `descargar.py <ids...>` baja los activos; `render_ph.py` construye y
renderiza (`PH_PREVIEW=1` para pruebas rapidas, `PH_VISTA=R_barra,...`,
`PH_OUT=salida.png`, `PH_SMP=1536`). `comparar.py antes.png despues.png
salida.jpg` genera el antes/despues.

Al instanciar una pieza suelta de un `.blend` se anula su desplazamiento
interno (las botellas de `wine_bottles_01` traen 0,2-0,6 m; las piezas del
juego de te tambien): sin eso acaban lejos de donde se colocan.
