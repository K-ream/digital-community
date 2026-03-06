/* Service Worker for Digital Community - Performance Optimization */
const CACHE_NAME = 'digital-community-v1.0.0';
const STATIC_CACHE_URLS = [
  '/',
  'index.html',
  'ai-events.html',
  'projects.html',
  'dashboard.html',
  'leaderboard.html',
  'exchange.html',
  'governance.html',
  'manifesto.html',
  'city.html',
  'apply.html',
  'login.html',
  'profile.html',
  'admin.html'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('OpenClaw: Caching static assets');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME) {
              console.log('OpenClaw: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip external requests
  if (!event.request.url.includes(self.location.origin)) return;
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request)
          .then(fetchResponse => {
            // Cache the fetched response
            const responseClone = fetchResponse.clone();
            caches.open(CACHE_NAME)
              .then(cache => cache.put(event.request, responseClone));
            return fetchResponse;
          })
          .catch(() => {
            // Offline fallback for HTML pages
            if (event.request.destination === 'document') {
              return caches.match('index.html');
            }
          });
      })
  );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Handle offline actions when connection restored
  console.log('OpenClaw: Background sync triggered');
}