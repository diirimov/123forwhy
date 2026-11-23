import numpy as np, soundfile as sf, librosa, json
from scipy.signal import butter, sosfilt, sosfiltfilt
SR=48000; IN=14.80; DUR=60.0; N=int(SR*DUR)
song,_=librosa.load('song.mp3',sr=SR,mono=False,offset=IN,duration=DUR+0.05)
song=song[:, :N]
if song.shape[1]<N: song=np.pad(song,((0,0),(0,N-song.shape[1])))
t=np.arange(N)/SR
VOICE='am_michael'
place={'l1':4.80,'l2':6.70,'l3':15.15,'l4':22.15,'l5':25.00,'l6':26.72,'l7':47.75,'l8':50.60,'l9':52.75,'l10':56.30}
vo=np.zeros(N); segs=[]
hp=butter(2,90,'hp',fs=SR,output='sos'); pres=butter(2,[2500,6000],'bp',fs=SR,output='sos')
for k,st in place.items():
    a,sr=sf.read(f'vo/{VOICE}_{k}.wav'); a=librosa.resample(a,orig_sr=sr,target_sr=SR)
    a=sosfilt(hp,a); a=a+0.35*sosfilt(pres,a)          # clarity
    # gentle compression
    env=np.sqrt(np.convolve(a**2,np.ones(480)/480,'same'))+1e-6
    gain=np.minimum(1,(0.12/env)**0.4); a=a*gain
    a=a/np.max(np.abs(a))*0.62
    i=int(st*SR); j=min(N,i+len(a)); vo[i:j]+=a[:j-i]; segs.append((st,st+len(a)/SR,k))
print([(k,round(a,2),round(b,2)) for a,b,k in segs])
# ducking envelope for song
duck=np.ones(N)
for a,b,k in segs:
    d=10**((-9.5 if a<30 else -12.5)/20)
    lo,hi=a-0.25,b+0.30
    m=(t>=lo)&(t<=hi); 
    ramp=np.clip(np.minimum((t-lo)/0.25,(hi-t)/0.35),0,1)
    duck=np.minimum(duck, 1-(1-d)*ramp)
# merge short gaps (<0.9s) between lines so music doesn't pump
from scipy.ndimage import minimum_filter1d, uniform_filter1d
duck=minimum_filter1d(duck,int(0.9*SR)); duck=uniform_filter1d(duck,int(0.25*SR))
# chorus 34.81->47.4 is narration-free: full level. Slight lift +1dB into the chorus
lift=1+ (10**(1/20)-1)*np.clip((t-34.6)/0.3,0,1)*np.clip((47.6-t)/0.4,0,1)
g=duck*lift
# muffled record-shop moment (2.52-4.55): low-pass crossfade
lp=butter(4,1100,'lp',fs=SR,output='sos'); muff=sosfiltfilt(lp,song,axis=1)*1.35
cs,ce=2.52,4.55
w=np.clip(np.minimum((t-cs)/0.03,(ce-t)/0.25),0,1)
songp=song*(1-w)+muff*w
# carve 1-4 kHz of the song under narration (frees space for the voice)
vb=butter(2,[1000,4000],'bp',fs=SR,output='sos'); band=sosfiltfilt(vb,songp,axis=1)
nenv=np.clip((1-duck)/(1-10**(-9.5/20)),0,1)
songp=songp-0.5*band*nenv
# fade in 0.08 (avoid click), fade out last 0.8 s
fade=np.clip(t/0.08,0,1)*np.clip((DUR-t)/0.8,0,1)
mus=songp*g*fade
# crowd roar: shaped noise
rng=np.random.default_rng(3)
def crowd(len_s, scream=True):
    n=int(len_s*SR); x=rng.standard_normal((2,n))
    bp=butter(2,[350,3500],'bp',fs=SR,output='sos'); x=sosfilt(bp,x,axis=1)
    m=1+0.35*np.sin(2*np.pi*np.cumsum(rng.uniform(3,7,n))/SR)
    y=x*m
    if scream:
        for _ in range(14):
            f0=rng.uniform(900,1800); s0=rng.integers(0,n-SR//2); L=rng.integers(SR//5,SR//2)
            tt=np.arange(L)/SR; tone=np.sin(2*np.pi*(f0+80*np.sin(2*np.pi*6*tt))*tt)*np.hanning(L)*0.25
            y[:,s0:s0+L]+=tone
    return y/np.max(np.abs(y))
def place_fx(buf, x, st, gain, fi=0.05, fo=0.6):
    i=int(st*SR); n=min(x.shape[1],N-i); e=np.ones(n); fi_n=int(fi*SR); fo_n=int(fo*SR)
    e[:fi_n]=np.linspace(0,1,fi_n); e[-fo_n:]*=np.linspace(1,0,fo_n); buf[:,i:i+n]+=x[:,:n]*e*gain
fx=np.zeros((2,N))
place_fx(fx,crowd(2.7),0.0,0.20,0.01,0.25)     # cold-open roar, cut hard at smash cut
fx[:,int(2.52*SR):int(2.60*SR)]*=np.linspace(1,0,int(.08*SR))
fx[:,int(2.60*SR):int(3.5*SR)]=0
place_fx(fx,crowd(4.5,False),45.3,0.08,0.8,1.2)  # stadium swell
place_fx(fx,crowd(3.8),56.1,0.11,0.9,1.2)        # 2015 return cheer
out=mus+fx+np.vstack([vo,vo])*1.0
pk=np.max(np.abs(out)); print('peak pre',pk)
sf.write('mix_raw.wav',out.T.astype(np.float32),SR,subtype='FLOAT')
json.dump({'segs':segs},open('vo_segs.json','w'))
