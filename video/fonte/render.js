const {chromium}=require('playwright');const fs=require('fs');
const FPS=12,DUR=+process.argv[3],N=FPS*DUR,W=4,dir=process.argv[2];
(async()=>{const b=await chromium.launch();fs.mkdirSync(dir+'/frames',{recursive:true});
const work=async(w)=>{const pg=await b.newPage({viewport:{width:1080,height:1920}});
 await pg.goto('file://'+dir+'/index.html');await pg.evaluate(()=>document.fonts.ready);await pg.waitForTimeout(800);
 if(w===0) fs.writeFileSync(dir+'/sfx.json',JSON.stringify(await pg.evaluate(()=>SFX)));
 for(let i=w;i<N;i+=W){await pg.evaluate(t=>render(t),i/FPS);
  await pg.screenshot({path:`${dir}/frames/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});}};
await Promise.all([0,1,2,3].map(work));await b.close();})();
