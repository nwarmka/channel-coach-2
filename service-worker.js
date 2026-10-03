const CACHE_NAME = "channel-coach-pwa-v2";

const APP_SHELL = [
  "/",
  "/manifest.json",
  "/static/icon-192.png",
  "/static/icon-512.png",
  "/static/channel-coach-icon.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );

  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter(
            (key) =>
              key.startsWith("channel-coach-pwa-") &&
              key !== CACHE_NAME
          )
          .map((key) => caches.delete(key))
      )
    )
  );

  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;

  if (request.method !== "GET") return;

  const url = new URL(request.url);

  const isSameOrigin =
    url.origin === self.location.origin;

  const isNavigation =
    request.mode === "navigate";

  const isStaticAsset =
    isSameOrigin &&
    (
      url.pathname.startsWith("/static/") ||
      url.pathname === "/manifest.json"
    );

  if (isNavigation) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const copy = response.clone();

            caches.open(CACHE_NAME).then((cache) => {
              cache.put("/", copy);
            });
          }

          return response;
        })
        .catch(async () => {
          const cached = await caches.match("/");

          if (cached) {
            return cached;
          }

          return new Response(
            `
            <!doctype html>
            <html>
              <head>
                <meta charset="utf-8">

                <meta
                  name="viewport"
                  content="width=device-width, initial-scale=1"
                >

                <meta
                  name="theme-color"
                  content="#8b5cf6"
                >

                <title>
                  Channel Coach — Offline
                </title>

                <style>
                  body {
                    margin: 0;
                    min-height: 100vh;

                    display: grid;
                    place-items: center;

                    background: #05070d;
                    color: #f8fafc;

                    font-family:
                      system-ui,
                      -apple-system,
                      BlinkMacSystemFont,
                      "Segoe UI",
                      sans-serif;
                  }

                  main {
                    width: min(
                      430px,
                      calc(100% - 40px)
                    );

                    padding: 28px;

                    text-align: center;

                    border:
                      1px solid
                      rgba(139,92,246,.45);

                    border-radius: 20px;

                    background: #0b0f19;

                    box-shadow:
                      0 18px 50px
                      rgba(0,0,0,.4);
                  }

                  h1 {
                    margin: 0 0 10px;

                    font-size: 1.5rem;
                  }

                  p {
                    margin: 0;

                    color: #aab2c6;

                    line-height: 1.55;
                  }

                  .dot {
                    width: 11px;
                    height: 11px;

                    margin:
                      0 auto 16px;

                    border-radius: 50%;

                    background: #ff3ea5;

                    box-shadow:
                      0 0 16px
                      rgba(255,62,165,.8);
                  }
                </style>
              </head>

              <body>
                <main>
                  <div class="dot"></div>

                  <h1>
                    Channel Coach is offline
                  </h1>

                  <p>
                    Check your connection.
                    The app will work again
                    as soon as you're back online.
                  </p>
                </main>
              </body>
            </html>
            `,
            {
              status: 200,
              headers: {
                "Content-Type":
                  "text/html; charset=utf-8"
              }
            }
          );
        })
    );

    return;
  }

  if (isStaticAsset) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const networkFetch =
          fetch(request)
            .then((response) => {
              if (
                response &&
                response.ok
              ) {
                const copy =
                  response.clone();

                caches
                  .open(CACHE_NAME)
                  .then((cache) => {
                    cache.put(
                      request,
                      copy
                    );
                  });
              }

              return response;
            })
            .catch(() => cached);

        return cached || networkFetch;
      })
    );
  }
});
