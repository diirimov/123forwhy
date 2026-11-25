import sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
text = "In medieval times, surviving your doctor was a challenge."
for v, sp in [("bm_george", 1.0), ("bm_fable", 1.0), ("am_michael", 1.0), ("am_fenrir", 1.0), ("bm_lewis", 1.0)]:
    a, sr = k.create(text, voice=v, speed=sp, lang="en-gb" if v.startswith("b") else "en-us")
    sf.write(f"narr_{v}.wav", a, sr)
    nz = np.where(np.abs(a) > 0.02)[0]
    print(v, sr, "dur %.2f speech %.2f-%.2f peak %.2f" % (len(a)/sr, nz[0]/sr, nz[-1]/sr, np.abs(a).max()))
