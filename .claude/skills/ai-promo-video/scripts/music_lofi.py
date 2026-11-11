"""Original chill-trap / lo-fi beat for the 9:16 Call Eva cut (LinkedIn / Reels). No third-party samples.
90 BPM, Am7-Fmaj7-Cmaj7-G, synced to the same scene changes as the 16:9 video.
Usage: python3 music_vertical.py raw.wav   (then loudness-normalise with ffmpeg loudnorm, see README)"""
import sys, wave
import numpy as np

SR, DUR, BPM = 44100, 30.0, 90
N = int(SR * DUR)
BEAT = 60 / BPM
BAR = 4 * BEAT
OFF = 9.2 - round(9.2 / BEAT) * BEAT          # downbeat lands on the 9.2s drop
rng = np.random.default_rng(21)
LAND, MISSED, DROP, RESULTS, CLOSE, END_HIT = 2.2, 4.3, 9.2, 19.4, 25.5, 29.0

drums = np.zeros(N); keys = np.zeros(N); low = np.zeros(N); fx = np.zeros(N)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def smooth(x, w):
    if w <= 1: return x
    c = np.cumsum(np.concatenate([[0], x])); y = (c[w:] - c[:-w]) / w
    return np.concatenate([np.full(w - 1, y[0]), y])
def add(buf, start, sig, gain=1.0):
    s = int(round(start * SR))
    if s >= N or s + len(sig) <= 0: return
    a = max(0, -s); e = min(len(sig), N - s)
    buf[s + a:s + e] += gain * sig[a:e]
def grid(t0, t1, step):
    k = int(np.ceil((t0 - OFF) / (BEAT * step) - 1e-9)); t = OFF + k * BEAT * step
    while t < t1 - 1e-9:
        yield t, k
        k += 1; t = OFF + k * BEAT * step
CHORDS = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]   # Am7 Fmaj7 Cmaj7 G7
ROOTS = [33, 29, 36, 31]
def bar_idx(t): return int(np.floor((t - OFF + 1e-6) / BAR)) % 4

# ---- instruments ----
def epiano(m, length):
    n = int(length * SR); tt = np.arange(n) / SR; f = midi(m)
    idx = 1.6 * np.exp(-tt * 3)
    s = np.sin(2 * np.pi * f * tt + idx * np.sin(2 * np.pi * f * tt))
    s += .25 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 5)
    trem = 1 + .12 * np.sin(2 * np.pi * 4.5 * tt)
    return s * trem * np.minimum(1, tt / .01) * np.exp(-tt * .9) * np.clip((length - tt) / .15, 0, 1)
def kick():
    n = int(.25 * SR); tt = np.arange(n) / SR
    return np.tanh(2 * np.sin(2 * np.pi * np.cumsum(55 + 120 * np.exp(-tt * 45)) / SR) * np.exp(-tt * 16))
def b808(m, length, glide_from=None):
    n = int(length * SR); tt = np.arange(n) / SR; f = midi(m)
    if glide_from is not None: f = midi(m) + (midi(glide_from) - midi(m)) * np.exp(-tt * 25)
    s = np.sin(2 * np.pi * np.cumsum(np.full(n, f) if np.isscalar(f) else f) / SR)
    return np.tanh(1.8 * s) * np.minimum(1, tt / .003) * np.exp(-tt * 1.3) * np.clip((length - tt) / .05, 0, 1)
def snare():
    n = int(.3 * SR); tt = np.arange(n) / SR
    no = rng.standard_normal(n); no = no - smooth(no, 5)
    body = np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30)
    return (no * np.exp(-tt * 16) * .6 + body * .5)
def hat(dec=80, g=1.0):
    n = int(.08 * SR); tt = np.arange(n) / SR
    return np.diff(np.diff(rng.standard_normal(n + 2))) * np.exp(-tt * dec) * .25 * g
def rim():
    n = int(.06 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1700 * tt) + .5 * rng.standard_normal(n)) * np.exp(-tt * 90) * .3
def bell(m):
    n = int(.9 * SR); tt = np.arange(n) / SR; f = midi(m)
    return (np.sin(2 * np.pi * f * tt + 2 * np.exp(-tt * 6) * np.sin(2 * np.pi * 3.5 * f * tt))) * np.exp(-tt * 4)
def riser(t0, t1, g):
    n = int((t1 - t0) * SR); p = np.linspace(0, 1, n); no = rng.standard_normal(n)
    add(fx, t0, ((1 - p) * smooth(no, 20) * 3 + p * (no - smooth(no, 25))) * p ** 2.4, g)
def impact(t, g):
    n = int(1.8 * SR); tt = np.arange(n) / SR
    boom = np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(38 + 80 * np.exp(-tt * 10)) / SR) * np.exp(-tt * 2))
    add(fx, t, boom + (rng.standard_normal(n) - smooth(rng.standard_normal(n), 5)) * np.exp(-tt * 3.5) * .2, g)
