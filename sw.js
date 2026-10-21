/* Bedside H&E service worker: caches the app so it opens offline.
   The page itself (index.html) is fetched network-first, so a new upload reaches students on their next open
   without bumping VERSION. Bump VERSION only when you change this file or the CORE list. */
var VERSION = 'bhe-v74';
var CORE=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon-maskable-192.png','./icon-maskable-512.png'];
var NET_TIMEOUT=4000; /* on slow ward wifi, fall back to the cached copy after this many ms */
self.addEventListener('install',function(e){e.waitUntil(caches.open(VERSION).then(function(c){return c.addAll(CORE)}).then(function(){return self.skipWaiting()}))});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==VERSION}).map(function(k){return caches.delete(k)}))}).then(function(){return self.clients.claim()}))});
function isPage(req,url){return req.mode==='navigate'||/\/(index\.html)?$/.test(url.pathname)}
function save(req,res){if(res&&res.ok&&res.type==='basic'){var copy=res.clone();caches.open(VERSION).then(function(c){c.put(req,copy)})}return res}
/* Network first: revalidate with the server (a cheap 304 when nothing changed), cache the answer, use the cache when offline or slow. */
function networkFirst(req){
  var key=req.mode==='navigate'?'./index.html':req;
  return new Promise(function(resolve){
    var done=false;
    function fromCache(){return caches.match(key,{ignoreSearch:true}).then(function(hit){return hit||caches.match('./index.html')})}
    var timer=setTimeout(function(){fromCache().then(function(hit){if(hit&&!done){done=true;resolve(hit)}})},NET_TIMEOUT);
    fetch(req.url,{cache:'no-cache',credentials:'same-origin'}).then(function(res){
      clearTimeout(timer);
      if(res.ok&&res.type==='basic'){var copy=res.clone();caches.open(VERSION).then(function(c){c.put(key,copy)})}
      if(!done){done=true;resolve(res)}
    }).catch(function(){
      clearTimeout(timer);
      fromCache().then(function(hit){if(!done){done=true;resolve(hit||Response.error())}});
    });
  });
}
/* Icons and manifest: serve the cached copy at once, refresh it in the background. */
function staleWhileRevalidate(req){
  return caches.match(req,{ignoreSearch:true}).then(function(hit){
    var net=fetch(req).then(function(res){return save(req,res)}).catch(function(){return hit||caches.match('./index.html')});
    return hit||net;
  });
}
self.addEventListener('fetch',function(e){
  var req=e.request;if(req.method!=='GET')return;
  var url=new URL(req.url);
  if(url.origin===location.origin){
    e.respondWith(isPage(req,url)?networkFirst(req):staleWhileRevalidate(req));
  }else if(/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)){
    e.respondWith(caches.open(VERSION).then(function(c){return c.match(req).then(function(hit){
      var net=fetch(req).then(function(res){c.put(req,res.clone());return res}).catch(function(){return hit});
      return hit||net;
    })}));
  }
});
