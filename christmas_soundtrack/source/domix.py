import sys, numpy as np, soundfile as sf, render as R, json
T=dict(np.load('work/raw.npz'))
if len(sys.argv)>1 and sys.argv[1]=='glide':
    T['glide']=R.render_glides(); np.savez('work/raw.npz',**T)
gains=json.loads(open('gains.json').read()) if __import__('os').path.exists('gains.json') else None
S=R.mix(T,gains)
bus=sum(S.values())
print('premaster peak',np.abs(bus).max())
M,l=R.master(bus)
print('LUFS',l,'peak dBFS',20*np.log10(np.abs(M).max()), 'len',M.shape[1]/R.SR)
sf.write('work/master.wav',M.T,R.SR,subtype='PCM_24')
np.save('work/premaster_gain.npy',np.array([np.abs(bus).max()]))
import pickle; pickle.dump({g:sum(S[k] for k in ks) for g,ks in R.GROUPS.items()},open('work/groups.pkl','wb'))
