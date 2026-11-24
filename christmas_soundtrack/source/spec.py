import numpy as np, soundfile as sf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, scipy.signal as ss, sys
y,sr=sf.read(sys.argv[1]); m=y.mean(1)
f,t,S=ss.spectrogram(m,sr,nperseg=4096,noverlap=3072)
fig,ax=plt.subplots(2,1,figsize=(18,9),gridspec_kw={'height_ratios':[3,1]})
ax[0].pcolormesh(t,f,10*np.log10(S+1e-12),vmin=-120,vmax=-40,shading='auto',cmap='magma'); ax[0].set_yscale('symlog',linthresh=200); ax[0].set_ylim(30,20000)
for b in range(0,49,4): ax[0].axvline(b*1.875,color='c',lw=0.6); ax[1].axvline(b*1.875,color='c',lw=0.6)
hop=int(sr*0.05); r=[20*np.log10(np.sqrt(np.mean(m[i:i+hop]**2))+1e-9) for i in range(0,len(m),hop)]
ax[1].plot(np.arange(len(r))*0.05,r); ax[1].set_xlim(0,90); ax[0].set_xlim(0,90); ax[1].set_ylim(-40,-5)
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=70)
