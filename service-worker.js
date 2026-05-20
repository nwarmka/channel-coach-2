self.addEventListener("install", function(event) {
  console.log("Channel Coach installed");
});

self.addEventListener("fetch", function(event) {
  event.respondWith(fetch(event.request));
});