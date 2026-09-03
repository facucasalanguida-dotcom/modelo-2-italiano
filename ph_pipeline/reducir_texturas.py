# Baja la memoria de textura de Cycles sin perdida visible a 2560x1440:
#  - PNG de 16 bits -> 8 bits (Blender los carga como float: 4x memoria)
#  - lo que esta lejos o es pequeno pasa a 2K (etiquetas de botella a 1K)
import cv2, glob, os, numpy as np
A2K = ('tree_small_02', 'potted_plant_01', 'potted_plant_02', 'tea_set_01', 'carrot_cake', 'croissant',
       'denim_fabric', 'asphalt_02', 'concrete_floor_worn_001', 'stone_tiles', 'stone_tiles_02', 'marble_01',
       'wine_bottles_01', 'metal_stool_01')
antes = despues = 0; n = 0
for f in sorted(glob.glob('*/textures/*_4k.*')):
    aid = f.split('/')[0]
    if not f.endswith(('.png', '.jpg')): continue
    im = cv2.imread(f, cv2.IMREAD_UNCHANGED)
    if im is None: print('  no leo', f); continue
    antes += os.path.getsize(f)
    cambiado = False
    if im.dtype == np.uint16:
        im = (im.astype(np.float32) / 257.0 + 0.5).astype(np.uint8); cambiado = True
    lado = 1024 if '_label_' in f else (2048 if aid in A2K else 4096)
    if max(im.shape[:2]) > lado:
        im = cv2.resize(im, (lado, lado * im.shape[0] // im.shape[1]), interpolation=cv2.INTER_AREA); cambiado = True
    if cambiado:
        if f.endswith('.png'): cv2.imwrite(f, im, [cv2.IMWRITE_PNG_COMPRESSION, 3])
        else: cv2.imwrite(f, im, [cv2.IMWRITE_JPEG_QUALITY, 93])
        n += 1
    despues += os.path.getsize(f)
print(f'convertidos {n}; disco {antes/1e6:.0f} MB -> {despues/1e6:.0f} MB')
