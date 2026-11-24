"""V2 instruments + musical SFX (48 kHz). Builds on medieval_inst.MInst (flute, hurdy-gurdy, lute, folk drums)."""
from engine import *  # noqa
from engine import _onepole, _harm_sum
sys.path.insert(0, os.path.join(HERE, '..', '..', 'medieval', 'src'))
import medieval_inst
from medieval_inst import MInst


class Inst2(MInst):
    # ---------------------------------------------------------------- folk fiddle
    def fiddle(self, notes, total, vel=1.0, drone=None):
        """notes: (ts, te, midi, grace, vel). Bowed string: Helmholtz saw + bow noise + violin body."""
        p, g, v, on = self._phrase(notes, total, glide=0.012, grace_len=0.035, att=0.014, rel=0.05)
        N = len(p)
        t = np.arange(N) / SR
        # expressive vibrato that restarts on each note
        vib_env = np.zeros(N)
        last = 0
        for i in on + [N]:
            if i > last:
                tt = np.arange(i - last) / SR
                vib_env[last:i] = smoothstep(0.12, 0.3, tt)
            last = i
        p = p + 0.16 * vib_env * np.sin(2 * np.pi * 5.8 * t)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        bow = 1 + 0.12 * _onepole(self.noise(N), np.exp(-1 / (0.01 * SR))) * 10
        acc = np.zeros(N)
        for i in on:
            L = min(int(0.06 * SR), N - i)
            acc[i:i + L] += np.exp(-np.arange(L) / (0.018 * SR))
        bright = 9 + 10 * acc + 4 * v
        out = _harm_sum(ph, f0.max(), lambda k: 1.0 / k, bright, maxk=60, fmax=12000) * bow
        if drone is not None:
            fd = mtof(drone)
            out += 0.35 * _harm_sum(2 * np.pi * fd * t, fd, lambda k: 1.0 / k, np.full(N, 6.0), maxk=30, fmax=9000) * bow
        for f, q, gdb in ((290, 1.6, 6), (480, 2.0, 4), (1050, 1.5, 3), (2700, 1.2, 6), (4200, 2.0, -4)):
            out = filt(out, 'peak', f, q, gdb)
        out = hp(out, 190)
        scratch = bp(self.noise(N), 3500, 0.7) * acc * 0.25
        out = (out + scratch) * g * (0.6 + 0.4 * v)
        return out * vel * 0.12

    # ---------------------------------------------------------------- church bell (tuned)
    def church_bell(self, n, vel=1.0, ring=3.0, big=False):
        f = mtof(n)
        N = int(ring * 1.6 * SR)
        t = np.arange(N) / SR
        parts = [(0.5, 0.6, 1.0), (1.0, 1.0, 0.8), (1.19, 0.55, 0.55), (1.5, 0.35, 0.45),
                 (2.0, 0.6, 0.35), (2.51, 0.25, 0.25), (2.66, 0.25, 0.2), (3.01, 0.15, 0.15), (4.1, 0.1, 0.1)]
        y = np.zeros(N)
        for r, a, d in parts:
            if r * f > 16000:
                continue
            beat = 1 + 0.1 * np.sin(2 * np.pi * self.rng.uniform(0.5, 2.0) * t)
            y += a * np.sin(2 * np.pi * r * f * t + self.rng.uniform(0, 6)) * np.exp(-t / (ring * d)) * beat
        strike = bp(self.noise(N), 2500, 1.0) * np.exp(-t / 0.006) * 0.8 + np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.02) * 0.4
        y = (y + strike) * (1 - np.exp(-t / 0.0015))
        if big:
            y += 0.4 * np.sin(2 * np.pi * 0.25 * f * t) * np.exp(-t / ring)
        return y * vel * 0.4

    def handbell(self, n, vel=1.0):
        f = mtof(n)
        N = int(1.2 * SR)
        t = np.arange(N) / SR
        y = sum(a * np.sin(2 * np.pi * r * f * t) * np.exp(-t / d) for r, a, d in ((1, 1, 0.6), (2.4, 0.4, 0.25), (5.3, 0.25, 0.1)))
        return y * (1 - np.exp(-t / 0.001)) * vel * 0.5

    # ---------------------------------------------------------------- knocker-up percussion
    def glass_tap(self, vel=1.0, pitch=1.0):
        N = int(0.35 * SR)
        t = np.arange(N) / SR
        y = np.zeros(N)
        for r, a, d in ((2210, 1, 0.09), (3480, 0.6, 0.06), (5150, 0.45, 0.04), (7020, 0.3, 0.03), (1380, 0.3, 0.05)):
            y += a * np.sin(2 * np.pi * r * pitch * t + self.rng.uniform(0, 6)) * np.exp(-t / d)
        tick = hp(self.noise(N), 3000) * np.exp(-t / 0.0015) * 1.2
        wood = np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.006) * 0.5
        return (y * 0.6 + tick + wood) * vel * 0.4

    def door_knock(self, vel=1.0, pitch=1.0):
        N = int(0.3 * SR)
        t = np.arange(N) / SR
        y = np.zeros(N)
        for r, a, d in ((118, 1.0, 0.07), (247, 0.7, 0.05), (395, 0.5, 0.035), (610, 0.3, 0.02)):
            y += a * np.sin(2 * np.pi * r * pitch * t) * np.exp(-t / d)
        y += bp(self.noise(N), 1500, 1.0) * np.exp(-t / 0.004) * 1.2
        return np.tanh(1.5 * y) * vel * 0.7

    def stick_click(self, vel=1.0):
        N = int(0.08 * SR)
        t = np.arange(N) / SR
        y = np.sin(2 * np.pi * 1850 * t) * np.exp(-t / 0.012) + 0.5 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t / 0.006)
        return (y + hp(self.noise(N), 4000) * np.exp(-t / 0.001)) * vel * 0.4

    # ---------------------------------------------------------------- royal
    def coins(self, vel=1.0, n=7, dur=0.12):
        N = int((dur + 0.3) * SR)
        y = np.zeros(N)
        for _ in range(n):
            i = int(self.rng.uniform(0, dur) * SR)
            L = N - i
            t = np.arange(L) / SR
            f = self.rng.uniform(3800, 7500)
            ping = sum(a * np.sin(2 * np.pi * f * r * t) for r, a in ((1, 1), (1.47, 0.6), (2.09, 0.4))) * np.exp(-t / self.rng.uniform(0.03, 0.09))
            y[i:] += ping * self.rng.uniform(0.4, 1.0)
        return y * vel * 0.12

    def fanfare_note(self, n, dur, vel=0.9, fall=False):
        """Natural trumpet: brass voice + bell resonance."""
        y = self.brass_voice(n, dur, vel, fall=fall, kind='tpt', sfz=True)
        y = filt(y, 'peak', 1400, 1.0, 4)
        return y

    def door_slam(self, vel=1.0):
        N = int(1.6 * SR)
        t = np.arange(N) / SR
        body = sum(a * np.sin(2 * np.pi * r * t) * np.exp(-t / d) for r, a, d in ((48, 1.0, 0.35), (73, 0.7, 0.25), (131, 0.4, 0.15)))
        crack = lp(self.noise(N), 2500) * np.exp(-t / 0.02)
        rattle = bp(self.noise(N), 900, 2) * np.exp(-t / 0.15) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t))
        return np.tanh(1.4 * (body + crack + 0.3 * rattle)) * vel * 0.8

    # ---------------------------------------------------------------- sin-eater
    def whisper(self, vel=1.0, kind='s', dur=0.12):
        """Breathy ghost consonant: 's', 'sh', 'h' (unvoiced through formants)."""
        N = int((dur + 0.08) * SR)
        t = np.arange(N) / SR
        nz = self.noise(N)
        if kind == 's':
            y = bp(nz, 6500, 1.2) + 0.4 * bp(nz, 4200, 2)
        elif kind == 'sh':
            y = bp(nz, 2800, 1.0) + 0.5 * bp(nz, 4500, 1.5)
        else:
            y = bp(nz, 1200, 1.5) + bp(nz, 2400, 2) * 0.6
        e = smoothstep(0, dur * 0.35, t) * (1 - smoothstep(dur * 0.5, dur + 0.05, t))
        return y * e * vel * 0.6

    def crow(self, vel=1.0):
        rng = self.rng
        outs = []
        for k in range(rng.integers(2, 4)):
            dur = rng.uniform(0.18, 0.26)
            y = syllable(rng, 'h', 'aE', 66 + rng.normal(0, 0.5), dur, 'fall', 1.0, False, 1.35, breath=0.6)
            y = np.tanh(3.5 * y) * 0.6
            y = filt(y, 'peak', 1600, 1.0, 8)
            outs.append(np.r_[y, np.zeros(int(rng.uniform(0.06, 0.12) * SR))])
        return hp(np.concatenate(outs), 500) * vel * 0.6

    def creak(self, dur=0.9, vel=1.0, f0=35, f1=110):
        """Stick-slip friction: irregular pulse train through wooden resonances."""
        N = int(dur * SR)
        t = np.arange(N) / SR
        rate = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(np.pi * t / dur)) + 8 * np.sin(2 * np.pi * 3 * t)
        ph = np.cumsum(rate / SR)
        pulses = np.diff(np.floor(ph), prepend=0) * (0.6 + 0.4 * self.rng.random(N))
        y = np.zeros(N)
        for f, q in ((620, 6), (1350, 8), (2300, 6), (330, 4)):
            y += bp(pulses, f, q)
        e = smoothstep(0, 0.05, t) * (1 - smoothstep(dur - 0.1, dur, t))
        return y * e * vel * 1.2

    def crunch(self, vel=1.0, dur=0.25):
        N = int((dur + 0.05) * SR)
        y = np.zeros(N)
        for _ in range(int(dur * 260)):
            i = int(self.rng.uniform(0, dur) ** 1.3 / dur ** 0.3 * SR)
            L = int(self.rng.uniform(0.002, 0.008) * SR)
            if i + L < N:
                y[i:i + L] += self.noise(L) * np.exp(-np.arange(L) / (L / 3)) * self.rng.uniform(0.2, 1)
        y = bp(y, 2200, 0.6) + 0.5 * bp(y, 600, 1.0)
        return y * vel * 0.8

    def ghost_swell(self, dur=1.6, vel=1.0, n=nn('A4')):
        """Reverse-swell ghost choir 'oooh' into a hit."""
        c = crowd(self.rng, '', 'u', n, dur, n_m=3, n_f=5, spread=0.05, contour='sung', effort=0.25, vib=0.25, breath=0.5)
        m = c.mean(0)[:int(dur * SR)]
        t = np.arange(len(m)) / SR
        return m * smoothstep(0, dur, t) ** 2 * vel

    def reverse_swell(self, dur=0.8, vel=1.0):
        N = int(dur * SR)
        t = np.arange(N) / SR
        y = hp(self.noise(N), 1500) * smoothstep(0, dur, t) ** 3
        y += np.sin(2 * np.pi * np.cumsum(mtof(60 + 24 * (t / dur) ** 2)) / SR) * smoothstep(0, dur, t) ** 2 * 0.2
        return y * vel * 0.6

    # ---------------------------------------------------------------- cartoon / comedy
    def slide_whistle(self, up=True, dur=0.45, vel=1.0):
        N = int(dur * SR)
        t = np.arange(N) / SR
        p = (72 + 24 * smoothstep(0, 1, t / dur)) if up else (96 - 24 * smoothstep(0, 1, t / dur))
        ph = 2 * np.pi * np.cumsum(mtof(p)) / SR
        y = np.sin(ph) + 0.05 * np.sin(2 * ph) + 0.06 * bp(self.noise(N), 3000, 1)
        return y * env_gate(t, 0.02, dur - 0.05, 0.03) * vel * 0.4

    def bonk(self, vel=1.0):
        N = int(0.5 * SR)
        t = np.arange(N) / SR
        p = 62 - 8 * (1 - np.exp(-t / 0.05))
        y = np.sin(2 * np.pi * np.cumsum(mtof(p)) / SR) * np.exp(-t / 0.12)
        y += self.wood(1.0, 700)[:N] if len(self.wood(1.0, 700)) >= N else np.r_[self.wood(1.0, 700), np.zeros(N - len(self.wood(1.0, 700)))]
        return y * vel * 0.6

    def footstep(self, vel=1.0, hard=True):
        N = int(0.15 * SR)
        t = np.arange(N) / SR
        heel = lp(self.noise(N), 900 if hard else 500) * np.exp(-t / 0.012)
        thud = np.sin(2 * np.pi * 95 * t) * np.exp(-t / 0.03)
        click = hp(self.noise(N), 3000) * np.exp(-t / 0.002) * (0.6 if hard else 0.1)
        return (heel + thud * 0.6 + click) * vel * 0.5

    def snore(self, dur=1.6, vel=1.0):
        """Cartoon snore: rattling inhale + whistling exhale."""
        N = int(dur * SR)
        t = np.arange(N) / SR
        half = dur * 0.55
        rate = 38 + 6 * np.sin(2 * np.pi * 1.5 * t)
        rattle = (np.sin(2 * np.pi * np.cumsum(rate) / SR) > 0.3).astype(float)
        inh = lp(self.noise(N) * (0.3 + rattle), 900) * smoothstep(0, half * 0.6, t) * (1 - smoothstep(half * 0.8, half, t))
        whist_p = 84 + 3 * np.sin(np.pi * np.clip((t - half) / (dur - half), 0, 1)) - 5 * np.clip((t - half) / (dur - half), 0, 1)
        whist = np.sin(2 * np.pi * np.cumsum(mtof(whist_p)) / SR) * smoothstep(half, half + 0.1, t) * (1 - smoothstep(dur - 0.25, dur, t))
        breath = bp(self.noise(N), 1800, 1) * smoothstep(half, half + 0.1, t) * (1 - smoothstep(dur - 0.3, dur, t)) * 0.3
        return (inh * 1.2 + whist * 0.25 + breath) * vel * 0.6
