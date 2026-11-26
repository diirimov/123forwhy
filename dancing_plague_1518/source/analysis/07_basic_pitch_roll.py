import pickle, numpy as np, sys
notes,_=pickle.load(open('bp_iso.pkl','rb'))
P=0.4666940; OFF=-0.006; ST=P/4
names='C C# D D# E F F# G G# A A# B'.split()
nn=lambda m:f"{names[m%12]}{m//12-1}"
lo,hi=int(sys.argv[1]),int(sys.argv[2]); b0,b1=int(sys.argv[3]),int(sys.argv[4])
ev=[]
for s,e,m,a,_ in notes:
    if lo<=m<hi:
        q=(s-OFF)/ST; ev.append((int(round(q)),max(1,int(round((e-s)/ST))),int(m),a))
for b in range(b0,b1):
    row=[f"{st-16*b:2d}:{nn(m)}/{d}" for st,d,m,a in sorted(ev) if 16*b<=st<16*b+16 and a>0.2]
    print(f"bar{b:2d} {b*16*ST+OFF:5.1f}s ", ' '.join(row))
