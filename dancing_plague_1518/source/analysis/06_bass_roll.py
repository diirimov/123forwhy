import librosa, numpy as np, sys
y,sr=librosa.load(sys.argv[1],sr=22050)
P=0.4666940; OFF=-0.006; ST=P/4
lo,hi=int(sys.argv[2]),int(sys.argv[3]); b0,b1=int(sys.argv[4]),int(sys.argv[5])
hop=64; fps=sr/hop
C=np.abs(librosa.cqt(y,sr=sr,hop_length=hop,fmin=librosa.midi_to_hz(lo-1),n_bins=(hi-lo+2)*3,bins_per_octave=36,filter_scale=2))
C=C.reshape(hi-lo+2,3,-1).max(1)[1:-1]
L=20*np.log10(C+1e-6)
names='C C# D D# E F F# G G# A A# B'.split()
chars=' .:-=+*#%@'
for B in range(b0,b1,4):
    print(f"--- bars {B}-{B+3}")
    rows={m:'' for m in range(lo,hi)}
    for s in range(B*16,(B+4)*16):
        a=int((OFF+s*ST+ST*0.5)*fps); b=int((OFF+(s+1)*ST)*fps)
        v=L[:,a:b].mean(1); v=v-v.max()
        for m in range(lo,hi):
            rows[m]+=('|' if s%16==0 else '')+chars[int(np.clip((v[m-lo]+18)/2,0,9))]
    for m in range(hi-1,lo-1,-1): print(f"{names[m%12]:2}{m//12-1} {rows[m]}")
