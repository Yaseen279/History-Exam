// The app's main flows (focus interview, Study tab, update log, text size), isolation of the /next/ preview copy from the live data, and a walk through every page of every complaint.
// usage: node tests/focus.js
const {serve,addHook,launch,reporter,ROOT}=require('./lib');
(async()=>{const R=reporter(),ok=R.ok;const s=serve(ROOT,addHook),{b,ctx}=await launch();const U=s.url;const pg=await ctx.newPage();const errs=[];pg.on('pageerror',e=>errs.push(e.message));
const closeWn=async()=>{const x=await pg.$('.wnft [data-act=wnClose]');if(x)await x.click()};
// 1. live: make a saved patient in the live app, focus must NOT be on there
await pg.goto(U+'/');await closeWn();await pg.click('[data-act=pick][data-id=cough]');await pg.waitForTimeout(200);
ok(!!(await pg.$('#fc')),'live app: the history opens in focus view');ok(!(await pg.$('.nxb')),'live app: no preview banner');
const c0=await pg.$('.pk[data-act=chip]');await c0.click();await pg.waitForTimeout(500);
const live0=await pg.evaluate(()=>localStorage.getItem('bhp.v1'));ok(live0&&JSON.parse(live0).encs.length===1,'live patient saved');
// 2. preview: gets a copy, changes stay in the copy
await pg.goto(U+'/next/');await closeWn();await pg.waitForTimeout(200);
const nx0=await pg.evaluate(()=>localStorage.getItem('bhp.next'));ok(nx0&&JSON.parse(nx0).encs.length===1,'preview starts from a copy of the saved patients');
ok(!!(await pg.$('#fc')),'preview reopens the copied patient in focus view');await pg.click('[data-act=newEnc]');await pg.waitForTimeout(200);ok(!!(await pg.$('.nxb')),'preview banner on home');
await pg.click('[data-act=pick][data-id=chest]');await pg.waitForTimeout(300);
ok(!!(await pg.$('#fc')),'preview: focus view opens for the history');
const n=await pg.$$eval('.fcseg i',x=>x.length);ok(n>20&&n<60,'chest pain has '+n+' focus pages');
const chips=await pg.$$('.fcpg .pk[data-act=chip]');ok(chips.length>=2&&chips.length<=12,'first page shows '+chips.length+' chips (was 64 on one page)');
await chips[0].click();await pg.waitForTimeout(150);
ok(!!(await pg.$('.fcpg .pk.y')),'tap marks a yes and stays on the page');
ok(!!(await pg.$('.fcdx .hch')),'differential shows in the top bar after an answer');
const h1=await pg.$eval('.fcq h3',x=>x.textContent);await pg.click('.fcnx');await pg.waitForTimeout(150);const h2=await pg.$eval('.fcq h3',x=>x.textContent);ok(h1!==h2,'Next moves on: '+h1+' -> '+h2);
await pg.click('.fcbk');await pg.waitForTimeout(150);ok((await pg.$eval('.fcq h3',x=>x.textContent))===h1&&!!(await pg.$('.fcpg .pk.y')),'Back returns, answer kept');
// rest: no
await pg.click('.fcnx');await pg.waitForTimeout(100);await pg.click('.fcno');await pg.waitForTimeout(200);
const st=await pg.evaluate(()=>{const d=JSON.parse(localStorage.getItem('bhp.next')||'{}');return 1});
await pg.click('.fcbk');await pg.waitForTimeout(150);ok((await pg.$$eval('.fcpg .pk.n',x=>x.length))>=2,'"Rest: no" marks the group as denied and moves on');
// then ask inside focus (chest H22 -> H30)
await pg.click('[data-act=fcMap]');await pg.waitForTimeout(100);const rows=await pg.$$('[data-act=fcJump]');let ti=-1;for(let i=0;i<rows.length;i++){if(/Timing/.test(await rows[i].textContent())){ti=i;break}}
await rows[ti].click();await pg.waitForTimeout(200);let more=await pg.$$('.fcpg [data-act=moreQ]');for(const m of more){await m.click();await pg.waitForTimeout(80)}
const ex=await pg.$('.fcpg .pk[data-k="H22"]');ok(!!ex,'timing page has "Only on exertion"');if(ex){await ex.click();await pg.waitForTimeout(250);const f=await pg.$('.fup');ok(!!f,'Then ask appears in focus view');if(f){await f.click();await pg.waitForTimeout(400);ok(/Relieving/.test(await pg.$eval('.fcq h3',x=>x.textContent))&&!!(await pg.$('.pk.flash')),'Then ask jumps to the right page')}}
// smart question
for(let i=0;i<4;i++){const cc=await pg.$$('.fcpg .pk[data-act=chip]:not(.y):not(.n)');if(cc[0])await cc[0].click();await pg.waitForTimeout(80)}
const sm=await pg.$('#fcSmart');ok(!!sm,'Best next question card appears');
if(sm){const q=await pg.$eval('#fcSmart b',x=>x.textContent);await pg.click('#fcSmart [data-act=fcAns][data-v="1"]');await pg.waitForTimeout(200);const q2=await pg.$('#fcSmart b')?await pg.$eval('#fcSmart b',x=>x.textContent):'';ok(q!==q2,'answering it records the answer and offers another: '+q+' -> '+(q2||'none'))}
// background + ROS all no, textarea typing keeps focus
await pg.click('[data-act=fcMap]');await pg.waitForTimeout(100);const rows2=await pg.$$('[data-act=fcJump]');for(let i=0;i<rows2.length;i++){if(/Past medical history/.test(await rows2[i].textContent())){await rows2[i].click();break}}
await pg.waitForTimeout(200);await pg.click('.fcpg .it [data-act=bgTri][data-v="1"]');await pg.waitForTimeout(100);ok(/positive/.test(await pg.$eval('.fcpg .pill',x=>x.textContent)),'background Yes updates the status');
await pg.fill('.fcpg textarea','Hypertension for 5 years');await pg.click('.fcnx');await pg.waitForTimeout(150);await pg.click('.fcno');await pg.waitForTimeout(150);
// run to the end
let guard=0;while(await pg.$('.fcnx[data-act=fcGo]')&&guard++<80){await pg.click('.fcnx');await pg.waitForTimeout(40)}
ok(/Summary/.test(await pg.$eval('.fcq h3',x=>x.textContent)),'reaches Summary and close');
await pg.fill('.fcpg textarea[data-b="tx.hpc"]','Central chest pain for 2 hours');await pg.waitForTimeout(500);
await pg.click('.fcnx');await pg.waitForTimeout(250);ok(await pg.$eval('.stages [aria-current=step]',x=>/Vitals/.test(x.textContent)),'last Next goes to vitals (exam is under maintenance)');
await pg.click('[data-act=stage][data-s=note]');await pg.waitForTimeout(300);const note=await pg.evaluate(()=>document.body.innerText+' '+Array.from(document.querySelectorAll('textarea')).map(t=>t.value).join(' ')+' '+localStorage.getItem('bhp.next'));ok(/Hypertension for 5 years/.test(note)&&/Central chest pain for 2 hours/.test(note),'note contains what was entered in focus view');
// resume position + list view toggle
await pg.click('[data-act=stage][data-s=hist]');await pg.waitForTimeout(200);ok(/Summary/.test(await pg.$eval('.fcq h3',x=>x.textContent)),'returns to the same page');
await pg.click('[data-act=fcView][data-v="0"]');await pg.waitForTimeout(250);ok(!(await pg.$('#fc'))&&!!(await pg.$('.stps')),'switch to full list view');
await pg.click('[data-act=fcView][data-v="1"]');await pg.waitForTimeout(250);ok(!!(await pg.$('#fc')),'switch back to focus view');
await pg.waitForTimeout(500);
ok((await pg.evaluate(()=>localStorage.getItem('bhp.v1')))===live0,'live saved data is untouched by the preview');
// 3. every complaint: walk all pages, no errors, each page renders something
const ids=await pg.evaluate(()=>window.__T?window.__T.PRES.map(p=>p.id):null);
if(ids){let tot=0,empty=[];for(const id of ids){if(id==='other')continue;
  const bk=await pg.$('[data-act=newEnc]');if(bk){await bk.click();await pg.waitForTimeout(40)}
  const sp=await pg.$('[data-act=pick][data-id="'+id+'"]');if(!sp){const s2=await pg.$('[data-act=spec][data-g=Surgery]');if(s2){await s2.click();await pg.waitForTimeout(60)}}
  const sp2=await pg.$('[data-act=pick][data-id="'+id+'"]');if(!sp2){const s3=await pg.$('[data-act=spec][data-g=Medicine]');if(s3)await s3.click();continue}
  await sp2.click();await pg.waitForTimeout(60);if(!(await pg.$('#fc'))){empty.push(id+':nofocus');continue}
  let g=0;while(g++<90){tot++;const cnt=await pg.$$eval('#fcIn .pk,#fcIn .it,#fcIn textarea,#fcIn .addpain',x=>x.length);if(!cnt)empty.push(id+':'+await pg.$eval('.fcq h3',x=>x.textContent));if(!(await pg.$('.fcnx[data-act=fcGo]')))break;await pg.click('.fcnx')}
 }
 ok(empty.length===0,'all complaints walk through, '+tot+' pages, none empty '+empty.slice(0,6).join(' | '))}
// exam under maintenance, one Study tab with only memory aids and reference
await pg.goto(U+'/next/');await pg.waitForTimeout(150);{const nw=await pg.$('[data-act=newEnc]');if(nw)await nw.click();await pg.waitForTimeout(80);let pk=await pg.$('[data-act=pick][data-id=chest]');if(!pk){await pg.click('[data-act=spec][data-g=Medicine]');await pg.waitForTimeout(80)}await pg.click('[data-act=pick][data-id=chest]');await pg.waitForTimeout(150)}
ok(!(await pg.$('.wnov')),'What\'s new does not reopen once seen');
{await pg.click('[data-act=newEnc]');await pg.waitForTimeout(100);await pg.click('[data-act=wnOpen]');await pg.waitForTimeout(150);const nu=await pg.$$eval('.wnup',x=>x.length),op=await pg.$$eval('.wnup[open]',x=>x.length);ok(nu===2&&op===1&&(await pg.$$eval('.wnup[open] .wnd',x=>x.length))>=5,'What\'s new: this update open with pictures, the past update collapsed');
 const past=await pg.$$('.wnup:not([open]) summary');await past[0].click();await pg.waitForTimeout(100);ok((await pg.$$eval('.wnup[open] .wnd',x=>x.length))>=8,'the past update opens with its pictures');await pg.click('.wnft [data-act=wnClose]');await pg.waitForTimeout(100);
 let pk=await pg.$('[data-act=pick][data-id=chest]');if(!pk){await pg.click('[data-act=spec][data-g=Medicine]');await pg.waitForTimeout(80)}await pg.click('[data-act=pick][data-id=chest]');await pg.waitForTimeout(150)}
await pg.click('[data-act=infoToggle]');await pg.waitForTimeout(100);await pg.click('[data-act=stage][data-s=ddx]');await pg.waitForTimeout(150);ok(!(await pg.$('[data-b="pt.age"]')),'patient form closes when the stage changes');
ok((await pg.$$eval('.stages button',x=>x.map(b=>b.dataset.s).join(',')))==='hist,exam,vit,ddx,rev,note','stage bar: History, Exam, Vitals, DDx, Review, Note');
await pg.click('.dxseg [data-s=web]');await pg.waitForTimeout(200);ok(!!(await pg.$('.dxseg [data-s=web][aria-pressed=true]'))&&await pg.$eval('.stages [aria-current=step]',x=>/DDx/.test(x.textContent)),'reasoning web opens inside DDx');
await pg.click('[data-act=stage][data-s=exam]');await pg.waitForTimeout(150);
ok(!!(await pg.$('.soonc'))&&!(await pg.$('.pk[data-act=chip]')),'Exam tab shows the maintenance notice, no exam findings');
await pg.click('[data-act=stage][data-s=rev]');await pg.waitForTimeout(150);ok(!/Examination steps not done|Examine:/.test(await pg.evaluate(()=>document.body.innerText)),'Review has no exam items');
const tabs=await pg.$$eval('.nav [data-act=nav]',x=>x.map(b=>b.dataset.tab).join(','));ok(tabs==='enc,log,study','bottom tabs: '+tabs);
await pg.click('[data-act=nav][data-tab=study]');await pg.waitForTimeout(150);const nA=await pg.$$eval('details.a2',x=>x.length);ok(nA>=25,'Memory aids: '+nA+' complaint cards');
ok(!/Exam guide|Virtual patient|Diagnosis quiz|flowchart/i.test(await pg.evaluate(()=>document.querySelector('#main').innerText)),'no exam guides, virtual patient, quiz or flowcharts in Study');
await pg.fill('#aq','aortic dissection');await pg.waitForTimeout(150);const nS=await pg.$$eval('details.a2',x=>x.length);ok(nS>=1&&nS<nA,'search narrows the aids to '+nS);await pg.fill('#aq','');
await pg.click('[data-act=aidG][data-g=Surgery]');await pg.waitForTimeout(100);ok((await pg.$$eval('details.a2',x=>x.length))<nA,'Surgery filter works');
await pg.click('[data-act=stab][data-v=ref]');await pg.waitForTimeout(150);const rt=await pg.$$eval('.rftiles button',x=>x.map(b=>b.dataset.v).join(','));ok(rt==='scores,calc,norm,crit,mnem','Reference sections: '+rt);
for(const r of rt.split(',')){await pg.click('.rftiles [data-v='+r+']');await pg.waitForTimeout(120);const len=await pg.evaluate(()=>document.querySelector('#main').innerText.length);ok(len>400&&!!(await pg.$('[data-act=rhub]')),'Reference > '+r+' opens with content');await pg.click('[data-act=rhub]');await pg.waitForTimeout(80)}
// removed controls, text size (on the live path)
await pg.goto(U+'/');await pg.waitForTimeout(200);{const w=await pg.$('.wnft [data-act=wnClose]');if(w)await w.click()}
ok(!(await pg.$('.nxb')),'live app has no preview banner');
{const nw=await pg.$('[data-act=newEnc]');if(nw){await nw.click();await pg.waitForTimeout(80)}let pk=await pg.$('[data-act=pick][data-id=cough]');if(!pk){await pg.click('[data-act=spec][data-g=Medicine]');await pg.waitForTimeout(80)}await pg.click('[data-act=pick][data-id=cough]');await pg.waitForTimeout(150)}
ok(!(await pg.$('.pk.ot')),'no "+ Other" chip in focus view');
await pg.click('[data-act=fcView][data-v="0"]');await pg.waitForTimeout(200);ok(!(await pg.$('[data-act=hyToggle]'))&&!(await pg.$('[data-act=covToggle]'))&&!(await pg.$('.pk.ot')),'list view has no High-yield only, Test yourself or "+ Other"');await pg.click('[data-act=fcView][data-v="1"]');await pg.waitForTimeout(150);
await pg.click('[data-act=moreToggle]');await pg.click('.moremenu [data-act=accent]');await pg.waitForTimeout(150);await pg.click('[data-act=fsSet][data-v=xl]');await pg.waitForTimeout(200);
ok((await pg.evaluate(()=>getComputedStyle(document.documentElement).fontSize))==='20px'&&!(await pg.evaluate(()=>document.documentElement.scrollWidth>innerWidth)),'Extra large text applies with no sideways scroll');
await pg.waitForTimeout(500);await pg.reload();await pg.waitForTimeout(250);ok((await pg.evaluate(()=>getComputedStyle(document.documentElement).fontSize))==='20px','text size is remembered');
await pg.click('[data-act=moreToggle]');await pg.click('.moremenu [data-act=accent]');await pg.waitForTimeout(100);await pg.click('[data-act=fsSet][data-v=m]');await pg.waitForTimeout(100);ok((await pg.evaluate(()=>getComputedStyle(document.documentElement).fontSize))==='16px','back to Normal');
ok(errs.length===0,'no page errors '+errs.slice(0,3).join(' ; '));
R.done();await b.close();s.close()})();
