import librosa, numpy as np
y,sr=librosa.load('sep_inst.wav',sr=22050)
hop=128; fps=sr/hop
S=np.abs(librosa.stft(y,n_fft=1024,hop_length=hop)); f=librosa.fft_frequencies(sr=sr,n_fft=1024)
lo=S[(f>30)&(f<120)].sum(0); on=np.maximum(0,np.diff(np.log(lo+1e-3),prepend=0))
# local tempo via dynamic programming from librosa using this onset env
tempo,beats=librosa.beat.beat_track(onset_envelope=on,sr=sr,hop_length=hop,start_bpm=128.4,tightness=400,units='time')
ibi=np.diff(beats)
for i in range(0,len(beats)-1,4):
    print(f"{beats[i]:6.2f} {60/np.mean(ibi[i:i+4]):6.1f}", end=' | ')
    if i%32==28: print()
np.save('beats_raw.npy',beats)