def whoosh(c):
    n = int(.8 * SR); add(fx, c - .55, smooth(rng.standard_normal(n), 30) * np.sin(np.linspace(0, np.pi, n)) ** 2, .5)

# ---- arrangement ----
# electric piano chords, slight strum, whole track
for t, k in grid(-BAR, END_HIT, 4):
    ch = CHORDS[bar_idx(t + .01)]
    for j, m in enumerate(ch): add(keys, t + j * .018, epiano(m, BAR + .1), .16)
add(keys, END_HIT, sum(epiano(m, 1.0) for m in CHORDS[0]), .18)
# bell melody for the lift (results + close)
mel = [76, 74, 72, 74, 76, 79, 76, 72]
for i, (t, k) in enumerate(grid(RESULTS, END_HIT, 1)):
    if k % 2 == 0: add(keys, t, bell(mel[(k // 2) % len(mel)]), .07)

# hats: light 8ths from 2.2, 8ths + triplet rolls after the drop
for t, k in grid(LAND, END_HIT, .5):
    g = .5 if t < MISSED else (.8 if t < DROP else 1.0)
    add(drums, t, hat(80, g), 1)
for t, k in grid(DROP, END_HIT, .25):
    if k % 2: add(drums, t, hat(120, .45), 1)
def roll(t_end, beats=1.0, step=1 / 6):
    for t, k in grid(t_end - beats * BEAT, t_end, step):
        add(drums, t, hat(140, .5 + .5 * (t - (t_end - beats * BEAT)) / (beats * BEAT)), 1)
for c in (DROP, RESULTS, CLOSE): roll(c, 1.0, 1 / 8)
for t, k in grid(DROP, END_HIT - BAR, 8): roll(t + 2 * BAR, .5, 1 / 6)

# snare (half-time, beat 3) from "MISSED", rims before that
for t, k in grid(LAND, END_HIT, 1):
    pos = k % 4
    if t < MISSED:
        if pos == 2: add(drums, t, rim(), 1)
    elif pos == 2: add(drums, t, snare(), .7 if t < DROP else 1.0)

# kick + 808 from the drop; 808 pattern per bar in 8ths
PAT = [(0, 3), (3, 2), (6, 1), (7, 1)]
for t, k in grid(DROP, END_HIT, 4):
    r = ROOTS[bar_idx(t + .01)]
    for pos, ln in PAT:
        st = t + pos * BEAT / 2
        if st >= END_HIT: break
        glide = r + 12 if pos == 7 else None
        add(low, st, b808(r + (12 if pos == 7 else 0), ln * BEAT / 2 + .05, glide_from=None if pos != 6 else r + 7), .5)
        if pos in (0, 3): add(drums, st, kick(), .8)
# tension pulse under "MISSED": soft 808 every 2 beats
for t, k in grid(MISSED - 2 * BEAT, DROP, 2): add(low, t, b808(ROOTS[bar_idx(t + .01)], BEAT * 1.5), .3)

# fx
riser(.2, LAND, .4); impact(LAND, .7)
for c in (MISSED, DROP, RESULTS, CLOSE): whoosh(c)
riser(DROP - 2.0, DROP, .45); impact(DROP, .9)
impact(RESULTS, .5); impact(END_HIT, .9)

# filtering: dark intro + "MISSED" section, opens at the drop
t_axis = np.arange(N) / SR
open_amt = np.clip(t_axis / LAND, 0, 1) * .6
open_amt = np.where(t_axis >= LAND, .55, open_amt)
open_amt = np.where(t_axis >= DROP, 1.0, open_amt)
open_amt = np.where((t_axis > DROP - 1.5) & (t_axis < DROP), .55 + .45 * (t_axis - (DROP - 1.5)) / 1.5, open_amt)
keys = smooth(keys, 40) * (1 - open_amt) + keys * open_amt

# sidechain keys under the kick/808 hits
duck = np.ones(N)
for t, k in grid(DROP, END_HIT, .5):
    if (k % 8) in (0, 3, 6, 7):
        s = int(t * SR); n = min(int(.18 * SR), N - s)
        duck[s:s + n] = np.minimum(duck[s:s + n], .5 + .5 * np.arange(n) / n)
keys *= duck

# vinyl texture: low hiss + sparse crackle
hiss = smooth(rng.standard_normal(N), 12) * .012
crackle = np.zeros(N); idx = rng.integers(0, N, 900); crackle[idx] = rng.standard_normal(900) * .25
vinyl = hiss + smooth(crackle, 2)

out = drums * .85 + keys + low + fx * .7 + vinyl
fade = np.clip((DUR - t_axis) / .4, 0, 1)
out = np.tanh(out * 1.3) * fade
out /= np.max(np.abs(out)) / .9
pcm = (out * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music_vertical.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.stack([pcm, pcm], 1).tobytes())
