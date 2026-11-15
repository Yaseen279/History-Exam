// Shared helpers for the browser tests. Run any test with: node tests/<name>.js
const path=require('path'),fs=require('fs'),http=require('http');
function findPW(){for(const p of ['playwright','/opt/node22/lib/node_modules/playwright']){try{return require(p)}catch(e){}}throw new Error('playwright not found')}
function findChrome(){if(process.env.CHROME)return process.env.CHROME;const base='/opt/pw-browsers';try{for(const d of fs.readdirSync(base).sort().reverse()){for(const sub of ['chrome-linux64/chrome','chrome-linux/chrome']){const f=path.join(base,d,sub);if(fs.existsSync(f))return f}}}catch(e){}return undefined}
// serve(root, patch): static server; patch(html, urlPath) can alter index.html on the way out (tests only)
function serve(root,patch){
  const srv=http.createServer((q,r)=>{let u=decodeURIComponent(q.url.split('?')[0]);if(u.endsWith('/'))u+='index.html';const f=path.join(root,u);
    if(!f.startsWith(root)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){r.writeHead(404);return r.end()}
    const ext=path.extname(f),ct={'.html':'text/html','.js':'application/javascript','.png':'image/png','.webmanifest':'application/manifest+json'}[ext]||'application/octet-stream';
    let body=fs.readFileSync(f);if(ext==='.html'&&patch)body=Buffer.from(patch(body.toString('utf8'),u));
    r.writeHead(200,{'Content-Type':ct});r.end(body)}).listen(0);
  return {url:'http://127.0.0.1:'+srv.address().port,close:()=>srv.close()};
}
// expose a few internals to the tests without touching the shipped file
const HOOK='window.__T={PRES:PRES,ACT:ACT,getP:getP,curEnc:curEnc,FUP:FUP,CZPIC:CZPIC,GUIDES:GUIDES,lpItem:lpItem,DB:function(){return DB}};';
const addHook=html=>html.replace('/* ================= boot ================= */',HOOK+'\n/* ================= boot ================= */');
async function launch(opts){const {chromium}=findPW();const b=await chromium.launch({executablePath:findChrome()});const ctx=await b.newContext(Object.assign({viewport:{width:390,height:844},serviceWorkers:'block'},opts||{}));await ctx.route(/fonts\.(googleapis|gstatic)|gc\.zgo\.at|goatcounter\.com|t\.me/,r=>r.abort());return {b,ctx}}
function reporter(){let fails=0;return {ok:(c,m)=>{if(!c)fails++;console.log((c?'PASS ':'FAIL ')+m)},done:()=>{console.log(fails?'FAILED '+fails:'ALL PASS');process.exitCode=fails?1:0}}}
const ROOT=path.resolve(__dirname,'..');
module.exports={serve,addHook,launch,reporter,ROOT};
