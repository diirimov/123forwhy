import librosa, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, sys
y,sr=librosa.load(sys.argv[1],sr=22050)
P=0.4666940; OFF=-0.006; BAR=4*P
lo_m,hi_m=int(sys.argv[4]),int(sys.argv[5])
bpo=36
C=np.abs(librosa.cqt(y,sr=sr,hop_length=64,fmin=librosa.midi_to_hz(lo_m-0.5),n_bins=(hi_m-lo_m)*3,bins_per_octave=bpo,filter_scale=1.5))
L=librosa.amplitude_to_db(C,ref=np.max)
names='C C# D D# E F F# G G# A A# B'.split()
fps=sr/64
for b0 in range(int(sys.argv[2]),int(sys.argv[3]),4):
    t0=b0*BAR+OFF; t1=t0+4*BAR
    i0,i1=max(0,int(t0*fps)),int(t1*fps)
    seg=L[:,i0:i1]
    W=seg-np.median(seg,axis=1,keepdims=True)
    fig,ax=plt.subplots(2,1,figsize=(30,18),sharex=True)
    for a,img,vmin,vmax in [(ax[0],seg,-55,0),(ax[1],W,0,22)]:
        a.imshow(img,origin='lower',aspect='auto',extent=[0,64,lo_m-0.5,hi_m-0.5],cmap='magma',vmin=vmin,vmax=vmax)
        for m in range(lo_m,hi_m):
            a.axhline(m-0.5,color='w',lw=0.15)
            if m%12 in (0,2,4,5,7,9,11): a.text(-0.6,m-0.3,f"{names[m%12]}{m//12-1}",color='k',fontsize=8)
        for s in range(65): a.axvline(s,color='lime' if s%16==0 else ('w' if s%4==0 else 'gray'),lw=1.5 if s%16==0 else (0.6 if s%4==0 else 0.2))
        for k in range(4): a.text(k*16+0.2,hi_m-1,f"bar {b0+k}",color='lime',fontsize=12)
    plt.tight_layout(); plt.savefig(f"{sys.argv[6]}_{b0:02d}.png",dpi=48); plt.close()
