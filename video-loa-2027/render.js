const {chromium}=require('playwright'); const {spawn}=require('child_process');
const FPS=30, TOTAL=60*FPS, W=+process.argv[2], NW=+process.argv[3];
const a=Math.floor(TOTAL*W/NW), b=Math.floor(TOTAL*(W+1)/NW);
(async()=>{
  const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+__dirname+'/cartelas.html'); await p.evaluate(()=>document.fonts.ready);
  const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',''+FPS,'-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',`seg${W}.mp4`],{stdio:['pipe','inherit','inherit']});
  for(let f=a;f<b;f++){ await p.evaluate(t=>render(t),Math.min(f/FPS,59.999));
    const buf=await p.screenshot({type:'png'}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await br.close(); console.log('done',W);
})();
