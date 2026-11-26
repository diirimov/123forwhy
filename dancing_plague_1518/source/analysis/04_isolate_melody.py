import librosa, numpy as np, scipy.ndimage as nd, soundfile as sf
y,sr=librosa.load('sep_inst.wav',sr=22050)
D=librosa.stft(y,n_fft=4096,hop_length=256); M=np.abs(D)
# drone: median over ~3s
drone=nd.median_filter(M,size=(1,257))
perc=nd.median_filter(M,size=(17,1))
harm=nd.median_filter(M,size=(1,9))
mask=(harm**2)/(harm**2+drone**2*1.5+perc**2+1e-9)
mel=librosa.istft(D*mask,hop_length=256,length=len(y))
sf.write('melody_iso.wav',mel,sr)
f0,vf,vp=librosa.pyin(mel,fmin=150,fmax=1400,sr=sr,frame_length=2048,hop_length=128)
np.save('f0.npy',np.vstack([f0,vp]))
