// Proves a change did not alter the live app: drives two builds through the same taps and compares the page HTML at each step.
// usage: node tests/same-as.js <dir of the reference build> [<dir of the new build, default repo root>]
const {serve,launch,reporter,ROOT}=require('./lib');
const A=process.argv[2],B=process.argv[3]||ROOT;if(!A){console.log('usage: node tests/same-as.js <reference dir> [new dir]');process.exit(2)}
const norm=h=>h.replace(/\b(data-id|data-enc|data-eid|id|for|value)="e?[a-z0-9]{6,}"/g,'$1="ID"').replace(/\d+ (min|h|d) ago|just now/g,'AGO').replace(/\d{1,2}[/:.]\d{1,2}([/:.]\d{2,4})?/g,'T');
async function run(root,ids){
  const s=serve(root),{b,ctx}=await launch();const pg=await ctx.newPage();const errs=[];pg.on('pageerror',e=>errs.push(e.message));const out=[];
  const snap=async n=>{await pg.waitForTimeout(60);out.push([n,norm(await pg.$eval('#app',x=>x.innerHTML))])};
  await pg.addInitScript(()=>{let i=0;Math.random=()=>((i=(i*9301+49297)%233280)/233280);const D=Date.now;const t0=1760000000000;Date.now=()=>t0});
  await pg.goto(s.url+'/');const x=await pg.$('.wnft [data-act=wnClose]');if(x)await x.click();await snap('home');
  for(const id of ids){
    const nw=await pg.$('[data-act=newEnc]');if(nw)await nw.click();await pg.waitForTimeout(40);
    let p=await pg.$('[data-act=pick][data-id="'+id+'"]');if(!p){const sw=await pg.$('[data-act=spec][aria-pressed=false]');if(sw){await sw.click();await pg.waitForTimeout(40)}p=await pg.$('[data-act=pick][data-id="'+id+'"]')}
    if(!p){out.push([id+':missing','']);continue}
    await p.click();await snap(id+':hist');
    const chips=await pg.$$('.pk[data-act=chip]');for(const i of [0,1,3,5])if(chips[i]){await chips[i].click().catch(()=>{});await pg.waitForTimeout(20)}
    await snap(id+':hist-ticked');
    for(const st of ['exam','vit','ddx','web','rev','note']){const t=await pg.$('[data-act=stage][data-s='+st+']');if(t){await t.click();await snap(id+':'+st)}}
    await pg.click('[data-act=stage][data-s=hist]').catch(()=>{});
  }
  for(const tab of ['log','ref','prac']){await pg.click('[data-act=nav][data-tab='+tab+']');await snap('tab:'+tab)}
  await b.close();s.close();return {out,errs};
}
(async()=>{const R=reporter();
  const ids=(process.env.IDS||'chest,cough,fever,headache,abd,genhx,groin,breast,joint,drain,postop,trauma,uti,confusion').split(',');
  const a=await run(A,ids),b=await run(B,ids);
  R.ok(a.errs.length===0&&b.errs.length===0,'no page errors (reference '+a.errs.length+', new '+b.errs.length+') '+b.errs.slice(0,2).join(' ; '));
  R.ok(a.out.length===b.out.length,'same number of screens: '+a.out.length);
  let diff=[];a.out.forEach((x,i)=>{const y=b.out[i];if(!y||x[1]!==y[1]){let k=0;const p=x[1],q=(y||['',''])[1];while(k<p.length&&p[k]===q[k])k++;diff.push(x[0]+' @'+k+'\n   ref: '+p.slice(Math.max(0,k-60),k+140)+'\n   new: '+q.slice(Math.max(0,k-60),k+140))}});
  R.ok(diff.length===0,a.out.length+' screens are identical in both builds'+(diff.length?'\n  '+diff.slice(0,4).join('\n  '):''));
  R.done()})();
