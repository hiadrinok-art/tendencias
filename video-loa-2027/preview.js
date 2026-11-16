const {chromium}=require('playwright');const path=require('path');
(async()=>{const times=process.argv.slice(3).map(Number);const out=process.argv[2];
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('console',m=>console.log('console:',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+path.resolve(process.env.PAGE||'index.html'));await p.evaluate(()=>document.fonts.ready);
for(const t of times){const s=Date.now();await p.evaluate(t=>renderAt(t),t);await p.screenshot({path:`${out}/f_${t}.jpg`,type:'jpeg',quality:80});console.log(t,Date.now()-s,'ms');}
await b.close();})();
