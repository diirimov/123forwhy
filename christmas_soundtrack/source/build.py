import time, numpy as np, render as R
t=time.time(); T=R.build_raw(); print('raw built',time.time()-t)
np.savez('work/raw.npz', **T)
for k,v in T.items(): print(k, v.shape, float(np.abs(v).max()))
