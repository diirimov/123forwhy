import numpy as np, onnxruntime as ort, soundfile as sf, subprocess
SR=44100; NFFT=7680; HOP=1024; DF=3072; DT=256
# source with 3 s margins each side
raw=subprocess.run(['ffmpeg','-loglevel','error','-i','../song.mp3','-af','atrim=start=11.8:duration=66','-f','f32le','-ac','2','-'],capture_output=True).stdout
x=np.frombuffer(raw,np.float32).reshape(-1,2).T.astype(np.float64)
win=np.hanning(NFFT+1)[:-1]
chunk=HOP*(DT-1); trim=NFFT//2; gen=chunk-2*trim
pad=gen-(x.shape[1]%gen)
mix=np.concatenate([np.zeros((2,trim)),x,np.zeros((2,pad)),np.zeros((2,trim))],1)
sess=ort.InferenceSession('models/Kim_Vocal_2.onnx')
def stft(sig):  # sig (2,chunk) -> (4,DF,DT)
    p=np.pad(sig,((0,0),(NFFT//2,NFFT//2)),mode='reflect')
    frames=np.stack([p[:,i*HOP:i*HOP+NFFT]*win for i in range(DT)],-1) # (2,NFFT,DT)
    S=np.fft.rfft(frames,axis=1)[:, :DF,:]
    return np.concatenate([S.real,S.imag],0).astype(np.float32) if False else np.stack([S[0].real,S[0].imag,S[1].real,S[1].imag],0).astype(np.float32)
def istft(spec):
    S=np.zeros((2,NFFT//2+1,DT),complex)
    S[0,:DF]=spec[0]+1j*spec[1]; S[1,:DF]=spec[2]+1j*spec[3]
    fr=np.fft.irfft(S,n=NFFT,axis=1)*win[None,:,None]
    L=NFFT+HOP*(DT-1); out=np.zeros((2,L)); wsum=np.zeros(L)
    for i in range(DT): out[:,i*HOP:i*HOP+NFFT]+=fr[:,:,i]; wsum[i*HOP:i*HOP+NFFT]+=win**2
    out/=np.maximum(wsum,1e-8); return out[:,NFFT//2:NFFT//2+chunk]
outs=[]
for i in range(0,mix.shape[1]-2*trim,gen):
    seg=mix[:,i:i+chunk]
    spec=sess.run(None,{'input':stft(seg)[None]})[0][0]
    outs.append(istft(spec)[:,trim:-trim])
voc=np.concatenate(outs,1)[:, :x.shape[1]]*1.009
voc=voc[:, int(3*SR):int(63*SR)]
sf.write('vocals.wav',voc.T,SR)
src=x[:, int(3*SR):int(63*SR)]; sf.write('inst.wav',(src-voc).T,SR)
print('ok',voc.shape, np.sqrt((voc**2).mean()), np.sqrt((src**2).mean()))
