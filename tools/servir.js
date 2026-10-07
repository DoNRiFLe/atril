#!/usr/bin/env node
// Servidor estatico minimo para el Atril. Sin dependencias: no hace falta
// npm install. Sirve la carpeta public/ y abre en letras.html.
//
//   node tools/servir.js [puerto]

const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PUERTO = Number(process.argv[2] || process.env.PORT || 3000);
const RAIZ = path.join(__dirname, '..');

const TIPOS = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp',
  '.ico': 'image/x-icon', '.woff2': 'font/woff2',
  '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.ogg': 'audio/ogg',
  '.wav': 'audio/wav', '.webm': 'audio/webm',
};

const servidor = http.createServer((req, res) => {
  let rel = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (rel === '/') rel = '/index.html';

  // nada de salir de public/
  const destino = path.join(RAIZ, path.normalize(rel).replace(/^(\.\.[/\\])+/, ''));
  if (!destino.startsWith(RAIZ)) {
    res.writeHead(403).end('Prohibido');
    return;
  }

  fs.stat(destino, (err, st) => {
    if (err || !st.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
         .end('No existe: ' + rel);
      return;
    }
    res.writeHead(200, {
      'Content-Type': TIPOS[path.extname(destino).toLowerCase()] || 'application/octet-stream',
      'Content-Length': st.size,
      'Cache-Control': 'no-cache',
    });
    fs.createReadStream(destino).pipe(res);
  });
});

servidor.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.error(`\nEl puerto ${PUERTO} ya esta ocupado.`);
    console.error(`Probá con otro:  node tools/servir.js 3001\n`);
  } else {
    console.error('\nError:', e.message, '\n');
  }
  process.exit(1);
});

servidor.listen(PUERTO, '0.0.0.0', () => {
  console.log('\n  Atril andando. Abrí en el navegador:\n');
  console.log(`    http://localhost:${PUERTO}`);
  for (const [, addrs] of Object.entries(os.networkInterfaces())) {
    for (const a of addrs || []) {
      if (a.family === 'IPv4' && !a.internal) {
        console.log(`    http://${a.address}:${PUERTO}/letras.html   (desde la tablet, misma wifi)`);
      }
    }
  }
  console.log('\n  Para Google Drive registrá este origen en Google Cloud Console:');
  console.log(`    http://localhost:${PUERTO}`);
  console.log('\n  Ctrl+C para cortar.\n');
});
