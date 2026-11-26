import librosa, numpy as np, sys
y,sr=librosa.load(sys.argv[1],sr=22050)
P=0.4666940; OFF=-0.006; ST=P/4
lo,hi=int(sys.argv[2]),int(sys.argv[3]); b0,b1=int(sys.argv[4]),int(sys.argv[5])
hop=64; fps=sr/hop
C=np.abs(librosa.cqt(y,sr=sr,hop_length=hop,fmin=librosa.midi_to_hz(lo-1),n_bins=(hi-lo+2)*3,bins_per_octave=36,filter_scale=1.5))
C=C.reshape(hi-lo+2,3,-1).max(1)[1:-1]  # semitone bins lo..hi-1
L=20*np.log10(C+1e-6)
nst=int((len(y)/sr-OFF)/ST)
M=np.zeros((hi-lo,nst))
for s in range(nst):
    a=int((OFF+s*ST)*fps)+2; b=int((OFF+(s+1)*ST)*fps)-1
    if a<0: a=0
    M[:,s]=L[:,a:b].mean(1) if b>a else -120
W=np.zeros_like(M)
for s in range(nst):
    w0,w1=max(0,s-64),min(nst,s+64)
    W[:,s]=M[:,s]-np.percentile(M[:,w0:w1],20,axis=1)
# also frame-relative: subtract per-step max
names='C C# D D# E F F# G G# A A# B'.split()
chars=' .:-=+*#%@'
for B in range(b0,b1,4):
    print(f"--- bars {B}-{B+3}  t={B*16*ST+OFF:.2f}s")
    for m in range(hi-1,lo-1,-1):
        row=''
        for s in range(B*16,min(nst,(B+4)*16)):
            v=W[m-lo,s]; rel=M[m-lo,s]-M[:,s].max()
            c=chars[int(np.clip(v/2.5,0,9))] if rel>-24 else ' '
            row+=('|' if s%16==0 else '')+c
        print(f"{names[m%12]:2}{m//12-1} {row}")
