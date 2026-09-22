# Prompt para pasar los renders por Gemini

Uno solo, el mismo para las quince. Va en ingles a proposito: los modelos de
imagen de Gemini responden bastante mejor asi.

Va objeto por objeto, no material por material. Lo que delata a un objeto
renderizado no es su color: es que le faltan las piezas pequeñas que tiene
uno de verdad -costuras, tornillos, juntas, rejillas, cables, holguras de
fabricacion-, que todos los iguales son exactamente iguales, y que apoya en
el suelo sin llegar a tocarlo.

Nombra explicitamente los cuatro elementos que el modelo redibujo cuando se
probo -el logo manuscrito, el liston de roble, las tiras de LED y los
cuarterones de las puertas-. Aun asi, conviene comparar el antes y el
despues en esos cuatro puntos antes de dar una imagen por buena.

```
This is a CGI render of a real restaurant. Rebuild it as a photograph of
that same restaurant, taken with a camera.

Keep every object exactly where it is and exactly the shape it is. What
changes is that each object stops looking manufactured by a computer and
starts looking like the real, specific, slightly used object it represents.

=== NEVER CHANGE ===
- Camera, framing, perspective, composition, proportions.
- The position, outline, size, orientation and number of every object.
  Nothing moves, nothing is added, nothing is deleted, nothing is swapped
  for a different model of the same thing.
- Any colour or material identity. The teal-blue wall stays that exact
  teal, the oak stays that oak, the dark stone stays that stone.
- Any text, logo, sign, label or screen. Do not re-letter, re-draw,
  straighten or tidy the handwritten CASA MARGOT wall logo.
- The vertical oak slat cladding: every slat in place, same width, same
  gap, same rhythm. Do not redraw it.
- The recessed LED strips on the stair treads and under the shelves: they
  stay continuous straight lines of light, same thickness, same position.
  Never split them into dots, lamps or glowing blobs.
- Door leaves, frames, handles and hardware: same design, same divisions.

=== WHAT MAKES AN OBJECT LOOK REAL ===
Apply all of this to every object in the frame, inside its own outline:

1. ASSEMBLY. Real objects are made of parts. Show the joins: panel gaps,
   weld seams, rivets and screw heads, hinges, rubber gaskets, ventilation
   grilles, adjustable feet, edge trims, the seam where two materials meet.
2. TOLERANCE. Nothing in reality is perfect. Gaps vary by a fraction of a
   millimetre along their length. A door sits a hair off flush. A shelf is
   a touch out of level. Symmetry is almost, never exactly.
3. VARIATION. Where several identical things repeat -chairs, slats, bottles,
   tiles, treads- each one differs slightly: grain, tone, wear, how the
   light catches it. Never a copy-pasted array.
4. CONTACT. Every object truly touches what holds it: a tight dark shadow
   right at the base opening as it rises, a little dust or crumb caught at
   the foot, a slight compression where soft meets hard. Nothing hovers.
5. USE. This is a working restaurant, not a showroom on opening day.
   Fingerprints where hands go, brighter edges where things rub, duller
   surfaces where they don't, a thin uneven veil of dust that only shows at
   grazing light.

=== OBJECT BY OBJECT ===
- Coffee machine, grinder, granita machine: brushed stainless with a
  directional grain, chrome group heads with real reflections, black
  rubberised portafilter handles worn shiny at the grip, backlit switches,
  engraved legends, the faint coffee staining a working machine has.
- Refrigerated display cases: real laminated glass with green edges and
  visible edge seals, stainless frames with fine brushing and fingerprints
  near the handles, shelf brackets, a lit interior with believable falloff,
  condensation film barely there at the coldest corner, perforated air
  grilles and control panel with real indicator lights.
- Kitchen line, hood and fridges: heavy-gauge stainless, hammered light,
  visible panel joints and fixing screws, knurled control knobs, filter
  cassettes in the hood with their own frames and clips, hygienic sealant
  at every corner.
- Tables: solid oak with real grain running through the thickness, visible
  end grain at the edges, a hand-applied matt finish that scatters light,
  softened arrises, faint ring marks and cutlery scratches.
- Chairs and the banquette: fabric with a real weave you can read up close,
  stitched seams and piping, slight slump and creasing where the covering
  wraps the foam, compression where a back meets a frame, tiny lint,
  slender legs with felt pads and scuffed tips.
- Pendant lamps: opal glass glowing unevenly, the lamp faintly visible
  inside, brass rims with warm tarnish in the recesses, a real cable with
  weight, a ceiling rose that sits flat against the ceiling.
- Bottles, jars and glassware: glass thickness visible at rims and bases,
  caustic light through the liquid, labels with slight lift at the edges
  and real paper texture, the food and drink inside looking edible rather
  than moulded.
- Wicker baskets, ceramic vases, terracotta pots: hand-made irregularity,
  each weave strand different, porous open clay, mineral bloom, the plant
  with imperfect leaves, a few browning tips and real soil.
- Stairs and glass balustrade: laminated glass with visible edges and
  fixings, oak handrail polished where hands run, treads with traffic wear
  along the middle of the walking line.
- Cars and street outside: real automotive paint with flake and clearcoat,
  panel gaps, dust film low on the bodywork, rubber seals gone matt, road
  surface with patches and worn markings.

=== LIGHT ===
Soft physically believable falloff. Real contact shadows and corner
occlusion, tight at the contact and opening as they move away. Indirect
bounce that carries colour: the oak warming the plaster near it, the teal
wall tinting what faces it. Gentle highlight roll-off instead of clipping,
and recovered detail in blown-out windows so the street reads. Lamps and
LEDs keep their exact shape but gain a faint, tight bloom, never a halo.

=== CAMERA ===
Photograph it as an architectural photographer would: full-frame sensor,
tilt-shift lens with verticals kept straight, around f/8, low ISO, tripod.
Very slight corner falloff, a trace of chromatic aberration on the
highest-contrast edges, the far plane a touch softer, fine luminance grain,
filmic response with neutral whites and open, slightly cool shadows.

Output the same image at the same resolution and aspect ratio. Same room,
same objects, same places: photographed instead of computed.
```
