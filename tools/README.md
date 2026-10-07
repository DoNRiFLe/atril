# Alineador de letras (audio → .lrc)

Genera los tiempos de karaoke a partir del audio de la canción y la letra que ya
tenés. Corre entero en tu máquina: no sube nada a ningún servicio.

## Instalar (una sola vez)

Antes que nada: clonalo en tu carpeta de usuario, **no** en `C:\Windows\system32`
ni en `Program Files`. Ahí Windows pide permisos de administrador y varias cosas
fallan sin decir por qué.

**Windows**

```powershell
cd $HOME
git clone -b main https://github.com/DoNRiFLe/atril
cd atril
powershell -ExecutionPolicy Bypass -File tools\instalar-alineador.ps1
```

Si no tenés Python, el script te ofrece instalarlo con `winget`. Después de eso
hay que **cerrar y volver a abrir PowerShell** (el PATH no se refresca en la
sesión abierta) y correr el instalador de nuevo.

**Linux / Mac**

```bash
python3 -m venv .venv-alineador
.venv-alineador/bin/pip install -r tools/requirements.txt
```

Necesitás Python 3.9 o más nuevo. La primera corrida además baja el modelo de
Whisper (unos 500 MB con `small`) y lo deja cacheado.

## Usar

En Windows, arrastrá el audio sobre `tools\alinear.bat`. Tiene que haber al lado
un `.txt` con la letra y el mismo nombre (`tema.mp3` → `tema.txt`), y te deja el
`tema.lrc` en la misma carpeta.

A mano, en cualquier sistema:

```bash
.venv-alineador/bin/python tools/alinear.py tema.mp3 tema.txt -o tema.lrc -m small
```

Después, en el Atril: **☰ Temas → Importar** y elegís el `.lrc`.

### Opciones que importan

| Flag | Para qué |
|---|---|
| `-m tiny\|base\|small\|medium\|large-v3` | Modelo. `small` es el equilibrio razonable; `medium` mejora con música fuerte y tarda ~3× más. |
| `--offset 0.4` | Adelanta cada línea esa cantidad de segundos, para llegar a leerla. Default 0.25. |
| `--no-vad` | Probalo si se saltea estrofas enteras. |
| `-l auto` | Idioma. Por defecto lo detecta solo; forzalo (`-l es`, `-l en`) si se equivoca. |
| `--mixto` | El tema alterna español e inglés: re-detecta el idioma en cada estrofa. |
| `--check` | No transcribe: solo mide el archivo (formato, pico, RMS) para descartar que esté mudo o dañado. |
| `-s`, `--separar` | Aísla la voz con demucs antes de transcribir. Es lo que salva los temas donde la banda tapa la voz. |
| `--demucs-modelo htdemucs_ft` | Modelo de separación más prolijo y bastante más lento que el default (`htdemucs`). |

El script te imprime el idioma que detectó y qué porcentaje de palabras logró
alinear. Por debajo de 60%
no te fíes: revisá el resultado o sincronizá ese tema a mano desde el Atril
(⚙ → Sincronizar tap a tap, que con el audio cargado sale clavado).

### Tiempos aproximados en CPU

Un tema de 4 minutos: `tiny` ~30 s, `small` ~2 min, `medium` ~6 min.
Con GPU NVIDIA es entre 5 y 10 veces más rápido — instalá
`pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` y en `tools/alinear.py` cambiá
`device="cpu", compute_type="int8"` por `device="cuda", compute_type="float16"`.

## Levantar el Atril

Doble clic en **`tools\servir.bat`**, o desde la consola:

```bash
node tools/servir.js
```

No necesita `npm install`: es un servidor estático de Node puro, sin
dependencias. Te imprime la URL de `localhost` y también la de tu IP en la red,
para abrirlo desde la tablet estando en la misma wifi. Si el puerto 3000 está
ocupado, pasale otro: `node tools/servir.js 3001`.

Para el uso normal del atril no hace falta nada de esto: podés abrir
`index.html` con doble clic y funciona todo, incluido cargar el audio y
sincronizar. El servidor sólo hace falta para Google Drive, porque Google no
permite login OAuth desde `file://`.

