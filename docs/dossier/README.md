# Dossier de Casa Margot

`build_dossier.py` arma el PDF de presentacion: portada con el logo, pagina
de color, una pagina por render a sangre, y las tablas de equipamiento con
la ficha de cada maquina como enlace clicable dentro del PDF.

    python3 build_dossier.py --fotos CARPETA_CON_LAS_FOTOS --ancho 2560

Las fotos son las del recorrido (`CM_01_calle.png` ... `CM_26_planta_alta.png`,
camaras en `docs/render/escena/recorrido.py`). Entran las que esten en la
carpeta: la que no este, se salta.

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

El orden y el pie de cada vista estan en la lista VISTAS: el del recorrido,
con la planta de cada piso delante de sus fotos y la barra y la cocina por
dentro junto a las suyas. Lo que no este en esa lista se añade detras, por
nombre de fichero.

Las plantas cenitales (25 y 26) son cuadradas: van enteras, con su nombre,
el Norte y una escala grafica de 3 m, que sale del ancho que abarca la foto
en `recorrido.py`. Una foto mas apaisada que 16:9 va a todo lo ancho; las
dos, encima de la banda del pie, que no las tape.
