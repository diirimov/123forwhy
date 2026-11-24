import sys, numpy as np, render as R
T=dict(np.load('work/raw.npz'))
for name in sys.argv[1:]:
    if name in R.GM: T[name]=R.render_gm(name,R.EV[name])[1]
    elif name=='pluck': T[name]=R.render_pluck(R.EV['pluck'])
    elif name=='glide': T[name]=R.render_glides()
    elif name=='bass':
        m,s=R.render_bass(); T['bass']=np.stack([m,m]); T['sub']=np.stack([s,s])
    elif name=='full':
        T=R.build_raw()
    print('rendered',name)
np.savez('work/raw.npz',**T)