El origen `http://localhost:3000` es el que va en *Orígenes autorizados de
JavaScript* al crear el Client ID en Google Cloud Console. Ojo: Google **no
acepta IPs privadas** como origen, así que para usar Drive desde la tablet hay
que publicar la app (Vercel, Cloudflare Pages, GitHub Pages) y registrar esa
URL. Por la IP de la red el atril funciona igual, pero sin sincronización.

## Aislar la voz (demucs)

Para los temas donde la banda tapa la voz, el paso que de verdad cambia el
resultado es separar la pista vocal antes de transcribir. El instalador te
ofrece instalar demucs; si lo salteaste:

```powershell
.venv-alineador\Scripts\python.exe -m pip install demucs
```

Se trae PyTorch, unos 2,5 GB.

Después, arrastrá el audio sobre **`tools\alinear-voz-aislada.bat`** en vez del
`.bat` normal. O a mano, con `--separar`:

```powershell
.venv-alineador\Scripts\python.exe tools\alinear.py temas\tema.mp3 temas\tema.txt -o temas\tema.lrc --separar
```

La voz aislada queda cacheada al lado del audio como `<nombre>.vocals.wav`, así
si volvés a alinear ese tema no se separa de nuevo. Los tiempos que salen valen
igual para el mp3 original: el Atril sigue reproduciendo tu archivo.

Tiempos en CPU, por cada tema de 4 minutos: separar tarda entre 3 y 8 minutos
según la máquina, más lo que tarde Whisper después.

Si demucs ya está instalado, el script lo usa **solo** cuando la transcripción
normal no reconoce ninguna palabra — así no pagás la espera en los temas que
salen bien de una.

## Cuando no reconoce nada

El orden para descartar:

1. `--check` sobre el archivo. Si el RMS da por debajo de -50 dBFS, el problema
   es el mp3, no Whisper.
2. `--separar` (ver arriba). Es lo que más mueve la aguja.
3. `-m medium` o `-m large-v3`. Tarda 3 y 10 veces más respectivamente.
4. Rendirse con ese tema y sincronizarlo a mano en el Atril: cargale el audio
   en el editor y usá ⚙ → Sincronizar tap a tap. Son 3 minutos y queda mejor
   que cualquier alineación dudosa.

Voces muy comprimidas, gritadas o con mucha distorsión encima (garage, punk,
metal) son el peor caso para Whisper. No es que esté mal configurado.

## Pasar los temas a la tablet

El respaldo lleva las letras y los tiempos, **no los audios** (los mp3 quedan
guardados aparte, en cada dispositivo). Para tocar en vivo no hacen falta: le
das ▶ cuando arranca la banda y la letra corre sola.

### Si la tablet está en la misma wifi que la PC

1. En la PC, en el Atril: **☰ Temas → Exportar todo**. Te baja
   `atril-respaldo.json`.
2. Copiá ese archivo dentro de `public/`.
3. Levantá el servidor: `node tools/servir.js`. Te imprime la dirección de tu
   PC en la red, algo tipo `http://192.168.1.50:3000/index.html`.
4. En la tablet abrí esa dirección y andá a **☰ Temas → Importar de una URL**.
   La que te propone por defecto ya es la correcta; aceptás y listo.

### Para que funcione sin internet ni PC

El Atril es una PWA: una vez abierto desde una dirección `https://`, queda
instalado en la tablet y funciona sin conexión.

1. Publicá la carpeta del repo en cualquier hosting estático gratuito
   (Cloudflare Pages, Vercel o GitHub Pages sirven; los dos primeros aceptan
   arrastrar la carpeta y listo).
2. En la tablet abrí esa URL con Chrome y usá **Agregar a pantalla de inicio**.
3. Importá los temas una vez (por URL, o con el `.json` descargado).

Queda con ícono propio, abre en pantalla completa sin barra del navegador, y
anda en modo avión. Los temas viven en la tablet.

Conviene publicarlo aunque sea por esto: si abrís el Atril por la IP de la PC,
los temas quedan guardados contra esa dirección, y el día que el router te dé
otra IP la tablet aparece vacía. Con una URL fija eso no pasa. Y es la misma
URL que después registrás en Google Cloud Console para que sincronice con Drive.
