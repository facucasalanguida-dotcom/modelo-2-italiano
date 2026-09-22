# Prompt para pasar los renders por Gemini

Uno solo, el mismo para las quince. Va en ingles a proposito: los modelos de
imagen de Gemini responden bastante mejor asi.

La idea: un render canta a render por cosas muy concretas -todo esta recien
estrenado, los bordes son perfectos, el vidrio no tiene una huella, no hay
polvo en ningun sitio y la luz es demasiado limpia-. El prompt va material
por material diciendo que aspecto tiene esa cosa en la vida real, y a la vez
prohibe tocar forma, sitio y color.

Nombra explicitamente los cuatro elementos que el modelo redibujo cuando se
probo -el logo manuscrito, el liston de roble, las tiras de LED y los
cuarterones de las puertas-. Aun asi, conviene comparar el antes y el
despues en esos cuatro puntos antes de dar una imagen por buena.

```
Turn this architectural render into a photograph of the same room.

Not a redesign, not a reinterpretation: the same room, the same objects, in
the same places, photographed instead of computed. Everything you change
must be at the level of surface, light and optics. Nothing may move, change
shape, change colour or appear that was not already there.

=== WHAT MUST NOT CHANGE ===
- Geometry, camera, framing, composition, perspective, proportions.
- Position, shape, size, orientation and number of every object.
- Every colour and material identity. The teal-blue wall stays that exact
  teal. The oak stays that oak. The dark stone stays that stone. Do not
  warm, cool, saturate or "improve" the palette.
- Any text, logo, sign, label, screen or branding. Do not re-letter,
  re-draw, straighten or clean up the handwritten CASA MARGOT wall logo.
- The vertical oak slat cladding on the columns and the bar front: every
  slat stays in place, same width, same gap, same rhythm. Do not redraw it.
- The recessed LED strips on the stair treads and under the shelves: they
  stay continuous straight lines of light, same thickness, same position.
  Never turn them into separate lamps, dots or glowing blobs.
- Door leaves, frames, handles and hardware: same design, same divisions.
- Do not add furniture, props, people, plants, cables, signage or clutter.

Every edge, silhouette, reflection and shadow boundary stays in the same
pixel position.

=== WHAT MAKES IT REAL ===
This is a working restaurant, not a showroom on opening day. Nothing is
brand new, nothing is laboratory-clean, nothing is mathematically perfect.
Give every surface the history it would really have, without altering its
shape or colour:

- Oak (slat cladding, bar top, tables, stair treads): visible grain and
  pore structure, cathedral figure, end grain darker where it is cut. Very
  slight tonal drift from board to board. Edges and arrises microscopically
  softened and a shade lighter where hands and chairs have rubbed them.
  A matt hand-applied finish that scatters light, not a mirror varnish.
- Lime plaster walls: a fine trowel tooth, faint float marks, soft blotches
  of uneven absorption, slightly darker in the corners and where the wall
  meets the floor. Not a flat uniform fill.
- Dark split stone slabs: real cleft face with depth -ridges catching light,
  recesses in shadow-, mineral grain and a faint sheen where the surface is
  flatter. The joints between slabs slightly irregular.
- Stainless steel (kitchen line, hood, appliances, door pulls): fine
  unidirectional brushing that catches the light along its grain, plus
  fingerprints, smears and micro-scratches concentrated where hands go:
  handles, edges, control panels. Reflections blurred and dimmed by that
  wear, never chrome-mirror.
- Glass (shopfront, door, display cases, glassware): faint fingerprints and
  smudges near handles and edges, a little dust settled in the lower
  corners, a very slight green tint in the thickness of the pane, honest
  reflections of the room layered over what is behind.
- Upholstery and seat cushions: real woven or grain texture close up, slight
  slump and softening at the front edges, gentle creases where the covering
  folds around the foam, tiny lint. Not a smooth inflated plastic shape.
- Terracotta pots: porous open surface, mineral bloom, darker where damp.
- Brass and painted metal: warm tarnish in the recesses, brighter on the
  edges that get touched.
- Floors: scuffs and traffic sheen along the walking lines, dust and crumbs
  gathering at skirtings and under furniture, joints slightly darkened.
- Horizontal surfaces catch a thin, uneven veil of dust that only shows at
  grazing light.

=== LIGHT ===
- Soft, physically believable falloff. Real contact shadows and ambient
  occlusion where objects meet surfaces, sharp right at the contact and
  opening as they move away.
- Indirect bounce that carries colour: the oak warming the plaster near it,
  the teal wall tinting what faces it.
- Gentle highlight roll-off instead of clipping, and recovered detail in
  blown-out windows so the street outside reads.
- Lamps and LEDs keep their exact shape but gain a faint, tight, realistic
  bloom, not a glow halo.

=== CAMERA ===
Photograph it as an architectural photographer would: full-frame sensor,
tilt-shift lens with verticals kept straight, around f/8, low ISO, tripod.
That brings very slight corner falloff, a trace of chromatic aberration on
the highest-contrast edges, natural depth cues with the far plane a touch
softer, fine luminance grain, and a filmic response with neutral whites and
shadows that stay open and slightly cool.

Output the same image at the same resolution and aspect ratio. It must look
like it was taken with a camera in that room.
```
