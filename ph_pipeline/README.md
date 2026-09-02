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
- **Bisel global** de 2,5 mm en toda la geometria que no lo tenia.
- **Render**: 2560x1440, 1536 muestras adaptativas, 12 rebotes, OIDN con
  albedo y normal, camara identica a la vista original para comparar.

Uso: `descargar.py <ids...>` baja los activos; `render_ph.py` construye y
renderiza (`PH_PREVIEW=1` para pruebas rapidas, `PH_VISTA=R_barra,...`).
`comparar.py antes.png despues.png salida.jpg` genera el antes/despues.
