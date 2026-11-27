"""Opening narration (DP-style) mixed over the approved soundtrack.

    python3 tools/make_voiceover.py [--synth]

--synth regenerates the voice with Kokoro TTS (pip install kokoro-onnx; model files kokoro-v1.0.onnx + voices-v1.0.bin
from github.com/thewh1teagle/kokoro-onnx releases, path in $KOKORO_DIR). Without it the committed raw take is used.
The soundtrack WAV is never modified: the music is only ducked by 4 dB under the voice in the mix copy
audio/PIED_PIPER_V2_MIX.wav, which is what the film is muxed with.
"""
import os, sys, json
import numpy as np, soundfile as sf
from scipy import signal
import pyloudnorm as pyln

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = "In twelve eighty-four... one hundred and thirty children vanished."
VOICE, SPEED = "am_onyx", 1.0
AT = 0.10                      # narration start (s): the first word sits on the hook's downbeat
RAW = os.path.join(HERE, "audio/vo/VO_raw_am_onyx.wav")

if "--synth" in sys.argv:
    from kokoro_onnx import Kokoro
    d = os.environ.get("KOKORO_DIR", ".")
    k = Kokoro(os.path.join(d, "kokoro-v1.0.onnx"), os.path.join(d, "voices-v1.0.bin"))
    a, sr = k.create(TEXT, voice=VOICE, speed=SPEED, lang="en-us")
    sf.write(RAW, a, sr)

music, sr = sf.read(os.path.join(HERE, "audio/PIED_PIPER_NEW_SOUNDTRACK.wav"))
vo, vsr = sf.read(RAW)
vo = signal.resample_poly(vo, sr, vsr)
# voice chain: high-pass, de-mud, presence, gentle compression (static), warm saturation
sos = signal.butter(2, 90, "high", fs=sr, output="sos"); vo = signal.sosfilt(sos, vo)
def peq(x, f0, g, q):
    A = 10 ** (g / 40); w = 2 * np.pi * f0 / sr; al = np.sin(w) / (2 * q)
    return signal.lfilter([1 + al * A, -2 * np.cos(w), 1 - al * A], [1 + al / A, -2 * np.cos(w), 1 - al / A], x)
vo = peq(vo, 280, -2.5, 1.0); vo = peq(vo, 3200, 2.5, .9); vo = peq(vo, 120, 1.5, .8)
env = signal.lfilter([1 - np.exp(-1 / (.01 * sr))], [1, -np.exp(-1 / (.01 * sr))], np.abs(vo))
gr = np.minimum(1, (np.percentile(env, 95) * .5 / np.maximum(env, 1e-9)) ** .4)
vo = np.tanh(vo * gr * 1.5) / 1.5
meter = pyln.Meter(sr)
vo = vo * 10 ** ((-16.0 - meter.integrated_loudness(np.stack([vo, vo], 1))) / 20)   # voice at -16 LUFS (music is -14)
i0 = int(AT * sr); n = len(vo)
v2 = np.zeros_like(music); v2[i0:i0 + n, 0] += vo; v2[i0:i0 + n, 1] += vo
# duck the music 4 dB under the voice (80 ms ramps)
act = np.zeros(len(music)); act[i0:i0 + n] = 1
k = int(.08 * sr); act = np.convolve(act, np.ones(2 * k) / (2 * k), "same")
mix = music * (10 ** (-4 * act / 20))[:, None] + v2
up = signal.resample_poly(mix, 4, 1, axis=0); tp = 20 * np.log10(np.abs(up).max())
if tp > -1.0:
    mix *= 10 ** ((-1.05 - tp) / 20)
    print("trimmed whole mix by", round(-1.05 - tp, 2), "dB to keep true peak <= -1 dBTP")
sf.write(os.path.join(HERE, "audio/PIED_PIPER_V2_MIX.wav"), mix, sr, subtype="PCM_24")
up = signal.resample_poly(mix, 4, 1, axis=0)
print(f"voice {AT:.2f}-{AT + n / sr:.2f}s | mix {meter.integrated_loudness(mix):.2f} LUFS, TP {20 * np.log10(np.abs(up).max()):.2f} dBTP")
json.dump(dict(text=TEXT, voice=f"Kokoro TTS {VOICE} speed {SPEED}", start=AT, end=round(AT + n / sr, 3), duck_db=-4,
               phrases=[["In twelve eighty-four", AT + .04, AT + 1.22], ["one hundred and thirty", AT + 1.32, AT + 2.07], ["children vanished.", AT + 2.15, AT + 3.34]]),
          open(os.path.join(HERE, "data/voiceover.json"), "w"), indent=1)
