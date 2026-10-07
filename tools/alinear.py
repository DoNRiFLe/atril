#!/usr/bin/env python3
"""
Alinea la letra de una cancion con su audio y escribe un .lrc listo para el Atril.

    pip install faster-whisper
    python tools/alinear.py tema.mp3 letra.txt -o tema.lrc

Como funciona: Whisper transcribe el audio con tiempo por palabra; despues se
alinea esa transcripcion (que siempre trae errores, sobre todo con la banda
sonando encima) contra la letra real que vos ya tenes. Cada linea se queda con
el tiempo de su primera palabra reconocida; las lineas que no pegaron se
interpolan entre sus vecinas.
"""
import argparse, difflib, os, re, shutil, subprocess, sys, tempfile, unicodedata
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# por debajo de este porcentaje de palabras alineadas, el .lrc no sirve
MINIMO = 35.0

def norm(w):
    """Minusculas, sin tildes y sin puntuacion, para comparar manzanas con manzanas."""
    w = unicodedata.normalize('NFD', w.lower().replace("'", ""))
    w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9]", "", w)

def stamp(t):
    m, s = divmod(max(0.0, t), 60)
    return f"[{int(m):02d}:{int(s):02d}.{int(round(s % 1 * 100)):02d}]"

def tiene_demucs():
    try:
        import demucs  # noqa: F401
        return True
    except ImportError:
        return False


def separar_voz(audio, modelo="htdemucs"):
    """Deja solo la voz en un .wav al lado del original, y devuelve su ruta.

    Se cachea: si el .vocals.wav ya existe, no vuelve a separar (tarda minutos).
    """
    dest = Path(audio).with_suffix(".vocals.wav")
    if dest.exists():
        print(f"  uso la voz ya separada: {dest.name}", file=sys.stderr)
        return str(dest)

    if not tiene_demucs():
        print("  demucs no esta instalado. Para separar la voz:", file=sys.stderr)
        print(f"    {sys.executable} -m pip install demucs", file=sys.stderr)
        return None

    print(f"  separando la voz con demucs ({modelo}); esto tarda unos minutos…",
          file=sys.stderr)
    tmp = tempfile.mkdtemp(prefix="demucs-")
    try:
        r = subprocess.run(
            [sys.executable, "-m", "demucs", "--two-stems=vocals",
             "-n", modelo, "-o", tmp, str(audio)],
            check=False,
        )
        if r.returncode != 0:
            print("  demucs fallo; sigo con el audio original.", file=sys.stderr)
            return None
        salida = Path(tmp) / modelo / Path(audio).stem / "vocals.wav"
        if not salida.exists():
            cands = list(Path(tmp).rglob("vocals.wav"))
            if not cands:
                print("  demucs no dejo el vocals.wav donde esperaba.", file=sys.stderr)
                return None
            salida = cands[0]
        shutil.move(str(salida), str(dest))
        print(f"  voz separada en {dest.name}", file=sys.stderr)
        return str(dest)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def medir(audio):
    """Nivel del audio, para saber si el problema es el archivo o la mezcla."""
    import av, math
    pico, suma, n = 0.0, 0.0, 0
    with av.open(audio) as cont:
        stream = cont.streams.audio[0]
        print(f"  formato: {stream.codec_context.name}, {stream.rate} Hz, "
              f"{stream.channels} canal(es)", file=sys.stderr)
        for frame in cont.decode(stream):
            a = frame.to_ndarray().astype("float64")
            if a.size == 0:
                continue
            m = abs(a).max()
            if m > 1.5:          # enteros: normalizar a -1..1
                a, m = a / 32768.0, m / 32768.0
            pico = max(pico, m)
            suma += (a ** 2).sum()
            n += a.size
    rms = math.sqrt(suma / n) if n else 0.0
    db = 20 * math.log10(rms) if rms > 0 else -99
    print(f"  nivel: pico {pico:.3f}, RMS {db:.1f} dBFS", file=sys.stderr)
    if db < -50:
        print("  El audio esta practicamente mudo: revisá el archivo.", file=sys.stderr)
    return db


