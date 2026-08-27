"""Monta el MP4 del vuelo con los fotogramas disponibles.

Se puede ejecutar en cualquier momento: los huecos aun sin renderizar se
rellenan con el fotograma valido mas cercano, asi que siempre sale un video
completo (mas fluido cuantos mas fotogramas haya).

  python3 montar_video.py <carpeta_frames> <total> <salida.mp4> [fps]
"""
import os, shutil, subprocess, sys, tempfile

import imageio_ffmpeg
import numpy as np
from PIL import Image

DIR, N, SALIDA = sys.argv[1], int(sys.argv[2]), sys.argv[3]
FPS = int(sys.argv[4]) if len(sys.argv) > 4 else 24

# revelado calido identico al de los renders fijos (postfx.py del proyecto)
sys.argv = ['postfx']
import importlib.util
spec = importlib.util.spec_from_file_location(
    'postfx', '/home/user/modelo-2-italiano/postfx.py')
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)

hay = sorted(i for i in range(N) if os.path.exists(f'{DIR}/f_{i:04d}.png'))
if not hay:
    sys.exit('No hay ningun fotograma todavia.')
print(f'{len(hay)}/{N} fotogramas reales ({100*len(hay)/N:.0f}%)')

tmp = tempfile.mkdtemp(prefix='napvid_')
try:
    for i in range(N):
        j = min(hay, key=lambda h: abs(h - i))       # el valido mas cercano
        dst = f'{tmp}/g_{i:04d}.png'
        shutil.copyfile(f'{DIR}/f_{j:04d}.png', dst)
        pf.postfx(dst)                                # grada in situ
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, '-y', '-framerate', str(FPS), '-i', f'{tmp}/g_%04d.png',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '19',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', SALIDA]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit('ffmpeg fallo:\n' + r.stderr[-1500:])
    mb = os.path.getsize(SALIDA) / 1e6
    print(f'VIDEO {SALIDA}  {N/FPS:.1f}s  {FPS}fps  {mb:.1f} MB')
finally:
    shutil.rmtree(tmp, ignore_errors=True)
