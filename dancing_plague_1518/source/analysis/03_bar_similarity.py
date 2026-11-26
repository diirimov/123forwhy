import librosa, numpy as np
y,sr=librosa.load('sep_inst.wav',sr=22050)
P=0.4666940; OFF=-0.006; ST=P/4; hop=64; fps=sr/hop
C=np.abs(librosa.cqt(y,sr=sr,hop_length=hop,fmin=librosa.midi_to_hz(55),n_bins=30*3,bins_per_octave=36)).reshape(30,3,-1).max(1)
L=np.log(C+1e-4)
nb=48
F=[]
for b in range(nb):
    v=[]
    for s in range(16):
        a=int((OFF+(b*16+s)*ST)*fps); a=max(a,0); e=int((OFF+(b*16+s+1)*ST)*fps)
        v.append(L[:,a:e].mean(1) if e>a else np.zeros(30))
    v=np.array(v); v=v-v.mean(0); F.append(v.flatten())
F=np.array(F); F/=np.linalg.norm(F,axis=1,keepdims=True)+1e-9
Sm=F@F.T
print('    '+''.join(f'{j%10}' for j in range(nb)))
for i in range(nb):
    print(f'{i:2d}  '+''.join(' .:-=+*#%@'[int(np.clip(Sm[i,j]*10,0,9))] if i!=j else 'X' for j in range(nb)), ' best:',[ (j,round(Sm[i,j],2)) for j in np.argsort(-Sm[i])[1:4]])