def _run(model, audio, lang, vad, mixto):
    auto = lang in (None, "auto")
    segments, info = model.transcribe(
        audio, language=(None if auto else lang),
        word_timestamps=True,
        vad_filter=vad,
        # el VAD viene calibrado para voz hablada; con la banda sonando encima
        # hay que aflojarlo o se come el tema entero
        vad_parameters=dict(threshold=0.3, min_silence_duration_ms=700,
                            speech_pad_ms=200) if vad else None,
        beam_size=5,
        condition_on_previous_text=False,
        # con intro instrumental, un solo segmento no alcanza para detectar idioma
        language_detection_segments=(4 if auto else 1),
        # re-detecta el idioma en cada segmento, para temas que mezclan dos
        multilingual=mixto,
    )
    words, nseg = [], 0
    for seg in segments:
        nseg += 1
        for w in (seg.words or []):
            n = norm(w.word)
            if n:
                words.append((n, w.start))
        print(f"  … {seg.end:6.1f}s", end="\r", file=sys.stderr)
    return words, nseg, info


def transcribe(audio, model_size, lang, vocals_only, mixto, separar,
               modelo_demucs="htdemucs"):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    if separar:
        voz = separar_voz(audio, modelo_demucs)
        if voz:
            audio = voz

    words, nseg, info = _run(model, audio, lang, vocals_only, mixto)
    if not words and vocals_only:
        vad_s = info.duration_after_vad or 0
        print(f"  el filtro de silencios dejo {vad_s:.0f}s de {info.duration:.0f}s "
              f"y no salio nada; reintento sin filtro…", file=sys.stderr)
        words, nseg, info = _run(model, audio, lang, False, mixto)

    # ultimo recurso: aislar la voz y volver a intentar
    if not words and not separar and tiene_demucs():
        print("  no se reconocio nada; pruebo aislando la voz…", file=sys.stderr)
        voz = separar_voz(audio, modelo_demucs)
        if voz:
            words, nseg, info = _run(model, voz, lang, False, mixto)

    print(f"  idioma: {info.language} (confianza {info.language_probability:.0%})",
          file=sys.stderr)
    print(f"  transcripcion: {len(words)} palabras en {nseg} segmentos, "
          f"{info.duration:.0f}s de audio", file=sys.stderr)

    if not words:
        print("", file=sys.stderr)
        print("Whisper no reconocio NINGUNA palabra en este audio.", file=sys.stderr)
        try:
            medir(audio)
        except Exception as e:
            print(f"  (no pude medir el audio: {e})", file=sys.stderr)
        print("Causas tipicas, en orden:", file=sys.stderr)
        if not tiene_demucs():
            print("  1. La voz queda tapada por la banda. Instalá demucs para aislarla:", file=sys.stderr)
            print(f"     {sys.executable} -m pip install demucs", file=sys.stderr)
        else:
            print("  1. Ni con la voz aislada se entiende. Probá -m medium o -m large-v3.", file=sys.stderr)
        print("  2. El archivo es instrumental o esta en silencio/muy bajo.", file=sys.stderr)
        print("  3. El mp3 esta dañado: abrilo en un reproductor para confirmar.", file=sys.stderr)
        print("  4. Sincronizá ese tema a mano en el Atril: cargale el audio y usá", file=sys.stderr)
        print("     Ajustes -> Sincronizar tap a tap. Son 3 minutos.", file=sys.stderr)
        sys.exit(2)

    return words, info.duration

def align(lyric_lines, heard):
    """Devuelve un tiempo (o None) por cada linea de la letra."""
    # palabras de la letra, recordando a que linea pertenece cada una
    lyr, owner = [], []
    for i, line in enumerate(lyric_lines):
        for w in line.split():
            n = norm(w)
            if n:
                lyr.append(n)
                owner.append(i)
    if not lyr or not heard:
        return [None] * len(lyric_lines), 0.0

    sm = difflib.SequenceMatcher(None, lyr, [w for w, _ in heard], autojunk=False)
    times = [None] * len(lyric_lines)
    matched = 0
    for a, b, size in sm.get_matching_blocks():
        for k in range(size):
            li, t = owner[a + k], heard[b + k][1]
            matched += 1
            if times[li] is None or t < times[li]:
                times[li] = t
    pct = matched / len(lyr) * 100
    print(f"  alineadas {matched}/{len(lyr)} palabras ({pct:.0f}%)", file=sys.stderr)
    if MINIMO <= pct < 75:
        print("  Alineo a medias: revisa el resultado en el Atril, sobre todo los\n"
              "       estribillos y las partes que se repiten.", file=sys.stderr)
    return times, pct

