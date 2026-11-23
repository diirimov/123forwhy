import sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k=Kokoro('tts/kokoro-v1.0.onnx','tts/voices-v1.0.bin')
voice=sys.argv[1]; speed=float(sys.argv[2])
lines={
 'l1':"Before the world knew ah-HAH,",
 'l2':"three musicians left Norway, chasing a sound they couldn't let go of.",
 'l3':"In London, they worked on one song. Again, and again.",
 'l4':"Its first release sold only three hundred copies.",
 'l5':"Most bands would have moved on.",
 'l6':"They didn't.",
 'l7':"Take On Me made them famous.",
 'l8':"It wasn't the end of their story.",
 'l9':"They said goodbye in twenty ten...",
 'l10':"and found their way back.",
}
for n,tx in lines.items():
  a,sr=k.create(tx,voice=voice,speed=speed,lang='en-us')
  # trim silence
  e=np.abs(a)>0.01; i=np.argmax(e); j=len(a)-np.argmax(e[::-1])
  a=a[max(0,i-240):j+1200]
  sf.write(f'vo/{voice}_{n}.wav',a,sr); print(n, round(len(a)/sr,2))
