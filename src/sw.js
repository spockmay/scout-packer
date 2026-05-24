const CACHE_NAME = 'scout-packer-v1.1.0';
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
  'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js',
  'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css'
];

// 1. Install - Save the "Survival Kit"
self.addEventListener('install', (event) => {
  self.skipWaiting(); // Forces the waiting service worker to become active
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

// delete the old cache when a new one is found
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('Clearing old cache:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
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
