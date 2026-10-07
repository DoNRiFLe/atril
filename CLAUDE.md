# Atril — contexto del proyecto

App para leer las letras de los temas en una tablet colgada del micrófono,
mientras se toca. Dario es el único desarrollador y el único usuario.

Publicada en **https://donrifle.github.io/atril/** desde `main`, con el
workflow `.github/workflows/pages.yml`. Push a `main` = publicado en ~2 minutos.

## Lo que no se negocia

- **Un solo archivo.** Toda la app es `index.html`: HTML, CSS y JS vanilla.
  Sin frameworks, sin build, sin `npm install`. Se tiene que poder abrir con
  doble clic y funcionar.
- **Sin dependencias de red en runtime.** Nada de CDNs: la app arranca en modo
  avión. La única excepción es la IFrame API de YouTube, que se carga sólo si
  el tema tiene un link, y si falla la app sigue andando.
- **Español argentino en toda la interfaz**, incluidos los mensajes de error.
- **Los datos son del usuario y viven en su dispositivo.** No se mandan a
  ningún servidor que no sea el Drive del propio usuario.

## Cómo está armado

| Dónde | Qué |
|---|---|
| `index.html` | La app entera |
| `atril-sw.js` | Service worker: red primero, caché de respaldo. **Subir `CACHE` cuando cambie `index.html`** |
| `atril.webmanifest` + `atril-*.png` | PWA, para instalarla en la tablet |
| `tools/alinear.py` | Audio + letra → `.lrc`, con Whisper. Opcional, corre local |
| `tools/servir.js` | Servidor estático de Node puro, sin dependencias |

### Dónde vive cada cosa

- **Temas** (letras, tiempos, metadatos): `localStorage`, clave `atril.data.v2`.
- **Audios**: IndexedDB, base `atril`, store `audio`, con el id del tema de
  clave. No van en `localStorage` ni en el respaldo `.json`.
- **Preferencias**: `localStorage`, `atril.prefs.v2`.
- **Drive**: `localStorage`, `atril.gdrive.v1`. Scope `drive.appdata`, o sea
  una carpeta privada que sólo ve esta app. El Client ID lo pone el usuario
  desde la interfaz: **nunca hardcodear credenciales**.

### El reloj del karaoke

Hay tres fuentes, en este orden: **archivo de audio local** (`<audio>`),
**video de YouTube** (`getCurrentTime()`), y si no hay ninguna, un
**cronómetro interno** que corre con `requestAnimationFrame`.

`hasAudio()` dice si hay fuente externa; `esYt()` distingue cuál. Cualquier
cambio en play/pausa/seek tiene que contemplar los tres casos.

Los tiempos se guardan por línea, en segundos, en `song.timings` (paralelo a
`song.lines`, con `null` en las líneas vacías). El formato de intercambio es
LRC estándar, que el editor muestra y acepta.

El **adelanto** (`prefs.lead`) se aplica al reproducir, no al grabar: así se
ajusta sin volver a sincronizar.

### Sincronización con Drive

Merge por tema según `updatedAt`, no reemplazo del archivo entero. Los borrados
van con tombstone (`deleted: true`) para que se propaguen en vez de resucitar
en el próximo merge. Toda escritura que deba sincronizarse tiene que tocar
`updatedAt` del tema y llamar a `saveData(true)`.

## Errores ya cometidos, para no repetirlos

- **Escribir un `.lrc` cuando la alineación salió mal.** Un archivo con tiempos
  interpolados parece válido y no sirve. `alinear.py` ahora aborta por debajo
  del 35% de palabras alineadas.
- **Que el primer tap de sincronización marcara la línea 1.** Arrancar el audio
  y marcar eran el mismo toque, así que la intro instrumental se comía la
  primera línea.
- **El VAD de Whisper calibrado para voz hablada** descartaba temas enteros con
  la banda sonando. Va con `threshold` bajo y reintento sin filtro.
- **Dar por hecho que el usuario tiene algo instalado.** Los scripts de Windows
  validan que Python exista de verdad (el stub de la Microsoft Store miente) y
  van con BOM UTF-8, porque PowerShell 5.1 los lee como ANSI y rompe los acentos.

## Qué no hacer

- **No bajar audio de YouTube.** Los términos del servicio lo prohíben. Para
  tomar tiempos de un video se usa el player embebido y sincronización manual.
- **No prometer login en una página estática.** No hay servidor que valide nada;
  cualquier contraseña en el cliente se lee con Ctrl+U. Si hace falta proteger
  algo, se cifran los datos en el dispositivo con WebCrypto y se avisa que
  perder el PIN es perder los datos.
- **No reproducir letras con copyright** en el repo, los ejemplos ni los tests.
  Las letras las carga el usuario y quedan en su dispositivo; `.gitignore` deja
  afuera `temas/`, `*.mp3` y `*.lrc`.

## Al tocar `index.html`

1. Verificar que el JS parsea (`node --check` sobre el bloque `<script>`).
2. Subir `CACHE` en `atril-sw.js`, o las tablets siguen con la versión vieja.
3. Probar con `node tools/servir.js` antes de pushear.
