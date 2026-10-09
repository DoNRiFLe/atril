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
  avión. Las únicas excepciones, todas a pedido y sin las que la app sigue
  andando:
  - YouTube: la IFrame API, que se carga sólo si el tema tiene un link, y el
    oEmbed (`datosDeYt()`), que se consulta al pegar un link para completar
    título y banda.
  - LRCLIB (`buscarLetra()`): con *Buscar letra*, o sola después de completar
    con YouTube si la letra está vacía. Le llegan el título y la banda, nada
    más. Genius no deja leer sus letras desde otra página (ni sus términos
    permiten sacarlas): sólo se abre su búsqueda en el navegador.
- **Español argentino en toda la interfaz**, incluidos los mensajes de error.
- **Los datos son del usuario y viven en su dispositivo.** No se mandan a
  ningún servidor que no sea el Drive del propio usuario.

## Cómo está armado

| Dónde | Qué |
|---|---|
| `index.html` | La app entera |
| `atril-sw.js` | Service worker: red primero, caché de respaldo. **Subir `CACHE` cuando cambie `index.html`**, siempre con la forma `'atril-vN'`: la app lee ese número para mostrar la versión y avisar si hay una nueva |
| `atril.webmanifest` + `atril-*.png` | PWA, para instalarla en la tablet |
| `tools/alinear.py` | Audio + letra → `.lrc`, con Whisper. Opcional, corre local |
| `tools/servir.js` | Servidor estático de Node puro, sin dependencias |

### Dónde vive cada cosa

- **Temas** (letras, tiempos, metadatos): `localStorage`, clave `atril.data.v2`.
- **Velocidad del autoscroll**: por tema, `song.speed` (si no tiene, `prefs.speed`).
  Leerla siempre con `velocidad()` y cambiarla con `setVelocidad()`.
- **Lista del show**: `data.show = {ids, updatedAt}`, dentro de `atril.data.v2`.
  Viaja entera en el respaldo y en Drive y gana la más nueva: no se mezcla tema
  por tema. Puede tener ids de temas borrados; `showList()` los filtra.
- **Audios**: IndexedDB, base `atril`, store `audio`, con el id del tema de
  clave. No van en `localStorage` ni en el respaldo `.json`.
- **Preferencias**: `localStorage`, `atril.prefs.v2`.
- **Drive**: `localStorage`, `atril.gdrive.v1`. Scope `drive.appdata`, o sea
  una carpeta privada que sólo ve esta app. El Client ID lo pone el usuario
  desde la interfaz: **nunca hardcodear credenciales**.
- **PIN del respaldo**: `localStorage`, `atril.pin.v1` (salt vigente,
  iteraciones y `desde`). Las claves AES que salen del PIN, no exportables, en
  IndexedDB `atril` (versión 2), store `claves`, por salt; las viejas quedan
  para abrir respaldos anteriores. **El PIN no se guarda.**

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

### Marcas de canto

Van **dentro del texto** de `song.lines`, no en un campo aparte: así viajan con
Drive, el respaldo, el PIN y el `.lrc` sin tocar el formato. Son símbolos donde
aplican (`↗ ↘ ⤴ ⤵ ～ ➰ ‖`, ver `MARCAS`) y el prefijo `(p) ` para piano; en el
editor el prefijo va después de los `[mm:ss.cc]`. Las escaleritas son de tres
caracteres (`▁▃▅` / `▅▃▁`) y en el atril se dibujan con un SVG (`ESCALERA`):
como texto salían como barras pesadas. `pintarLinea()` las dibuja con color, y
todo lo que compara letra (la búsqueda) tiene que pasar por `sinMarcas()`.

### Dos líneas siempre a la vista

Pedido del usuario: aunque la banda se pierda, tiene que ver la línea actual y
la que viene. Por eso la actual se ubica al 10% de la pantalla (`centrar()`) y
`ajustarFs()` topea la letra para que la actual y la siguiente entren juntas en
el 85% del alto (el máximo pedido es 200 px).
El tamaño que se ve (`fsEf`) puede ser menor que el pedido (`prefs.fs`); A+, A−
y el pellizco parten de `fsEf`. Se recalcula al cambiar de tema y con un
`ResizeObserver` sobre `#stage` (girar la tablet, pantalla completa).

Con karaoke o sincronizando hay una línea **intro** (`introEl`) antes de la 1ª,
fuera de `lineEls`: es la actual mientras `active === -1` (`elDe(-1)`), y al
tocar muestra cuántos segundos faltan para entrar.

**Modo show** (`body.show`): el tema actual está en la lista del show. La barra
de abajo se agranda, pierde el deslizador de velocidad y suma una pausa grande
(`#btnPlay2`); los temas de autoscroll tienen 🐢 / 🐇 (`#velShow`).

**Pantalla encendida** (`prefs.wake`): el wake lock se pide mientras la app está
a la vista (`wakeSegun()`), no sólo mientras corre un tema: entre tema y tema
la tablet no se tiene que bloquear en el show.
En pantalla completa (`body.zen`) se va sólo la barra de arriba. El ⛶ de la
lista (`#btnFull`) pone sólo la pantalla completa del navegador; `zenFull`
recuerda si la pidió el zen, para que salir del zen no devuelva las pestañas.

### Sincronización con Drive

Merge por tema según `updatedAt`, no reemplazo del archivo entero. Los borrados
van con tombstone (`deleted: true`) para que se propaguen en vez de resucitar
en el próximo merge. Toda escritura que deba sincronizarse tiene que tocar
`updatedAt` del tema y llamar a `saveData(true)`.

Con PIN puesto, `atril.json` y el `.json` exportado van cifrados (PBKDF2 +
AES-GCM, sobre `{atril:'cifrado', v:1, salt, iter, desde, iv, datos}`); en el
dispositivo todo sigue en claro. Entre dispositivos gana el PIN cambiado
último (`desde`, o `pinDesde` en la copia sin cifrar). Las sincronizaciones
automáticas nunca piden el PIN: si hace falta, abortan sin subir nada. **Con PIN
puesto nunca se sube ni se exporta en claro** salvo con *Exportar sin cifrar*.

## Errores ya cometidos, para no repetirlos

- **Escribir un `.lrc` cuando la alineación salió mal.** Un archivo con tiempos
  interpolados parece válido y no sirve. `alinear.py` ahora aborta por debajo
  del 35% de palabras alineadas.
- **Que el primer tap de sincronización marcara la línea 1.** Arrancar el audio
  y marcar eran el mismo toque, así que la intro instrumental se comía la
  primera línea.
- **Resaltar con los tiempos viejos mientras se sincroniza.** Al re-sincronizar
  un tema que ya tenía tiempos, `tick()` y `seek()` seguían marcando líneas
  solas. Sincronizando, sólo el toque marca: los dos lo chequean con `syncing`.
- **Que una pausa en medio de la sincronización volviera a 0:00.** El "primer
  toque arranca" se aplicaba a cualquier toque con la reproducción parada, así
  que si se pausaba el video, el siguiente toque reiniciaba el tema. Ahora, con
  líneas ya marcadas, el toque sigue desde donde está. Además el avance se
  guarda con cada toque (`localStorage`, `atril.sync.v1`) y se puede seguir
  desde una línea (`seguirDesde()`) o desde donde quedó un guardado a medias
  (`corteGuardado()`).
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
