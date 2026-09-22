# Prompt para pasar los renders por Gemini

Uno solo, el mismo para las quince. Va en ingles a proposito: los modelos de
imagen de Gemini responden bastante mejor asi.

Nombra explicitamente los cuatro elementos que el modelo redibujo cuando se
probo -el logo manuscrito, el liston de roble, las tiras de LED y los
cuarterones de las puertas- porque son los que mas se le van. Aun asi,
conviene comparar el antes y el despues en esos cuatro puntos antes de dar
una imagen por buena.

```
Photorealistic finishing pass on this architectural interior render.
This is a strict enhancement task, not a re-imagining. Treat it as
photographic grading and detail recovery on an existing photograph.

DO NOT CHANGE, under any circumstance:
- Geometry, camera, framing, composition, perspective, proportions.
- Position, shape, size, orientation or number of any object.
- Any colour, hue or material identity. The teal-blue wall stays exactly
  that teal, the oak stays that oak, the dark stone stays that stone.
- Any text, logo, signage, label, display or branding. Do not re-letter,
  re-draw or "clean up" the handwritten CASA MARGOT wall logo.
- The vertical oak slat cladding on the columns and the bar front: keep
  every slat in place, same width, same gap, same rhythm. Do not re-draw it.
- The recessed LED strips on the stair treads and under the shelves: keep
  them as continuous straight lines of light, same thickness, same
  position. Do not turn them into separate lamps or reshape them.
- Door panels, frames, handles and hardware: same design, same divisions.

Every edge, silhouette, reflection and shadow boundary must remain in
exactly the same pixel position. Add nothing, remove nothing, move nothing.

ONLY IMPROVE, with shapes and colours untouched:
- Surface micro-detail: oak grain and end grain, lime plaster tooth, the
  rough split face of the dark stone slabs, brushed stainless steel, fabric
  weave on the upholstery, terracotta porosity, glass with faint
  fingerprints and micro-scratches, subtle wear on edges and corners.
- Light: softer and more natural falloff, believable contact shadows and
  ambient occlusion in corners, more convincing indirect bounce, gentler
  highlight roll-off, recovered detail in blown-out window areas.
- Camera realism: natural lens character, realistic depth cues, fine
  photographic grain, filmic tonal response, subtle colour separation in
  the shadows.

Output the same image at the same resolution and aspect ratio, looking
photographed rather than rendered.
```
