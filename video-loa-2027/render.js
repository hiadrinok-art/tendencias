// Renderiza index.html quadro a quadro (determinístico por tempo) e codifica em MP4.
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');const fs=require('fs');
const FPS=30,DUR=240,TOTAL=FPS*DUR,WORKERS=+(process.env.WORKERS||4);
const OUT=process.env.OUT||'build';fs.mkdirSync(OUT,{recursive:true});
async function worker(id,f0,f1){
  const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.resolve('index.html'));await p.evaluate(()=>document.fonts.ready);
  const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-',
    '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-r',String(FPS),`${OUT}/seg_${id}.mp4`],{stdio:['pipe','inherit','inherit']});
  for(let f=f0;f<f1;f++){await p.evaluate(t=>renderAt(t),f/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:95});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    if((f-f0)%300===0)console.log(`w${id} ${f-f0}/${f1-f0}`);}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
}
(async()=>{const per=Math.ceil(TOTAL/WORKERS);const jobs=[];
  for(let i=0;i<WORKERS;i++)jobs.push(worker(i,i*per,Math.min(TOTAL,(i+1)*per)));
  await Promise.all(jobs);
  fs.writeFileSync(`${OUT}/list.txt`,[...Array(WORKERS).keys()].map(i=>`file 'seg_${i}.mp4'`).join('\n'));
  console.log('frames done');})();
