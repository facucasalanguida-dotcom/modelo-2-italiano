# Sitio personal — visualizacion arquitectonica

Web de presentacion para enviar a estudios, empresas de reformas y promotoras.
Una sola pagina en espanol, fondo oscuro calibrado, sin dependencias mas alla
de las fuentes de Google.

| Archivo | Que es |
|---|---|
| `pagina.html` | La pagina: titulo, estilos, contenido y script. Es el cuerpo, sin `<html>` ni `<head>`, porque asi la publica el Artifact de Claude. |
| `build_sitio.py` | Envuelve `pagina.html` en un documento completo y escribe `index.html`. |
| `index.html` | Generado. Lo que se sube a cualquier hosting estatico. |
| `img/` | Imagenes optimizadas para web (2,1 MB en total). |
| `video/vuelo.mp4` | Previsualizacion del vuelo de camara. |

## Regenerar

```bash
python3 build_sitio.py
```

## Publicar

- **Enlace inmediato**: publicado como Artifact de Claude. Se actualiza volviendo
  a publicar `pagina.html`.
- **Dominio propio**: sube `index.html`, `img/` y `video/` tal cual a cualquier
  hosting estatico (GitHub Pages, Netlify, un FTP). No hay backend.

## Contacto

El formulario no tiene servidor: compone el resumen del encargo y lo abre en el
programa de correo del visitante (`mailto:`), con la direccion montada en
JavaScript para que no quede escrita en el HTML. Tambien copia el resumen al
portapapeles. Si algun dia se quiere un formulario que guarde los mensajes hace
falta un servicio externo, y eso ya pide hosting propio.

## Datos que hay que revisar antes de mandarla

- El nombre del rotulo y del pie sale del correo de la cuenta. Cambialo en
  `pagina.html` si no es exacto: aparece en el `<title>`, en `.brand` y en el pie.
- La direccion de correo del formulario esta en la constante `BUZON` del script.
- Los plazos del apartado "Proceso" son una estimacion: ajustalos a tu ritmo real.
