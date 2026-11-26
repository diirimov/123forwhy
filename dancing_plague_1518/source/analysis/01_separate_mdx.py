import onnxruntime as ort, numpy as np, soundfile as sf, sys
sess=ort.InferenceSession(sys.argv[1]); inp=sess.get_inputs()[0]; print(inp.shape)
_,C,F,T=inp.shape; T=int(T); F=int(F)
n_fft=6144; hop=1024; dim_f=F; dim_t=T
x,sr=sf.read(sys.argv[2]); x=x.T.astype(np.float32)  # 2,N
import scipy.signal as ss
win=np.hanning(n_fft+1)[:-1].astype(np.float32)
def stft(a):  # a: 2,L -> 2,bins,frames (center)
    a=np.pad(a,((0,0),(n_fft//2,n_fft//2)),mode='reflect')
    nfr=1+(a.shape[1]-n_fft)//hop
    idx=np.arange(n_fft)[None,:]+hop*np.arange(nfr)[:,None]
    fr=a[:,idx]*win
    return np.fft.rfft(fr,axis=-1).transpose(0,2,1)
def istft(S,L):
    fr=np.fft.irfft(S.transpose(0,2,1),n=n_fft,axis=-1)*win
    nfr=fr.shape[1]; out=np.zeros((2,n_fft+hop*(nfr-1)),np.float32); wsum=np.zeros(out.shape[1],np.float32)
    for i in range(nfr):
        out[:,i*hop:i*hop+n_fft]+=fr[:,i]; wsum[i*hop:i*hop+n_fft]+=win**2
    out/=np.maximum(wsum,1e-8); return out[:,n_fft//2:n_fft//2+L]
chunk=hop*(dim_t-1); trim=n_fft//2; gen=chunk-2*trim
N=x.shape[1]; pad=gen-N%gen
xp=np.concatenate([np.zeros((2,trim),np.float32),x,np.zeros((2,pad+trim),np.float32)],1)
out=np.zeros_like(xp)
for i in range(0,N+pad,gen):
    w=xp[:,i:i+chunk]
    S=stft(w)[:, :dim_f, :dim_t]
    z=np.concatenate([S.real,S.imag],0)  # order: L.re,R.re,L.im,R.im ? UVR uses view_as_real then permute -> [L.re,L.im,R.re,R.im]
    z=np.stack([S[0].real,S[0].imag,S[1].real,S[1].imag])[None].astype(np.float32)
    y=sess.run(None,{inp.name:z})[0][0]
    Sy=np.zeros((2,n_fft//2+1,dim_t),np.complex64)
    Sy[0,:dim_f]=y[0]+1j*y[1]; Sy[1,:dim_f]=y[2]+1j*y[3]
    o=istft(Sy,chunk)
    out[:,i+trim:i+chunk-trim]=o[:,trim:-trim]
inst=out[:,trim:trim+N]*float(sys.argv[4] if len(sys.argv)>4 else 1.022)
sf.write(sys.argv[3]+'_inst.wav',inst.T,sr); sf.write(sys.argv[3]+'_vox.wav',(x-inst).T,sr)
print('done')
