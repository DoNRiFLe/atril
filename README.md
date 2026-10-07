# Atril

Las letras de tus temas en una tablet, para leerlas mientras tocás.

- **Modo atril**: la letra baja sola, a la velocidad que le pongas.
- **Modo karaoke**: si el tema tiene tiempos, resalta la línea actual y la
  centra en pantalla.
- Tamaño de letra a botón, a slider o pellizcando con dos dedos.
- Funciona **sin internet**: se instala en la tablet como una app.
- Los temas se guardan en el dispositivo, con respaldo a un archivo o
  sincronización con Google Drive.

Todo vive en un solo `index.html`, sin frameworks ni build.

## Usarlo

La forma cómoda es abrirlo desde su dirección web y, en la tablet, usar
**Agregar a pantalla de inicio**. Queda con ícono propio, abre en pantalla
completa y anda en modo avión.

Para probarlo en la máquina, alcanza con abrir `index.html` con doble clic, o:

```bash
node tools/servir.js
```

que además te dice la dirección para entrar desde la tablet por la misma wifi.

## Cargar un tema

**☰ Temas → + Nuevo**: título, artista y la letra pegada, un renglón por línea
(los renglones vacíos son pausas). Opcionalmente, el audio del tema.

## Ponerle los tiempos

**Con el audio cargado**, ⚙ → *Sincronizar tap a tap*: el primer toque arranca
el tema, y después marcás una vez por línea. Tres minutos y queda clavado.
El ↶ deshace y rebobina para volver a escuchar esa parte.

**Automático**, con Whisper: ver [tools/README.md](tools/README.md). Anda bien
con voces limpias; con la banda encima conviene el tap a tap.

También podés importar y exportar `.lrc`, que es el formato estándar de
karaoke: en el editor de cada tema la letra se ve con sus `[mm:ss.cc]` adelante
y se corrigen a mano.

## Controles

| | |
|---|---|
| Tocar la pantalla | Pausa / sigue |
| Tocar una línea | Salta a ese momento |
| Doble toque | Pantalla completa |
| Pellizcar | Tamaño de letra |
| Espacio | Pausa / sigue (y marca, al sincronizar) |
| ↑ ↓ | Velocidad del autoscroll |
| ← → | ±5 segundos |
| + − | Tamaño de letra |
| F | Pantalla completa |

Las flechas y el espacio sirven para manejarlo con una pedalera Bluetooth de
las que pasan páginas, sin sacar las manos del instrumento.

## Sincronizar con Google Drive

Opcional, para que la tablet y la computadora compartan los mismos temas.
Necesita un Client ID propio: los pasos están dentro de la app, en
⚙ → *Google Drive* → *Configurar Client ID*.

Usa el scope `drive.appdata`, o sea una carpeta privada que sólo ve esta app.
No puede leer ni tocar el resto de tus archivos.

## Publicarlo

Cualquier hosting estático sirve. Con GitHub Pages: *Settings* → *Pages* →
*Deploy from a branch* → `main` / `root`.

El contenido que cargues (letras, audios, tiempos) queda en tu dispositivo:
no se sube al repositorio ni a ningún servidor.
