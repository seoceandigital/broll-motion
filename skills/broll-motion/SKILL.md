---
name: broll-motion
description: Use cuando alguien te da un video de cara a camara (y su transcripcion) y pide B-roll, motion graphics, cortinillas animadas u overlays. Genera clips animados sincronizados con las palabras del presentador y listos para su editor.
---

# B-roll de motion graphics

Generas clips animados que acompanan lo que dice un presentador en camara. El principio que ordena todo el resto: **hay una sola forma en pantalla y nunca corta**. Crece, se estrecha, cambia de esquinas y de color, y su contenido se sustituye con un desenfoque corto. Un cursor provoca cada cambio con clics y arrastres, y cada cambio cae sobre una palabra concreta del audio.

Eso es lo que separa esto de una plantilla: no hay cortes duros entre graficos, hay un objeto que se transforma mientras el presentador habla.

El usuario recibe clips sueltos para meter en su editor, un montaje de revision y dos paginas HTML para revisar.

## Contenido de la skill

| Carpeta | Que hay |
|---|---|
| `engine/` | `motion.js` (motor), `base.css`, `build.py` (clip a HTML autocontenido), `render.js` (render con motion blur), `beats.js` (hojas de fotogramas), fuentes Geist |
| `scripts/` | `setup.sh`, `transcribe.py`, `inspect_video.py`, `words.py`, `composite.py`, `make_pages.py` |
| `reference/engine-api.md` | Como se escribe un clip. **Leelo antes del primero.** |
| `examples/` | Un clip de referencia con la sintaxis completa del motor |

`$SKILL` es la carpeta de esta skill. Se trabaja siempre en una carpeta `motion/` dentro del proyecto del usuario.

## Orden de trabajo

### 1. Entorno (solo la primera vez)

```bash
bash $SKILL/scripts/setup.sh ./motion
```

Instala Playwright y Chromium en `motion/node_modules` y crea `clips/`, `dist/`, `out/`, `work/` e `inputs/`. Todos los comandos del motor llevan `NODE_PATH=./motion/node_modules`.

El script acepta rutas relativas y absolutas. Si termina con "Listo", el entorno esta preparado.

En Linux, si Node y ffmpeg no estan en el PATH del sistema, exportalos antes de cualquier comando. `render.js` invoca `ffmpeg` por nombre y, si no lo encuentra, falla sin explicar la causa.

La skill trae `.claude/settings.json` con permisos restrictivos (pide confirmacion antes de `rm`, `mv`, `curl` y `git push`). Si el usuario quiere aplicarlos a su proyecto, copialo a la raiz del proyecto; no lo hagas sin preguntar.

### 2. Brief

Si el primer mensaje ya trae la informacion, extraela y pregunta solo lo que falte. Si llega en una linea, haz una unica ronda de preguntas. Nunca repreguntes algo ya contestado.

Datos necesarios:

- **Video.** Ruta al archivo. Se referencia como `motion/work/source.*`.
- **Transcripcion.** SRT o VTT con tiempos. Si el usuario no tiene ninguno, generalo tu en local con `transcribe.py` (paso 3); no hace falta ningun servicio externo ni subir el video a ningun sitio.
- **Densidad.** Ligera 2-4 clips por minuto, media 4-7 (por defecto), alta casi todas las frases.
- **Estilo.** Paleta por defecto o marca del usuario. Si tiene marca, que deje logo, capturas y colores en `motion/inputs/`.
- **Restricciones.** Frases que se quedan en su cara, cifras reales que se pueden mostrar, capturas de producto a recrear.

### 3. Inspeccion y transcripcion

```bash
python3 $SKILL/scripts/inspect_video.py motion/work/source.mp4 motion/work
```

Si el usuario no tiene SRT, sacalo del audio en local:

```bash
uv venv .venv-stt --python 3.12 && . .venv-stt/bin/activate
uv pip install faster-whisper
python $SKILL/scripts/transcribe.py motion/work/source.mp4 motion/work/source.srt \
  --lang es --model small --words motion/work/palabras.json
```

