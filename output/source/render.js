const L=require('./lib'); const {renderFrame}=require('./shots'); const {spawn}=require('child_process');
const [f0,f1,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
const c=L.createCanvas(1080,1920); const g=c.getContext('2d');
const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out],{stdio:['pipe','inherit','inherit']});
(async()=>{ for(let f=f0;f<f1;f++){ renderFrame(g,f/30,f); const buf=c.data(); if(!ff.stdin.write(Buffer.from(buf))) await new Promise(r=>ff.stdin.once('drain',r)); }
 ff.stdin.end(); ff.on('close',()=>console.log('done',out)); })();
