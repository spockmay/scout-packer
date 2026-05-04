const CACHE_NAME = 'scout-packer-v1.0.1';
const ASSETS = [
  './',
  './index.html',
  './styles.css',
  './manifest.json',
  './icon-512.png',
  './icon-192.png',
  './apple-touch-icon.png',
  './weather-sprites.png',
  './amplify_outputs.json',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
];

// 1. Install - Save the "Survival Kit"
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

// 2. Fetch - The Proxy Logic
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      // Return cached version, or go to network if not in cache
      return response || fetch(event.request);
    })
  );
});