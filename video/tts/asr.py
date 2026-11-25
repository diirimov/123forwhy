import sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from pocketsphinx import Decoder
def load(p):
    a, sr = sf.read(p); a = a if a.ndim == 1 else a.mean(1)
    return (resample_poly(a, 16000, sr) * 32767).astype(np.int16)
for p in sys.argv[1:]:
    pcm = load(p)
    d = Decoder(samprate=16000); d.start_utt(); d.process_raw(pcm.tobytes(), full_utt=True); d.end_utt()
    free = d.hyp().hypstr if d.hyp() else ''
    d2 = Decoder(samprate=16000); d2.set_align_text("in medieval times surviving your doctor was a challenge")
    d2.start_utt(); d2.process_raw(pcm.tobytes(), full_utt=True); d2.end_utt()
    segs = [(s.word, round(s.start_frame/100,2), round(s.end_frame/100,2)) for s in d2.seg() if s.word not in ('<sil>','<s>','</s>')]
    sc = d2.hyp().score if d2.hyp() else None
    print(p, '| free:', free, '| align score', sc); print('   ', segs)
