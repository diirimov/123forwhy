"""Film look: grade, bloom, vignette, paper texture + grain (same family as the Dancing Plague look)."""
import numpy as np, cv2
from core import W, H

_paper = None
_vig = None
_grains = None


def _init():
    global _paper, _vig, _grains
    if _paper is not None:
        return
    rng = np.random.default_rng(5)
    # paper fibre texture (static)
    n = rng.standard_normal((H // 4, W // 4)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 2.5)
    n2 = cv2.resize(rng.standard_normal((H // 16, W // 16)).astype(np.float32), (W // 4, H // 4))
    tex = n * 0.6 + cv2.GaussianBlur(n2, (0, 0), 3) * 1.2
    tex = cv2.resize(tex, (W, H), interpolation=cv2.INTER_CUBIC)
    tex = tex / (np.abs(tex).max() + 1e-6)
    _paper = (1.0 + 0.045 * tex)[..., None].astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.48) / (H * 0.62)) ** 2)
    _vig = (1 - 0.55 * np.clip(d - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
    _grains = [((rng.standard_normal((H // 2, W // 2)).astype(np.float32)) * 0.022) for _ in range(6)]


def grade(img, frame, warm=0.5, bloom=0.35, flash=0.0, sat=0.92, lift=(0.035, 0.03, 0.06)):
    """img: HxWx4 uint8 RGBA from skia (RGBA order). returns HxWx3 uint8 RGB"""
    _init()
    x = img[..., :3].astype(np.float32) / 255.0 * 1.1
    # bloom
    if bloom > 0:
        small = cv2.resize(x, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
        br = np.clip(small - 0.62, 0, 1)
        br = cv2.GaussianBlur(br, (0, 0), 9)
        x = x + cv2.resize(br, (W, H), interpolation=cv2.INTER_LINEAR) * bloom * 1.6
    # saturation
    lum = (x[..., 0:1] * 0.3 + x[..., 1:2] * 0.59 + x[..., 2:3] * 0.11)
    x = lum + (x - lum) * sat
    # split tone: shadows violet-blue, highlights warm parchment
    sh = np.clip(1 - lum * 2, 0, 1)
    hi = np.clip(lum * 2 - 1, 0, 1)
    x = x + sh * np.array(lift, np.float32) + hi * np.array([0.05, 0.03, -0.02], np.float32) * warm
    # paper + vignette
    x = x * _paper * _vig
    # grain (changes 30x/s)
    g = _grains[(frame // 2) % len(_grains)]
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    x = x + g * (0.6 + 0.4 * (1 - lum))
    if flash > 0:
        x = x + flash * np.array([1.0, 0.92, 0.75], np.float32) * 0.6
    # soft filmic shoulder
    x = np.clip(x, 0, None)
    x = x / (1 + np.maximum(x - 0.85, 0) * 1.2)
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


def over(base, ov):
    """alpha-composite RGBA overlay (premultiplied from skia) on RGB uint8"""
    a = ov[..., 3:4].astype(np.float32) / 255.0
    return (base.astype(np.float32) * (1 - a) + ov[..., :3].astype(np.float32) * a).clip(0, 255).astype(np.uint8)