El entorno virtual es obligatorio: en la mayoria de distribuciones el Python del sistema rechaza la instalacion (PEP 668). El modelo `small` basta para localizar palabras; sube a `medium` solo si el audio es dificil.

Esto da tiempos **por palabra sacados del audio**, mas exactos que estimarlos repartiendo un bloque de SRT entre sus caracteres. Usa `palabras.json` para anclar los cambios de estado.

Si el usuario ya trae su SRT, conviertelo a tiempos estimados con:

```bash
python3 $SKILL/scripts/words.py transcripcion.srt > motion/work/words.txt
```

Abre `motion/work/contact.png` y mirala tu mismo, no te fies solo del JSON. `video.json` da resolucion, fps y los tramos de composicion:

- **full:** el presentador llena el cuadro.
- **pip:** el presentador esta en un recuadro y el resto esta libre. Incluye la posicion del recuadro y avisa si cambia de tamano.

Los clips deben coincidir en resolucion y fps con el video. Los tiempos por palabra de un SRT son estimados (unos 0,2 s de margen).

### 4. Plan, y aprobacion antes de escribir codigo

Presenta una tabla, una fila por clip:

| # | Entra-Sale | Frase | Que hace la forma y sobre que palabras | Tratamiento | Por que |

**La decision importante es cuanto cuadro ocupa cada clip.** Tomala clip a clip y justificala:

- **Cortinilla a pantalla completa.** Cuando el cuadro es todo cara y la frase describe algo visible: un producto, un proceso, una comparacion, una cifra, un cambio de capitulo. Dura lo que dura la idea, 3 a 10 s, y despues se devuelve la cara. Nunca en el primer segundo del gancho ni sobre frases personales o de opinion. Minimo 2 s de cara entre cortinillas.
- **Panel en el hueco.** Cuando el montaje ya deja sitio: recuadro PiP, pantalla partida, zona lisa. Clip transparente (`bg:null`) centrado en la zona libre y dimensionado para no invadir el recuadro del presentador en ningun momento. Puede durar 15 s o mas como una sola mutacion, porque la cara no desaparece.
- **Nada.** La frase habla del presentador, o esta demasiado pegada a otro clip.

Reglas de contenido:

- Muestra los objetos reales de los que habla: la carpeta, la terminal, el archivo, el producto, el resultado. Sacalos de sus palabras y mapea cada idea sobre el vocabulario de interacciones de `reference/engine-api.md`.
- **Nunca inventes cifras, citas, precios ni resultados.** Barras relativas, lineas de texto esqueleto o etiquetas literales de la transcripcion. Las cifras reales entran solo si las da el usuario, y lo ilustrativo se declara en la entrega.
- Una idea por clip. Un tramo PiP continuo puede ser un unico clip largo con varios estados.
- El ritmo lo marca el habla, no la musica: un cambio por golpe hablado, cada 0,4 a 1,2 s.

Espera la aprobacion. Un render es caro en tiempo de maquina: corregir la tabla cuesta minutos, rehacer los clips cuesta horas.

### 5. Construir

Un fragmento por clip en `motion/clips/NN-nombre.html`, segun `reference/engine-api.md`. Despues:

```bash
python3 $SKILL/engine/build.py motion/dist motion/clips/*.html
```

Cada cambio de estado va sobre su palabra: tiempo local = tiempo de la palabra menos el punto de entrada del clip.

### 6. Verificar fotogramas antes de renderizar

```bash
NODE_PATH=./motion/node_modules node $SKILL/engine/beats.js motion/dist/NN-nombre.html motion/work/NN.png 0.4 1.2 2.1
```

Elige instantes donde cada estado ya se ha asentado, mas un par a mitad de mutacion. Mira todas las hojas. Corrige texto apretado, cortado o ilegible, cambios fuera de palabra y cualquier momento en que el cursor se salga del cuadro. Vuelve a comprobar despues de corregir. Este paso no es opcional: es lo que evita renderizar durante media hora algo que estaba mal a los 2 segundos.

