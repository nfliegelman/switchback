const SHELL = 'sb-shell-v3610';
self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(
    ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'])));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(
    ks.filter(k => k.startsWith('sb-shell-') && k !== SHELL).map(k => caches.delete(k))
  )).then(() => clients.claim()));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  if (u.pathname.includes('/areas/')) {
    e.respondWith(caches.open('sb-areas').then(async c => {
      const hit = await c.match(e.request);
      const refresh = fetch(e.request).then(r => { if (r.ok) c.put(e.request, r.clone()); return r; }).catch(() => null);
      return hit || refresh.then(r => r || new Response('{}', {status: 503}));
    }));
  } else if (u.pathname.endsWith('board.json')) {
    e.respondWith(fetch(e.request).then(r => {
      caches.open(SHELL).then(c => c.put(e.request, r.clone())); return r;
    }).catch(() => caches.match(e.request)));
  } else {
    e.respondWith(caches.match(e.request).then(h => h || fetch(e.request)));
  }
});