def monotonic_fill(times, lines, total):
    """Rellena los None interpolando y fuerza que los tiempos no retrocedan."""
    out = list(times)
    # no permitir saltos hacia atras
    last = 0.0
    for i, t in enumerate(out):
        if t is not None:
            if t < last:
                out[i] = None
            else:
                last = t
    known = [i for i, t in enumerate(out) if t is not None]
    if not known:
        return [i * total / max(1, len(lines)) for i in range(len(lines))]
    for i in range(len(out)):
        if out[i] is not None:
            continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        if prev is None:
            out[i] = max(0.0, out[nxt] - 2.0)
        elif nxt is None:
            out[i] = out[prev] + 2.0
        else:
            f = (i - prev) / (nxt - prev)
            out[i] = out[prev] + (out[nxt] - out[prev]) * f
    return out

def main():
    p = argparse.ArgumentParser(description="Audio + letra -> .lrc")
    p.add_argument("audio")
    p.add_argument("letra", help="archivo .txt con la letra, una linea por renglon")
    p.add_argument("-o", "--out", help="archivo .lrc de salida")
    p.add_argument("-m", "--model", default="small",
                   help="tiny/base/small/medium/large-v3 (default: small)")
    p.add_argument("-l", "--lang", default="auto",
                   help="codigo de idioma (es, en, pt...) o 'auto' para detectarlo")
    p.add_argument("--offset", type=float, default=0.25,
                   help="segundos a adelantar cada linea, para leerla a tiempo")
    p.add_argument("--no-vad", action="store_true",
                   help="no filtrar silencios (probalo si se come estrofas)")
    p.add_argument("--mixto", action="store_true",
                   help="el tema mezcla dos idiomas: detectarlo en cada segmento")
    p.add_argument("--check", action="store_true",
                   help="solo medir el audio y salir, sin transcribir")
    p.add_argument("-s", "--separar", action="store_true",
                   help="aislar la voz con demucs antes de transcribir (tarda, pero"
                        " es lo que salva los temas con la banda fuerte)")
    p.add_argument("--forzar", action="store_true",
                   help="escribir el .lrc aunque la alineacion haya salido mal")
    p.add_argument("--demucs-modelo", default="htdemucs",
                   help="modelo de demucs: htdemucs, htdemucs_ft (mejor y mas lento),"
                        " mdx_extra")
    args = p.parse_args()

    raw = open(args.letra, encoding="utf-8").read().replace("\r", "").split("\n")
    while raw and not raw[-1].strip():
        raw.pop()
    if not raw:
        sys.exit("La letra esta vacia.")

    if args.check:
        medir(args.audio)
        return

    print(f"Transcribiendo con el modelo '{args.model}'…", file=sys.stderr)
    heard, duration = transcribe(args.audio, args.model, args.lang,
                                 not args.no_vad, args.mixto, args.separar,
                                 args.demucs_modelo)
    total = duration or (heard[-1][1] + 5 if heard else 180.0)

    times, pct = align(raw, heard)
    if pct < MINIMO and not args.forzar:
        print("", file=sys.stderr)
        print(f"Alineo solo el {pct:.0f}% de las palabras: el resultado no sirve,", file=sys.stderr)
        print("asi que no escribo el .lrc (usá --forzar si lo querés igual).", file=sys.stderr)
        print("", file=sys.stderr)
        print("Que probar, en orden:", file=sys.stderr)
        if not args.separar:
            print("  --separar          aislar la voz con demucs (lo que mas ayuda)", file=sys.stderr)
        print("  -m medium          modelo mas grande, tarda unas 3 veces mas", file=sys.stderr)
        print("  --mixto            si el tema alterna dos idiomas", file=sys.stderr)
        print("  -l es   /  -l en   si detecto mal el idioma", file=sys.stderr)
        print("", file=sys.stderr)
        print("Y revisá que la letra del .txt sea la de ESTE audio (pasa mas de lo", file=sys.stderr)
        print("que parece: otra version, un vivo, otro tema).", file=sys.stderr)
        print("Si no hay caso, sincronizá ese tema a mano en el Atril:", file=sys.stderr)
        print("cargale el audio y usá Ajustes -> Sincronizar tap a tap.", file=sys.stderr)
        sys.exit(3)

    times = monotonic_fill(times, raw, total)

    lines = []
    for line, t in zip(raw, times):
        lines.append(stamp(t - args.offset) + line if line.strip() else "")
    out = "\n".join(lines) + "\n"

    if args.out:
        open(args.out, "w", encoding="utf-8").write(out)
        print(f"Escrito {args.out}", file=sys.stderr)
        print("Revisalo en el Atril y corregi a mano lo que baile.", file=sys.stderr)
    else:
        sys.stdout.write(out)

if __name__ == "__main__":
    main()