### 7. Renderizar

```bash
NODE_PATH=./motion/node_modules node $SKILL/engine/render.js motion/dist/NN-nombre.html motion/out/NN-nombre_0m32s40.mp4 30000/1001
```

- Los fps son los del video de origen.
- Los clips de panel (`bg:null`) se escriben en `.mov`: ProRes 4444 con canal alfa. Requiere un ffmpeg con `prores_ks`.
- El nombre lleva el punto de entrada en la linea de tiempo: `0m32s40` es 0:32,40.
- Son 4 subfotogramas por fotograma, mucho mas lento que el tiempo real. Con varios nucleos, dos clips en paralelo.
- En maquinas con poca memoria, lanzalo como trabajo en segundo plano con aviso al terminar. Nunca en primer plano con un bucle de sondeo.

### 8. Entregar

Escribe `motion/plan.json` (esquema en `reference/engine-api.md`) y despues:

```bash
python3 $SKILL/scripts/composite.py motion/plan.json motion/out/preview.mp4
python3 $SKILL/scripts/make_pages.py motion/plan.json motion/out/preview.mp4
```

En `motion/out/` quedan: los clips, `TIMING.md` (archivo, entrada, salida, frase, tratamiento y que es ilustrativo), `preview.mp4` (el video con los clips insertados a corte seco y audio original), `viewer.html` y `compare.html`.

Di con claridad que el montaje es solo para revisar. El corte final lo hace el usuario en su editor, donde ajusta tiempos, transiciones y audio.

## Estilo por defecto

La marca del usuario manda sobre esto.

- **Color:** lienzo `#E9E7E2`, tinta `#0B0B0B`, componentes blancos, un solo acento `#FF5A1F`. Sobre material oscuro, los paneles usan formas claras (`#F4F2EE`).
- **Tipografia:** Geist para interfaz, Geist Mono para codigo, rutas y terminales. Un unico juego de iconos con un unico grosor de trazo (`M.icon`).
- **Movimiento:** muelles con rebote minimo. El borde que avanza y el que sigue usan muelles distintos, asi los indicadores se estiran al moverse. La camara acerca para que cada estado llene el cuadro.
- **Prohibido:** easing saltarin, particulas, brillos, degradados en la interfaz, grosores de icono mezclados, tiempos muertos, datos inventados y cualquier cosa con aspecto de plantilla.

## Errores que ya han pasado

- `will-change` sobre algo que la camara escala deja el texto borroso. No lo pongas.
- El texto que se sustituye dentro de una forma que muta necesita sus propios tiempos de entrada y salida (`M.vis` din/lin/lout). Sin eso, el texto viejo y el nuevo se solapan.
- Las etiquetas con `mix-blend-mode: difference` tienen que ir en una capa que lleve el modo de fusion; un padre con filtro las aisla y dejan de fundirse.
- Los elementos que se deslizan bajo un resaltado necesitan muelles `M.FAST`, o la fila resaltada se queda vacia un instante.
- El cursor tiene que seguir dentro del cuadro en todos los niveles de zoom, tambien durante las mutaciones.
- Los tiempos de un SRT se desvian dentro de cada bloque. Pon los cambios importantes en la primera o la ultima palabra del bloque.
- Un clip termina manteniendo su ultimo estado; el montaje congela ese fotograma si el hueco es mas largo.
- Si no puedes descargar el video de origen, pideselo al usuario en vez de insistir con descargadores.
- `transcribe.py` sobre un video sin voz (un render de motion graphics, musica sola) devuelve vacio aunque el archivo tenga pista de audio. Reintenta solo sin el filtro de voz y, si sigue vacio, lo dice. Comprueba que el material tiene voz antes de culpar al script.
- La transcripcion automatica falla en nombres propios y marcas. Revisa el SRT antes de usarlo para rotulos en pantalla: un nombre mal escrito en un grafico es peor que no poner grafico.
