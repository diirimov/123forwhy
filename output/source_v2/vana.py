import numpy as np, librosa, soundfile as sf, json
v,sr=sf.read('vocals.wav'); v=v.mean(1); SR=sr
hop=441  # 10ms
rms=librosa.feature.rms(y=v,frame_length=2048,hop_length=hop)[0]; db=20*np.log10(rms+1e-6)
t=np.arange(len(rms))*hop/SR
act=db>-32
# segments of vocal activity
segs=[];s=None
for i,a in enumerate(act):
    if a and s is None: s=i
    if not a and s is not None:
        if i-s>8: segs.append((t[s],t[i]))
        s=None
# merge gaps<0.12
m=[]
for a,b in segs:
    if m and a-m[-1][1]<0.12: m[-1]=(m[-1][0],b)
    else: m.append((a,b))
print('vocal phrases (video s):'); print([ (round(a,2),round(b,2)) for a,b in m])
f0,vf,vp=librosa.pyin(v,fmin=80,fmax=1100,sr=SR,frame_length=2048,hop_length=hop)
midi=librosa.hz_to_midi(f0)
json.dump({'t':t.tolist(),'midi':[None if np.isnan(x) else round(float(x),2) for x in midi],'db':db.round(1).tolist(),'phr':m},open('vocal_analysis.json','w'))
# per 0.25s summary 30-60
for s0 in np.arange(0,60,0.25):
    k=(t>=s0)&(t<s0+0.25); mm=midi[k]; mm=mm[~np.isnan(mm)]
    note=librosa.midi_to_note(np.median(mm)) if len(mm)>3 else '-'
    print(f"{s0:5.2f} {db[k].mean():6.1f} {note}", end=' | ' if int(s0*4)%4!=3 else '\n')
