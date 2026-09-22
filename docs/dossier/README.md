# Dossier de Casa Margot

`build_dossier.py` arma el PDF de presentacion: portada con el logo, pagina
de color, una pagina por render a sangre, y las tablas de equipamiento con
la ficha de cada maquina como enlace clicable dentro del PDF.

    python3 build_dossier.py --fotos ../render/casa_margot

Opciones:

    --fotos    carpeta con los CM_*.png o .jpg. Si hay las dos, manda el jpg.
    --salida   fichero de salida
    --titulo   subtitulo de portada
    --lugar    ciudad, sale en portada y contraportada
    --ancho    reescala las fotos a ese ancho en px. Sin esto el PDF pesa
               unos 50 MB con quince vistas; con --ancho 2000 baja a 4,5 MB,
               que es lo que pasa por correo.
    --sin-equipamiento   deja fuera las tablas de maquinaria.

Las tablas de equipamiento se leen de `docs/planos/LISTA_MAKRO.md`, no de una
copia: si alli se cambia una maquina o una ficha, el dossier sale ya
cambiado. Son las 24 referencias del modelo y las 19 alternativas, con su
medida, donde va cada una y el enlace a makro.es.

Las paginas son 16:9 para que los renders entren sin bandas: son 3840x2160 y
cualquier formato de papel les dejaria franjas arriba y abajo.

El logo se incrusta como VECTOR desde `docs/pared/CASA_MARGOT_LOGO_NERO.pdf`,
no como imagen: se puede ampliar sin que pixele.

Los colores salen de `docs/render/escena/materiales.py`, que es de donde los
toma el render. Si alli cambia un albedo, hay que cambiarlo tambien en la
lista PALETA de este script.

El orden y el pie de cada vista estan en la lista VISTAS. Lo que no este en
esa lista se añade detras, por nombre de fichero.
