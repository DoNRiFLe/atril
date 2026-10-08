# Atril

Las letras de tus temas en una tablet, para leerlas mientras tocás.

- **Modo atril**: la letra baja sola, a la velocidad que le pongas.
- **Modo karaoke**: si el tema tiene tiempos, resalta la línea actual y deja
  entera a la vista la que viene.
- **Lista del show**: el orden de los temas para tocar, y se pasa de uno a otro
  con un botón o un pedal Bluetooth.
- Tamaño de letra a botón, a slider o pellizcando con dos dedos. Nunca tan
  grande que no entren dos líneas.
- Funciona **sin internet**: se instala en la tablet como una app.
- Los temas se guardan en el dispositivo, con respaldo a un archivo o
  sincronización con Google Drive.

Todo vive en un solo `index.html`, sin frameworks ni build.

## Usarlo

La forma cómoda es abrirlo desde su dirección web y, en la tablet, usar
**Agregar a pantalla de inicio**. Queda con ícono propio, abre en pantalla
completa y anda en modo avión.

### Dejarlo listo para tocar sin internet

1. Con wifi, abrí la dirección https donde está publicado (por ejemplo
   `https://donrifle.github.io/atril/`) e instalalo: menú ⋮ → *Agregar a
   pantalla de inicio*.
2. Todavía con wifi, cargá los temas (☁ desde Drive, o *Importar*) y abrí una
   vez los que tienen audio, para que el audio quede en la tablet.
3. ⚙ → *Sin internet* tiene que decir *Lista*. Desde ahí abrilo siempre con el
   ícono.

Los temas quedan guardados **por dirección**: lo que cargues entrando por
`http://192.168.x.x:3000` no aparece en la de GitHub, y al revés. Usá siempre la
misma. Los videos de YouTube son lo único que necesita conexión; sin ella, el
karaoke sigue con el reloj interno.

### En la computadora

Para probarlo, alcanza con abrir `index.html` con doble clic, o:

```bash
node tools/servir.js
```

que además te dice la dirección para entrar desde la tablet por la misma wifi.
Esa dirección es `http://`, y por ahí el navegador no lo deja instalado para
usar sin internet: sirve para probar, no para el show.

## Cargar un tema

**☰ Temas → + Nuevo**: título, artista y la letra pegada, un renglón por línea
(los renglones vacíos son pausas). Opcionalmente, el audio del tema o un link
de YouTube.

