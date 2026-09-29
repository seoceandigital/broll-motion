"""Transcribe un video a SRT con tiempos por palabra, en local y sin API.

Cierra el hueco del flujo: sin esto hay que traer el SRT de un editor externo.

uso:
    python3 transcribe.py video.mp4 salida.srt [--lang es] [--model small]

Requiere faster-whisper en un entorno virtual (PEP 668 impide instalarlo en el
Python del sistema en muchas distribuciones):

    uv venv .venv-stt --python 3.12
    . .venv-stt/bin/activate
    uv pip install faster-whisper

Modelos, de menos a mas preciso: tiny, base, small (por defecto), medium, large-v3.
small basta para localizar palabras; medium o superior solo si el audio es dificil.
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile


def extraer_audio(video: str, destino: str) -> None:
    """Saca el audio a WAV mono 16 kHz, que es lo que espera el modelo."""
    r = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-i", video,
         "-vn", "-ac", "1", "-ar", "16000", destino],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(f"ffmpeg no pudo extraer el audio:\n{r.stderr.strip()}")


def marca(segundos: float) -> str:
    """Formato de tiempo SRT: 00:01:23,450"""
    if segundos < 0:
        segundos = 0.0
    h, resto = divmod(segundos, 3600)
    m, s = divmod(resto, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def recoger(segmentos):
    """Recorre los segmentos del modelo y devuelve (bloques, palabras)."""
    bloques, palabras = [], []
    for seg in segmentos:
        texto = seg.text.strip()
        if not texto:
            continue
        bloques.append((seg.start, seg.end, texto))
        for w in (seg.words or []):
            palabras.append({"t": round(w.start, 2), "w": w.word.strip()})
        print(f"  [{marca(seg.start)}] {texto[:70]}", file=sys.stderr)
    return bloques, palabras


def main() -> None:
    p = argparse.ArgumentParser(description="Video a SRT con tiempos por palabra, en local.")
    p.add_argument("video")
    p.add_argument("salida", help="ruta del SRT de salida")
    p.add_argument("--lang", default="es", help="codigo de idioma (es por defecto)")
    p.add_argument("--model", default="small", help="tiny, base, small, medium, large-v3")
    p.add_argument("--words", default=None,
                   help="ruta opcional para volcar los tiempos por palabra en JSON")
    args = p.parse_args()

    if not pathlib.Path(args.video).exists():
        sys.exit(f"No existe el video: {args.video}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit(
            "Falta faster-whisper. Creá un entorno virtual y instalalo:\n"
            "  uv venv .venv-stt --python 3.12\n"
            "  . .venv-stt/bin/activate\n"
            "  uv pip install faster-whisper"
        )

    with tempfile.TemporaryDirectory() as tmp:
        wav = str(pathlib.Path(tmp) / "audio.wav")
        extraer_audio(args.video, wav)

        print(f"Cargando el modelo {args.model}...", file=sys.stderr)
        modelo = WhisperModel(args.model, device="cpu", compute_type="int8")

        print("Transcribiendo...", file=sys.stderr)
        segmentos, info = modelo.transcribe(
            wav, language=args.lang, word_timestamps=True, vad_filter=True,
        )
        bloques, palabras = recoger(segmentos)

        # El filtro de voz a veces se come pistas con musica de fondo o voz baja.
        # Antes de dar el video por mudo, se reintenta sin filtro.
        if not bloques:
            print("El filtro de voz no encontro nada. Reintentando sin filtro...",
                  file=sys.stderr)
            segmentos, info = modelo.transcribe(
                wav, language=args.lang, word_timestamps=True, vad_filter=False,
            )
            bloques, palabras = recoger(segmentos)

    if not bloques:
        sys.exit(
            "No se detecto voz en el audio.\n"
            "Causas habituales: el video no tiene pista de voz (solo musica o "
            "efectos), el idioma indicado con --lang no es el que se habla, o el "
            "audio esta demasiado bajo."
        )

    with open(args.salida, "w", encoding="utf-8") as f:
        for i, (ini, fin, texto) in enumerate(bloques, 1):
            f.write(f"{i}\n{marca(ini)} --> {marca(fin)}\n{texto}\n\n")

    if args.words:
        with open(args.words, "w", encoding="utf-8") as f:
            json.dump(palabras, f, ensure_ascii=False, indent=1)

    print(
        f"\nListo: {args.salida} · {len(bloques)} bloques · {len(palabras)} palabras "
        f"· idioma detectado {info.language} (confianza {info.language_probability:.2f})",
        file=sys.stderr,
    )
    print(
        "Los tiempos por palabra vienen del audio, asi que son mas exactos que "
        "los estimados a partir de un SRT de texto.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
