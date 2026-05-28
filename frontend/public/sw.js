// Service Worker for cache management
const CACHE_NAME = 'ai-advertising-platform-v1';
const DYNAMIC_CACHE_NAME = 'ai-advertising-platform-dynamic-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/version.json'
];

// Install event - cache resources
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        // 强制激活新的service worker
        return self.skipWaiting();
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  
  // 跳过非HTTP/HTTPS协议的请求（如chrome-extension等）
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // 不缓存 API 请求和认证请求
  if (url.pathname.includes('/api/') || url.pathname.includes('/auth/')) {
    event.respondWith(fetch(request));
    return;
  }
  
  // 对于version.json，总是从网络获取最新版本
  if (url.pathname === '/version.json') {
    event.respondWith(
      fetch(request, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      }).catch(() => {
        // 如果网络请求失败，尝试从缓存获取
        return caches.match(request);
      })
    );
    return;
  }
  
  // 对于静态资源，使用缓存优先策略
  event.respondWith(
    caches.match(request)
      .then(response => {
        if (response) {
          // 如果缓存中有，返回缓存版本
          return response;
        }
        
        // 如果缓存中没有，从网络获取并缓存
        return fetch(request).then(fetchResponse => {
          // 只缓存成功的响应和同源请求
          if (!fetchResponse || 
              fetchResponse.status !== 200 || 
              fetchResponse.type !== 'basic' ||
              !url.protocol.startsWith('http')) {
            return fetchResponse;
          }
          
          // 克隆响应，因为响应是流，只能使用一次
          const responseToCache = fetchResponse.clone();
          
          // 安全地缓存响应
          caches.open(DYNAMIC_CACHE_NAME)
            .then(cache => {
              try {
                cache.put(request, responseToCache);
              } catch (error) {
                console.warn('缓存失败:', error);
              }
            })
            .catch(error => {
              console.warn('打开缓存失败:', error);
            });
          
          return fetchResponse;
        }).catch(error => {
          console.warn('网络请求失败:', error);
          return new Response('网络错误', { status: 503 });
        });
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // 立即控制所有客户端
      return self.clients.claim();
    })
  );
});

// 监听消息，支持手动清除缓存
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            console.log('Clearing cache:', cacheName);
            return caches.delete(cacheName);
          })
        );
      }).then(() => {
        // 通知客户端缓存已清除
        event.ports[0].postMessage({ success: true });
      })
    );
  }
}); 