Si pegás el link de YouTube con el título o el artista vacíos, los completa
solo con el nombre del video (sacando lo de "Official Video", "Karaoke
Version" y parecidos). Algunos canales ponen el tema antes que la banda: si
quedó al revés, **⇄ Invertir**. Lo que ya escribiste no lo toca.

### Buscar la letra

**🔎 Buscar letra** la busca en [LRCLIB](https://lrclib.net), una base abierta
de letras, con el título y la banda del tema. Si pegaste un link de YouTube y
la letra está vacía, la busca sola. Cuando la encuentra elegís:

- **Pegar con tiempos**: queda lista para karaoke. Los tiempos son los de la
  grabación original; con un video de karaoke con otra intro o tocando en vivo
  pueden quedar corridos, y se ajustan con el tap a tap.
- **Pegar solo la letra**.

Si no está, **Buscar en Genius** abre la búsqueda en el navegador para copiarla
a mano. Al buscar, a LRCLIB le llegan sólo el título y la banda. Las letras
tienen derechos de autor: son para usarlas vos, no para publicarlas.

## Ponerle los tiempos

**Con el audio cargado**, ⚙ → *Sincronizar tap a tap*: el primer toque arranca
el tema y queda en la **intro**; recién cuando entra la voz tocás para la 1ª
línea, y después una vez por línea. Tres minutos y queda clavado. El ↶ deshace
y rebobina para volver a escuchar esa parte.

Al tocar, mientras dura la intro arriba dice *♪ Intro · entrás en 5 s*, con la
cuenta regresiva hasta la primera línea.

**Automático**, con Whisper: ver [tools/README.md](tools/README.md). Anda bien
con voces limpias; con la banda encima conviene el tap a tap.

También podés importar y exportar `.lrc`, que es el formato estándar de
karaoke: en el editor de cada tema la letra se ve con sus `[mm:ss.cc]` adelante
y se corrigen a mano.

## Marcas de canto

En el editor del tema, arriba de la letra, hay una fila de botones para marcar
cómo se canta cada parte. Ponés el cursor justo donde va y tocás la marca:

| | |
|---|---|
| ↗ / ↘ | La línea sube / baja |
| Escalerita arriba / abajo | Sube / baja escalonado, nota por nota |
| ⤴ / ⤵ | El final va para arriba / para abajo |
| ～ | Alargar |
| ➰ | Rulo |
| ‖ | Respirar |
| **p** | En piano |

**Piano** va por línea: con el cursor en una línea la marca a ella sola; para
una estrofa entera, la seleccionás y tocás *piano*. Tocarlo otra vez lo saca.
En el atril, cada marca sale con su color y las líneas en piano llevan una
barra violeta al costado.

Las marcas son parte de la letra: viajan con Drive, el respaldo y el `.lrc`, y
no cambian los tiempos del karaoke. Se borran como cualquier letra.

## Lista del show

**☰ → Todos los temas**: tocá **+** en cada tema, en el orden del show. En
**Lista del show** los movés de a un lugar con **▲ ▼** (o arrastrando desde
**≡**) y los sacás con **−**. En *Todos los temas*, **🗑** borra el tema, con
confirmación.

Si el tema que estás viendo es del show, ⏮ ⏭ (y el pedal) siguen ese orden;
arriba dice en cuál vas (*show 3/12*) y al final de la letra, cuál sigue.
Tocando ese *Sigue:* pasás directo. La lista viaja con el respaldo y con Drive.

Mientras estás en un tema del show, la barra de abajo se agranda para usarla
sin mirar: sin la velocidad, con ⏮ ⏭ y un botón grande de pausa. ☰ abre directo
la lista del show, con el tema actual a la vista. En pantalla completa la barra
de abajo sigue estando, con **✕ Salir** para volver.

## Controles

| | |
|---|---|
| Tocar la pantalla | Pausa / sigue |
| Tocar una línea | Salta a ese momento: si la banda se adelantó o se atrasó, el karaoke se reengancha desde ahí |
| Tocar *Sigue: …* | Pasa al tema siguiente del show |
| Tocar *♪ Intro* | Vuelve al principio del tema |
| Doble toque | Pantalla completa |
| Pellizcar | Tamaño de letra |
| Espacio | Pausa / sigue (y marca, al sincronizar) |
| ↑ ↓ | Velocidad del autoscroll |
| ← → | ±5 segundos |
| + − | Tamaño de letra |
| F | Pantalla completa |
| Avanzar / Retroceder página | Tema siguiente / anterior (y marca / deshace, al sincronizar) |

### Pedal o control Bluetooth

Los pedales pasa-páginas mandan *Avanzar página* y *Retroceder página*, así
que cambian de tema sin configurar nada. Los que mandan flechas o espacio
también sirven, con lo de la tabla de arriba.

Para cualquier otro control: ⚙ → *Control o pedal Bluetooth* → *Aprender*, y
apretás su botón; desde ahí ese botón pasa al tema siguiente. Si no aparece
nada, la tecla no le llega al navegador. Es lo que pasa con los controles de
selfie (como el del trípode Xiaomi): mandan *subir volumen*, y Android casi
siempre se queda con esa tecla. En ese caso hace falta un pasador de páginas
Bluetooth, o una app que remapee el botón.

## Sincronizar con Google Drive

Opcional, para que la tablet y la computadora compartan los mismos temas.
Necesita un Client ID propio: los pasos están dentro de la app, en
⚙ → *Google Drive* → *Configurar Client ID*.

Usa el scope `drive.appdata`, o sea una carpeta privada que sólo ve esta app.
No puede leer ni tocar el resto de tus archivos.

## Respaldo cifrado con PIN

Opcional. Con ⚙ → *Respaldo cifrado* → *Poner PIN*, el `.json` que exportás y
la copia de Drive se guardan cifrados (AES-256, con una clave que sale del
PIN). Sin el PIN no se pueden leer.

- En el dispositivo las letras siguen a la vista: para tocar no se pide nada.
- El PIN no se guarda en ningún lado. Cada dispositivo lo pide una vez y se
  queda con la clave.
- Si lo cambiás o lo sacás en un dispositivo, los demás se enteran al
  sincronizar con Drive (y, si es nuevo, te lo piden).
- **Si te olvidás el PIN, lo cifrado no se recupera.** Los temas siguen en cada
  dispositivo, y la copia de Drive se puede reemplazar con *No me acuerdo el
  PIN*, que te pide uno nuevo.
- Hace falta abrir el Atril por https o desde `localhost`: por `http://` con la
  IP de la PC (`servir.js` por wifi) el navegador no deja cifrar. Para pasar un
  respaldo por ese camino, usá *Exportar sin cifrar*.
- Los audios que se suben a Drive no se cifran.

## Publicarlo

Cualquier hosting estático sirve. Con GitHub Pages: *Settings* → *Pages* →
*Deploy from a branch* → `main` / `root`.

El contenido que cargues (letras, audios, tiempos) queda en tu dispositivo:
no se sube al repositorio ni a ningún servidor.
