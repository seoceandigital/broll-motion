# broll-motion

Skill para Claude Code que anima tus vídeos mientras hablas.

Le das el vídeo de tu cara a cámara y su transcripción. Te devuelve clips animados sincronizados con tus palabras, listos para arrastrar a tu editor.

Fork en español de [Barty-Bart/motion-graphics](https://github.com/Barty-Bart/motion-graphics) (MIT, Bart Slodyczka). El motor de animación es obra suya y se conserva intacto; el flujo de trabajo, la documentación, los defaults de estilo y los permisos están reescritos. Detalles en [LICENSE](LICENSE).

## El principio

Hay una sola forma en pantalla y nunca corta. Crece, se estrecha, cambia de esquinas y de color, y su contenido se sustituye con un desenfoque breve. Un cursor provoca cada cambio con clics y arrastres reales, y cada cambio cae sobre una palabra concreta de tu audio.

Por eso no parece una plantilla: no hay cortes duros entre gráficos, hay un objeto que se transforma mientras hablas.

## Qué te devuelve

| Archivo | Qué es |
|---|---|
| `NN-nombre_0m32s40.mp4` | El clip, nombrado por el segundo exacto en que entra en tu línea de tiempo |
| `NN-nombre_0m32s40.mov` | Igual, pero con transparencia (ProRes 4444) para los paneles que van junto a tu cara |
| `preview.mp4` | Tu vídeo con los clips ya insertados, para revisar |
| `compare.html` | Original contra montaje, sincronizados |
| `viewer.html` | Los clips uno a uno |
| `TIMING.md` | Cada clip con su entrada, salida y la frase que cubre |

El montaje es solo para revisar. El corte final lo haces tú en tu editor, donde ajustas tiempos, transiciones y audio.

## Instalación

Copia `skills/broll-motion` en el `.claude/skills/` de tu proyecto, o en `~/.claude/skills/` para tenerla siempre.

Requisitos: Node 18 o superior, Python 3 y ffmpeg. Los paneles transparentes además necesitan el codificador ProRes; compruébalo con:

```bash
ffmpeg -hide_banner -encoders | grep prores_ks
```

En la primera ejecución se instalan Playwright y Chromium en una carpeta `motion/` dentro de tu proyecto.

## Uso

Pide a Claude Code que use la skill `broll-motion` y dale la ruta del vídeo y la transcripción.

¿No tienes transcripción? No hace falta que la busques fuera. La skill la genera en tu propio ordenador con `transcribe.py` (faster-whisper): sin API, sin coste por minuto y sin subir tu vídeo a ningún servicio. Además saca los tiempos **palabra por palabra directamente del audio**, que son más exactos que repartir un bloque de subtítulos entre sus letras.

Un aviso: la transcripción automática se equivoca con nombres propios y marcas. Repasa el SRT antes de que un nombre mal escrito acabe en un rótulo.

El proceso tiene una parada obligatoria: antes de escribir una sola línea de código, te presenta una tabla con cada clip propuesto, la frase que cubre y por qué ha elegido ese tratamiento. Hasta que no apruebas, no renderiza nada. Eso es deliberado: un render tarda bastante más que el vídeo en sí, y corregir la tabla cuesta minutos.

## Sobre los datos

No inventa cifras, precios, citas ni resultados. Cuando una frase pide un número que no le has dado, usa barras de tamaño relativo o líneas de texto esqueleto, y en la entrega te dice qué es ilustrativo. Si quieres cifras reales en pantalla, se las das tú.

## Cómo funciona por dentro

Cada fotograma es una función pura del tiempo: no hay transiciones CSS ni temporizadores, así que cualquier fotograma se puede dibujar por separado. Los muelles son respuestas cerradas, y un valor que cambia de destino varias veces es la suma de un muelle por cambio.

Los clips son archivos HTML pequeños sobre un motor compartido (`skills/broll-motion/engine/motion.js`). Chromium headless captura cuatro subfotogramas por fotograma en un obturador de 180 grados y ffmpeg los funde en motion blur.

## Qué no hace por ti

- No monta tu vídeo. Te da piezas.
- No decide tu dirección de arte. Propone tratamientos razonables; el criterio es tuyo.
- No arregla un guion flojo. Si la frase no describe nada visible, lo correcto es dejar tu cara.

## Licencia

MIT, sobre el trabajo original de Bart Slodyczka. Fuentes Geist bajo SIL Open Font License. Trazados de iconos adaptados de Lucide (ISC).

Fork y documentación en español: Antonio Alba, [@antonioalba.ai](https://instagram.com/antonioalba.ai)
