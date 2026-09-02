# Convierte los mapas EXR (rugosidad / normal) a PNG de 16 bits: misma
# informacion util para Cycles con la mitad de memoria de textura.
import OpenEXR, numpy as np, cv2, glob, os, sys
n = 0
for f in sorted(glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/*/textures/*_4k.exr')):
    png = f[:-4] + '.png'
    if os.path.exists(png): continue
    with OpenEXR.File(f) as ex:
        ch = ex.channels()
        if 'RGB' in ch: rgb = ch['RGB'].pixels
        elif 'RGBA' in ch: rgb = ch['RGBA'].pixels[:, :, :3]
        else:
            planos = [ch[k].pixels for k in ('R', 'G', 'B') if k in ch]
            rgb = np.stack(planos, axis=-1) if len(planos) == 3 else np.repeat(ch[list(ch)[0]].pixels[..., None], 3, axis=-1)
    rgb = np.clip(np.nan_to_num(rgb.astype(np.float32)), 0, 1)
    bgr16 = (rgb[:, :, ::-1] * 65535 + 0.5).astype(np.uint16)
    cv2.imwrite(png, bgr16, [cv2.IMWRITE_PNG_COMPRESSION, 2])
    os.remove(f); n += 1
    print('  ', os.path.basename(png), bgr16.shape, flush=True)
print('convertidos:', n)
