/* Bedside H&P service worker: caches the app so it opens offline. Bump VERSION when you update the files. */
var VERSION = 'bhp-v65';
var CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(VERSION).then(function(c){return c.addAll(CORE)}).then(function(){return self.skipWaiting()}))});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==VERSION}).map(function(k){return caches.delete(k)}))}).then(function(){return self.clients.claim()}))});
self.addEventListener('fetch',function(e){
  var req=e.request;if(req.method!=='GET')return;
  var url=new URL(req.url);
  if(url.origin===location.origin){
    e.respondWith(caches.match(req,{ignoreSearch:true}).then(function(hit){
      return hit||fetch(req).then(function(res){var copy=res.clone();caches.open(VERSION).then(function(c){c.put(req,copy)});return res}).catch(function(){return caches.match('./index.html')});
    }));
  }else if(/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)){
    e.respondWith(caches.open(VERSION).then(function(c){return c.match(req).then(function(hit){
      var net=fetch(req).then(function(res){c.put(req,res.clone());return res}).catch(function(){return hit});
      return hit||net;
    })}));
  }
});
