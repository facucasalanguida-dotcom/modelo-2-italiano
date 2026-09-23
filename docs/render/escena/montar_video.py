"""Junta los fotogramas del dron en un video, con el FFmpeg de Blender.

No se lanza a mano: lo lanza video.py cuando estan todos los fotogramas.

    blender --background --python montar_video.py -- --carpeta CARPETA
        --fps 60 --salida CasaMargot_dron.mp4 [--codec H264|H265]

H.264 en MP4 con calidad 'casi sin perdida' y el preajuste mas lento, que es
el que mejor comprime: se ve en cualquier sitio. Los PNG se quedan: son el
original, para montarlo en un editor si se quiere.
"""
import argparse
import os
import re
import sys

import bpy


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--carpeta', required=True)
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--salida', required=True)
    ap.add_argument('--codec', default='H264', choices=('H264', 'H265'))
    a = ap.parse_args(argv)

    carpeta = os.path.abspath(a.carpeta)
    fotos = sorted(f for f in os.listdir(carpeta) if re.fullmatch(r'dron_\d{5}\.png', f))
    if not fotos:
        sys.exit(f'No hay fotogramas dron_#####.png en {carpeta}')
    sc = bpy.context.scene
    img = bpy.data.images.load(os.path.join(carpeta, fotos[0]))
    ancho, alto = img.size[0], img.size[1]
    bpy.data.images.remove(img)

    se = sc.sequence_editor_create()
    tira = se.strips.new_image(name='dron', filepath=os.path.join(carpeta, fotos[0]),
                               channel=1, frame_start=1)
    for f in fotos[1:]:
        tira.elements.append(f)
    tira.colorspace_settings.name = 'sRGB'

    r = sc.render
    sc.frame_start, sc.frame_end = 1, len(fotos)
    r.fps = a.fps
    r.resolution_x, r.resolution_y, r.resolution_percentage = ancho, alto, 100
    r.use_sequencer = True
    r.use_compositing = False
    # los PNG ya llevan el revelado (AgX) de la escena: aqui no se toca nada
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    if hasattr(r.image_settings, 'media_type'):
        r.image_settings.media_type = 'VIDEO'
    r.image_settings.file_format = 'FFMPEG'
    ff = r.ffmpeg
    ff.format = 'MPEG4'
    ff.codec = a.codec
    ff.constant_rate_factor = 'PERC_LOSSLESS'
    ff.ffmpeg_preset = 'BEST'
    ff.gopsize = a.fps                      # un fotograma clave por segundo
    ff.audio_codec = 'NONE'
    r.filepath = os.path.abspath(a.salida)
    print(f'montando {len(fotos)} fotogramas {ancho}x{alto} a {a.fps} fps -> {r.filepath}',
          flush=True)
    bpy.ops.render.render(animation=True)
    print('VIDEO LISTO', r.filepath, flush=True)


if __name__ == '__main__':
    main()
