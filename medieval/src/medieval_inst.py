"""Physically-inspired medieval instrument models built on top of studio.Inst.

wooden flute (breathy fipple flute with chiff + 'cuts'), bagpipe chanter + drones
(continuous reed with gracenote articulation), hurdy-gurdy (wheel-bowed melody string,
drones, tangent clicks, 'chien' trompette buzz), double-course lute, wordless group chant,
tribal drums (davul, frame drum, darbuka doum/tek), crowd stomps & claps, zills.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'soundtracks', 'src'))
from studio import *  # noqa
from studio import _harm_sum


class MInst(Inst):
    # ------------------------------------------------------------------ wooden flute
    def flute(self, n, dur, vel=0.8, grace=None, prev=None, glide=False, stac=False, vib=1.0, roll=False):
        gate = max(dur * (0.5 if stac else 0.93), 0.05)
        N = int((gate + 0.3) * SR)
        t = np.arange(N) / SR
        p = np.full(N, float(n)) + 0.15 * np.exp(-t / 0.018)
        if glide and prev is not None:
            p += (prev - n) * np.exp(-t / 0.022)
        if grace is not None:  # folk 'cut': a flick from above
            p += (grace - n) * (1 - smoothstep(0.026, 0.042, t))
        if roll:  # turn: n+2, n, n-1, n
            p += np.where(t < 0.04, 2, np.where(t < 0.075, 0, np.where(t < 0.11, -1, 0)))
        p += 0.075 * vib * smoothstep(0.22, 0.45, t) * np.sin(2 * np.pi * 5.0 * t + self.rng.uniform(0, 6))
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        amp = env_gate(t, 0.012 if vel > 0.95 else 0.02, gate, 0.04)
        if gate > 0.3:
            amp *= 1 - 0.1 * smoothstep(0.05, 0.2, t) + 0.1 * smoothstep(0.2, gate, t)
        b = vel
        H = [1.0, 0.2 + 0.18 * b, 0.11 + 0.09 * b, 0.045 + 0.03 * b, 0.022, 0.012, 0.006]
        tone = np.zeros(N)
        for k, h in enumerate(H, 1):
            if k * f0.max() < 16000:
                tone += h * np.sin(k * ph + self.rng.uniform(0, 6))
        f = float(mtof(n))
        nz = self.noise(N)
        breath = bp(nz, f, 5.0) * 0.55 + bp(nz, 2 * f, 4.0) * 0.25 + hp(nz, 5000) * 0.05
        chiff = bp(nz, min(3.2 * f, 9000), 1.5) * np.exp(-t / 0.016) * 1.4
        out = tone * amp + (breath * 0.22 * amp + chiff * (t < 0.06)) * (0.6 + 0.4 * vel)
        return out * vel * 0.9

    # ------------------------------------------------------------------ phrase engine
    def _phrase(self, notes, total, glide=0.007, grace_len=0.032, att=0.006, rel=0.02):
        """notes: (ts, te, midi, grace, vel) in seconds from phrase start. Returns pitch, gate, vel arrays."""
        N = int(total * SR)
        p = np.full(N, np.nan); g = np.zeros(N); v = np.zeros(N)
        onsets = []
        for ts, te, m, gr, vel in notes:
            i0, i1 = int(ts * SR), min(N, int(te * SR))
            p[i0:i1] = m; g[i0:i1] = 1; v[i0:i1] = vel
            if gr is not None:
                p[i0:i0 + int(grace_len * SR)] = gr
            onsets.append(i0)
        # hold pitch through gaps
        idx = np.where(~np.isnan(p), np.arange(N), 0)
        np.maximum.accumulate(idx, out=idx)
        p = p[idx]
        p[np.isnan(p)] = notes[0][2]
        a = np.exp(-1 / (glide * SR))
        p = lfilter([1 - a], [1, -a], p - p[0]) + p[0]
        ga = np.exp(-1 / (att * SR))
        gs = lfilter([1 - ga], [1, -ga], g)
        gs = np.maximum(gs, 0)
        rr = np.exp(-1 / (rel * SR))
        gs = np.maximum(gs, lfilter([1 - rr], [1, -rr], g) * (g == 0))
        va = lfilter([1 - ga], [1, -ga], v)
        return p, gs, va, onsets

    def bagpipe(self, notes, total, vel=1.0):
        p, g, v, on = self._phrase(notes, total, glide=0.004, grace_len=0.03, att=0.008, rel=0.03)
        N = len(p)
        t = np.arange(N) / SR
        p = p + 0.04 * np.sin(2 * np.pi * 3.1 * t) + 0.02 * lp(self.noise(N), 8) * 20
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        out = _harm_sum(ph, f0.max(), lambda k: 1.0 / k ** 0.55 * (1.0 if k % 2 else 0.75), np.full(N, 40.0), maxk=40, fmax=11000)
        out = filt(out, 'peak', 1150, 1.4, 7)
        out = filt(out, 'peak', 2600, 1.6, 5)
        out = hp(out, 280)
        out += bp(self.noise(N), 3000, 0.8) * 0.06
        return out * g * (0.7 + 0.3 * v) * vel * 0.18

    def pipe_drone(self, notes, dur, vel=1.0):
        N = int(dur * SR)
        t = np.arange(N) / SR
        out = np.zeros(N)
        for i, n in enumerate(notes):
            f = mtof(n) * (1 + self.rng.normal(0, 0.0007))
            ph = 2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.21 * t + i)
            out += _harm_sum(ph, f, lambda k: 1.0 / k ** 0.7 * (1 if k % 2 else 0.6), np.full(N, 25.0), maxk=30, fmax=7000)
        out = filt(out, 'peak', 900, 1.0, 4)
        out *= smoothstep(0, 0.35, t) * (1 - smoothstep(dur - 0.15, dur, t))
        return lp(out, 6000) * vel * 0.16

    def bag_groan(self, n, dur=0.9, vel=1.0):
        """Bag inflating: drone sags up into pitch - a comic accent."""
        N = int(dur * SR)
        t = np.arange(N) / SR
        p = n - 7 * np.exp(-t / 0.18) + 0.2 * np.sin(2 * np.pi * 7 * t) * np.exp(-t / 0.3)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        out = _harm_sum(ph, f0.max(), lambda k: 1.0 / k ** 0.6, 5 + 25 * smoothstep(0, 0.4, t), maxk=30, fmax=8000)
        out = filt(out, 'peak', 1100, 1.2, 6)
        return out * smoothstep(0, 0.12, t) * (1 - smoothstep(dur - 0.2, dur, t)) * vel * 0.18

    def hurdy(self, notes, total, vel=1.0, bright=1.0):
        p, g, v, on = self._phrase(notes, total, glide=0.005, grace_len=0.03, att=0.01, rel=0.035)
        N = len(p)
        t = np.arange(N) / SR
        p = p + 0.03 * np.sin(2 * np.pi * 5.5 * t) * smoothstep(0.2, 0.5, t)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        bow = 1 + 0.18 * lp(self.noise(N), 35) * 6
        out = _harm_sum(ph, f0.max(), lambda k: 1.0 / k ** 0.95, np.full(N, 14.0 * bright), maxk=50, fmax=10000) * bow
        out = filt(out, 'peak', 320, 1.0, 3)
        out = filt(out, 'peak', 1050, 1.3, 4)
        out = filt(out, 'peak', 2700, 2.0, 3)
        out += hp(self.noise(N), 3000) * 0.03 * bow
        clicks = np.zeros(N)
        for i in on:
            L = min(300, N - i)
            clicks[i:i + L] += np.exp(-np.arange(L) / 40.0)
        out += hp(clicks * self.noise(N), 1500) * 0.25
        return out * g * (0.7 + 0.3 * v) * vel * 0.35

    def hurdy_drone(self, notes, dur, vel=1.0):
        N = int(dur * SR)
        t = np.arange(N) / SR
        out = np.zeros(N)
        bow = 1 + 0.15 * lp(self.noise(N), 25) * 6
        for i, n in enumerate(notes):
            f = mtof(n) * (1 + self.rng.normal(0, 0.0006))
            ph = 2 * np.pi * f * t
            out += _harm_sum(ph, f, lambda k: 1.0 / k ** 1.0, np.full(N, 10.0), maxk=40, fmax=7000)
        out = filt(out, 'peak', 320, 1.0, 3) * bow
        out *= smoothstep(0, 0.25, t) * (1 - smoothstep(dur - 0.12, dur, t))
        return out * vel * 0.2

    def chien(self, n, vel=1.0, dur=0.14):
        """Trompette 'dog' buzz: one rhythmic wheel-stroke."""
        N = int((dur + 0.05) * SR)
        t = np.arange(N) / SR
        f = mtof(n)
        ph = 2 * np.pi * f * t
        tone = _harm_sum(ph, f, lambda k: 1.0 / k ** 0.7, np.full(N, 20.0), maxk=40, fmax=9000)
        rate = 52 + 10 * vel
        rattle = np.clip(np.sin(2 * np.pi * rate * t) * 4, -1, 1) * 0.5 + 0.5
        e = smoothstep(0, 0.01, t) * (1 - smoothstep(dur * 0.6, dur, t))
        out = hp(tone * (0.35 + 0.65 * rattle), 350) * e
        return out * vel * 0.3

    # ------------------------------------------------------------------ lute (double courses)
    def lute(self, n, dur, vel=0.8, bright=0.82, t60=1.3):
        f = mtof(n)
        gate = max(dur, 0.06)
        N = int((gate + 0.35) * SR)
        t = np.arange(N) / SR
        y = self.ks(f * 1.0012, N, t60=t60, bright=bright * (0.6 + 0.4 * vel))
        y += 0.85 * self.ks(f * 0.9988, N, t60=t60 * 0.9, bright=bright * (0.55 + 0.4 * vel))
        if n < 57:
            y += 0.35 * self.ks(f * 2.001, N, t60=t60 * 0.7, bright=bright)
        y = y + 0.8 * filt(y, 'peak', 230, 1.2, 6) + 0.4 * filt(y, 'peak', 1900, 1.5, 4)
        y = hp(y, 90)
        y += bp(self.noise(N), 4000, 1.0) * np.exp(-t / 0.003) * 0.6
        y *= np.where(t > gate, np.exp(-(t - gate) / 0.06), 1.0)
        return y * vel * 0.27

    # ------------------------------------------------------------------ group chant (wordless)
    def chant(self, n, dur, vel=0.8, vowels='o', cons='h', voices=6, spread=0.018, octave=True, shift=0.93):
        dur = max(dur, 0.1)
        outs = []
        L = int((dur + 0.5) * SR)
        out = np.zeros(L)
        for i in range(voices):
            nn_ = n + self.rng.normal(0, 0.12) - (12 if (octave and i % 3 == 2) else 0)
            y = self.vox(nn_, dur * self.rng.uniform(0.92, 1.0), vel, vowels=vowels, cons=cons,
                         shift=shift * self.rng.uniform(0.94, 1.06), scoop=self.rng.uniform(0.2, 0.8), vib=0.6)
            d = int(self.rng.uniform(0, spread) * SR)
            m = min(L - d, len(y))
            out[d:d + m] += y[:m]
        return out / np.sqrt(voices) * 0.35

    # ------------------------------------------------------------------ percussion
    def davul(self, vel=1.0):
        N = int(0.9 * SR)
        t = np.arange(N) / SR
        f = 58 + 60 * np.exp(-t / 0.03)
        ph = 2 * np.pi * np.cumsum(f) / SR
        body = np.sin(ph) * np.exp(-t / 0.38) + 0.35 * np.sin(1.6 * ph) * np.exp(-t / 0.12)
        slap = lp(self.noise(N), 1800) * np.exp(-t / 0.012) * 0.9 + bp(self.noise(N), 180, 1.0) * np.exp(-t / 0.06) * 0.5
        return np.tanh(1.8 * (body + slap)) * vel * 0.75

    def frame(self, vel=1.0, f=95.0):
        N = int(0.5 * SR)
        t = np.arange(N) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.35 * np.exp(-t / 0.02))) / SR
        y = np.sin(ph) * np.exp(-t / 0.18) + bp(self.noise(N), 700, 0.8) * np.exp(-t / 0.03) * 0.6
        return y * vel * 0.8

    def doum(self, vel=1.0):
        N = int(0.4 * SR)
        t = np.arange(N) / SR
        ph = 2 * np.pi * np.cumsum(110 * (1 + 0.25 * np.exp(-t / 0.015))) / SR
        y = np.sin(ph) * np.exp(-t / 0.16) + lp(self.noise(N), 1000) * np.exp(-t / 0.006) * 0.4
        return y * vel * 0.8

    def tek(self, vel=1.0):
        N = int(0.15 * SR)
        t = np.arange(N) / SR
        y = bp(self.noise(N), 3500, 1.2) * np.exp(-t / 0.01) * 2.2 + np.sin(2 * np.pi * 720 * t) * np.exp(-t / 0.025) * 0.5
        return y * vel * 0.75

    def stomp(self, vel=1.0, crowd=5):
        N = int(0.4 * SR)
        out = np.zeros(N)
        for i in range(crowd):
            d = int(abs(self.rng.normal(0, 0.007)) * SR)
            t = np.arange(N - d) / SR
            f = 62 * self.rng.uniform(0.9, 1.1)
            y = np.sin(2 * np.pi * f * t * (1 + 0.6 * np.exp(-t / 0.01))) * np.exp(-t / 0.09)
            y += bp(self.noise(N - d), 320 * self.rng.uniform(0.85, 1.15), 1.5) * np.exp(-t / 0.035) * 0.9
            y += bp(self.noise(N - d), 1100, 2.5) * np.exp(-t / 0.015) * 0.4
            out[d:] += y
        return out / np.sqrt(crowd) * vel * 0.7

    def crowdclap(self, vel=1.0, crowd=7):
        N = int(0.4 * SR)
        out = np.zeros(N)
        for i in range(crowd):
            d = int(abs(self.rng.normal(0, 0.009)) * SR)
            t = np.arange(N - d) / SR
            c = bp(self.noise(N - d), self.rng.uniform(900, 1900), 1.3) * np.exp(-t / 0.011) * 2.5
            out[d:] += c
        out = out / np.sqrt(crowd)
        t = np.arange(N) / SR
        out += hp(self.noise(N), 800) * np.exp(-t / 0.07) * 0.15
        return out * vel * 1.25

    def zill(self, vel=1.0):
        N = int(1.2 * SR)
        t = np.arange(N) / SR
        y = np.zeros(N)
        for r, a, tau in ((2950, 1, 0.5), (4330, 0.6, 0.35), (6120, 0.4, 0.25), (7790, 0.25, 0.15)):
            y += a * np.sin(2 * np.pi * r * t + self.rng.uniform(0, 6)) * np.exp(-t / tau)
        y += hp(self.noise(N), 6000) * np.exp(-t / 0.004)
        return y * vel * 0.25

    def shake(self, dur, vel=1.0):
        """Tambourine shake/roll."""
        N = int(dur * SR)
        t = np.arange(N) / SR
        am = 0.5 + 0.5 * np.sin(2 * np.pi * 14 * t) ** 2
        return hp(self.noise(N), 6500) * am * smoothstep(0, dur * 0.7, t) * (1 - smoothstep(dur - 0.03, dur, t)) * vel * 0.3

    def boom(self, vel=1.0):
        N = int(2.2 * SR)
        t = np.arange(N) / SR
        ph = 2 * np.pi * np.cumsum(36 + 70 * np.exp(-t / 0.06)) / SR
        y = np.sin(ph) * np.exp(-t / 0.7)
        y += lp(self.noise(N), 300) * np.exp(-t / 0.2) * 0.4
        return np.tanh(1.6 * y) * vel


_MN = dict(davul=1.0, frame=1.0, doum=1.0, tek=1.0, stomp=1.0, crowdclap=1.0, zill=1.0)
