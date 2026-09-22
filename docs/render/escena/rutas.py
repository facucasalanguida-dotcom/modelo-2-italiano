#!/usr/bin/env python3
"""Donde estan los activos. Un solo sitio que lo decida, y nada mas.

Los 1,5 GB de Poly Haven, el coche y el logo no van al repositorio. Hasta
ahora cada fichero decidia por su cuenta donde buscarlos -escena.py con
CM_SCRATCH, materiales.py con PH_DIR, preparar_activos.py con otra regla- y
con los tres apuntando a sitios distintos el render salia sin texturas
diciendo que todo estaba bien. Esto lo decide una vez para todos.

No importa bpy a proposito: preparar_activos.py tiene que poder usarlo con
el Python de siempre, sin Blender.
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))


def activos():
    """Carpeta raiz de los activos.

    Manda CM_SCRATCH si esta puesta -PH_DIR tambien vale, por lo de antes-.
    Si no, se busca la primera que ya tenga un 'ph' dentro. Y si no hay
    ninguna, la de al lado del codigo, que es donde preparar_activos.py los
    deja por defecto.
    """
    for v in ('CM_SCRATCH', 'PH_DIR'):
        e = os.environ.get(v)
        if e:
            e = os.path.abspath(os.path.expanduser(e))
            # PH_DIR apuntaba a la carpeta ph, no a la raiz
            return os.path.dirname(e) if os.path.basename(e) == 'ph' else e
    for c in (os.path.join(AQUI, 'activos'),
              os.path.join(os.path.expanduser('~'), 'casa_margot_activos'),
              '/tmp/claude-0/-home-user-modelo-2-italiano/'
              '30d2763c-3169-519a-ac78-c5a47134634b/scratchpad'):
        if os.path.isdir(os.path.join(c, 'ph')):
            return c
    return os.path.join(AQUI, 'activos')


SCRATCH = activos()
PH = os.path.join(SCRATCH, 'ph')
LOGO = os.path.join(SCRATCH, 'logo', 'casa_margot_recortado.png')
COCHES = os.path.join(SCRATCH, 'coches')
