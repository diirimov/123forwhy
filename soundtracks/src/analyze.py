import sys, wave, numpy as np
def load(p):
    w=wave.open(p); n=w.getnframes(); b=np.frombuffer(w.readframes(n),np.uint8).reshape(-1,3)
    return (np.c_[np.zeros(len(b),np.uint8),b].copy().view('<i4').ravel()/2**31).reshape(-1,2).T
for p in sys.argv[1:]:
    x=load(p); m=x.mean(0); s=(x[0]-x[1])/2
    seg=m[int(5*44100):int(17*44100)]
    F=np.abs(np.fft.rfft(seg*np.hanning(len(seg))))**2; f=np.fft.rfftfreq(len(seg),1/44100)
    bands=[31,63,125,250,500,1000,2000,4000,8000,16000]
    lv=[10*np.log10(F[(f>=b/np.sqrt(2))&(f<b*np.sqrt(2))].sum()+1e-20) for b in bands]
    ref=lv[5]
    print(p.split('/')[-1], ' '.join(f'{b}:{l-ref:+.0f}' for b,l in zip(bands,lv)), f' side/mid {20*np.log10(np.std(s)/np.std(m)):.1f}dB')
