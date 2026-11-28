"""Frame renderer. usage: python render.py START END OUT.mp4   (frames [START, END))
or: python render.py --still FRAME out.png"""
import sys, os, math, subprocess, time
import numpy as np, cv2
from core import *
import scenes, captions, post

INFO = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)

# transitions at cuts: whip = horizontal motion blur across the cut, wipe = dark foreground sweep
B = bar_t
WHIPS = [B(7), B(15), B(27), B(29), B(31), bar_t(32, 8)]
WIPES = [(B(11), 1), (B(23), -1), (B(19), 1), (B(13), -1)]


def render_scene(t, frame):
    surf = skia.Surface.MakeRaster(INFO)
    c = surf.getCanvas()
    c.clear(hexc('#0b0d1c'))
    i, fn = scenes.shot_at(t)
    fx = fn(c, t, frame) or {}
    img = surf.makeImageSnapshot().toarray()
    return img, fx


def render_frame(frame):
    t = frame / FPS
    img, fx = render_scene(t, frame)
    rgb = post.grade(img, frame, flash=fx.get('flash', 0.0))
    if fx.get('dim'):
        rgb = (rgb.astype(np.float32) * (1 - fx['dim'])).astype(np.uint8)
    # whip pans
    for tw in WHIPS:
        d = abs(t - tw)
        if d < 0.1:
            k = int(1 + 90 * (1 - d / 0.1) ** 2)
            rgb = cv2.blur(rgb, (k, 1))
    # loop closure: crossfade the final knocks into the opening frame composition
    if t > 59.62:
        a = smooth(ramp(t, 59.62, 60.0))
        img0, fx0 = render_scene(0.0, 0)
        rgb0 = post.grade(img0, 0, flash=0)
        rgb = (rgb.astype(np.float32) * (1 - a) + rgb0.astype(np.float32) * a).astype(np.uint8)
    # overlay layer: wipes + captions (crisp, ungraded)
    ov = skia.Surface.MakeRaster(INFO)
    oc = ov.getCanvas()
    oc.clear(skia.ColorTRANSPARENT)
    for tw, dirn in WIPES:
        d = (t - tw) / 0.22
        if -1 < d < 1:
            x = W / 2 + dirn * d * (W * 0.9)
            pth = smooth_poly([(x - 260, -50), (x + 200, -50), (x + 300, H + 50), (x - 160, H + 50)], True, 0.2)
            oc.drawPath(pth, fill('#07060c'))
            oc.drawPath(pth, stroke('#2a2238', 10))
    if fx.get('knock'):
        oc.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), fill('#000000', 0.25 * clamp(fx['knock'])))
    captions.draw(oc, t)
    ova = ov.makeImageSnapshot().toarray()
    return post.over(rgb, ova)


def main():
    if sys.argv[1] == '--still':
        for fr in sys.argv[2].split(','):
            fr = int(fr)
            out = render_frame(fr)
            p = sys.argv[3].replace('#', '%04d' % fr)
            cv2.imwrite(p, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        return
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    crf = os.environ.get('CRF', '14')
    preset = os.environ.get('PRESET', 'slow')
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', preset, '-crf', crf, '-pix_fmt', 'yuv420p',
           '-x264-params', 'keyint=60:min-keyint=60', out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fr in range(a, b):
        pr.stdin.write(render_frame(fr).tobytes())
        if (fr - a) % 60 == 0:
            print('frame', fr, '%.2fs/f' % ((time.time() - t0) / (fr - a + 1)), flush=True)
    pr.stdin.close()
    pr.wait()


if __name__ == '__main__':
    main()
