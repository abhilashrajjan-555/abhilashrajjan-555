"""Generates an original upbeat 30s music bed for the Call Eva promo (no third-party samples, so no licence issues).
124 BPM, C-G-Am-F, synced to the scene changes in index.html.
Usage: python3 music.py out.wav   (then loudness-normalise with ffmpeg loudnorm, see README)"""
import sys, wave
import numpy as np

SR, DUR, BPM = 44100, 30.0, 124
N = int(SR * DUR)
BEAT = 60 / BPM
OFF = 9.2 - round(9.2 / BEAT) * BEAT      # put a downbeat exactly on the 9.2s drop
rng = np.random.default_rng(11)

# scene marks (seconds), match index.html
LAND, MISSED, DROP, RESULTS, CLOSE, END_HIT = 2.2, 4.3, 9.2, 19.4, 25.5, 29.0

drums = np.zeros(N); music = np.zeros(N); fx = np.zeros(N)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def smooth(x, w):
    if w <= 1: return x
    c = np.cumsum(np.concatenate([[0], x])); y = (c[w:] - c[:-w]) / w
    return np.concatenate([np.full(w - 1, y[0]), y])
def add(buf, start, sig, gain=1.0):
    s = int(start * SR)
    if s >= N or s + len(sig) <= 0: return
    a = max(0, -s); e = min(len(sig), N - s)
    buf[s + a:s + e] += gain * sig[a:e]
def saw(f, n, detune=(0,)):
    tt = np.arange(n) / SR; out = np.zeros(n)
    for d in detune:
        ff = f * (1 + d / 100)
        for h in range(1, 9):
            if ff * h > 12000: break
            out += np.sin(2 * np.pi * ff * h * tt + d) / h
    return out / len(detune)
def beats(t0, t1, step=1.0):
    k0 = int(np.ceil((t0 - OFF) / (BEAT * step) - 1e-9))
    t = OFF + k0 * BEAT * step
    while t < t1 - 1e-9:
        yield t
        t += BEAT * step
def chord_at(t):
    bar = int(np.floor((t - OFF + 1e-6) / (4 * BEAT))) % 4
    return [[48, 52, 55], [43, 47, 50], [45, 48, 52], [41, 45, 48]][bar]  # C G Am F (roots + triad)

# ---- instruments ----
def kick():
    n = int(.4 * SR); tt = np.arange(n) / SR
    f = 48 + 110 * np.exp(-tt * 35)
    k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    k[:int(.003 * SR)] += rng.standard_normal(int(.003 * SR)) * .4
    return np.tanh(k * 2)
def clap():
    n = int(.25 * SR); tt = np.arange(n) / SR
    no = rng.standard_normal(n); no = no - smooth(no, 6); no = smooth(no, 2)
    e = np.exp(-tt * 18)
    for d in (0, .011, .022): e += np.exp(-np.clip(tt - d, 0, None) * 140) * (tt >= d)
    return no * e * .5
def hat(open_=False):
    n = int((.22 if open_ else .05) * SR); tt = np.arange(n) / SR
    no = np.diff(np.diff(rng.standard_normal(n + 2)))
    return no * np.exp(-tt * (14 if open_ else 70)) * .35
def bass(m, length):
    n = int(length * SR); tt = np.arange(n) / SR
    s = smooth(saw(midi(m), n), 18) + .6 * np.sin(2 * np.pi * midi(m) * tt)
    return s * np.minimum(1, tt / .004) * np.exp(-tt * 6) * (tt < length * .9)
def stab(notes, length):
    n = int(length * SR); tt = np.arange(n) / SR
    s = sum(saw(midi(m + 12), n, detune=(-12, 0, 12)) for m in notes)
    return smooth(s, 3) * np.minimum(1, tt / .003) * np.exp(-tt * 9) / len(notes)
def pluck(m):
    n = int(.25 * SR); tt = np.arange(n) / SR
    f = midi(m); s = np.sign(np.sin(2 * np.pi * f * tt)) * .4 + np.sin(2 * np.pi * f * tt)
    return smooth(s, 4) * np.exp(-tt * 16)
def riser(t0, t1, gain=.5):
    n = int((t1 - t0) * SR); p = np.linspace(0, 1, n)
    no = rng.standard_normal(n); hp = no - smooth(no, 30)
    sig = (1 - p) * smooth(no, 25) * 3 + p * hp
    tone = np.sin(2 * np.pi * np.cumsum(200 + 1400 * p ** 2) / SR) * .25
    add(fx, t0, (sig + tone) * p ** 2.2, gain)
def impact(t, gain=1.0):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-tt * 12)) / SR) * np.exp(-tt * 2.5)
    crash = (rng.standard_normal(n) - smooth(rng.standard_normal(n), 4)) * np.exp(-tt * 3) * .25
    add(fx, t, np.tanh(boom * 1.5) + crash, gain)
def whoosh(c):
    n = int(.8 * SR); no = smooth(rng.standard_normal(n), 30)
    add(fx, c - .55, no * np.sin(np.linspace(0, np.pi, n)) ** 2, .6)

# ---- arrangement ----
K = kick(); C = clap()
for t in beats(0, END_HIT):
    g = .55 if t < LAND else 1.0
    add(drums, t, K, g)
    beat_in_bar = int(round((t - OFF) / BEAT)) % 4
    if t >= LAND and beat_in_bar in (1, 3): add(drums, t, C, .8)
for t in beats(LAND, END_HIT, .5):
    if round((t - OFF) / (BEAT / 2)) % 2: add(drums, t, hat(True), .7)
for t in beats(DROP, END_HIT, .25): add(drums, t, hat(False), .5 if round((t - OFF) / (BEAT / 4)) % 2 else .3)
for t in beats(RESULTS, END_HIT, .25): add(drums, t, hat(False), .2)

# offbeat bass
for t in beats(0, END_HIT, .5):
    if not round((t - OFF) / (BEAT / 2)) % 2: continue
    g = 0 if t < LAND else (.45 if t < DROP else 1.0)
    if g: add(music, t, bass(chord_at(t)[0] - 12, BEAT / 2), .55 * g)
# stabs: 3-3-2 rhythm in 8ths
for t in beats(0, END_HIT, .5):
    pos = int(round((t - OFF) / (BEAT / 2))) % 8
    if pos in (0, 3, 6):
        g = .35 if t < DROP else 1.0
        add(music, t, stab(chord_at(t), BEAT * .6), .32 * g)
# 16th arp from the drop
for t in beats(DROP - 4 * BEAT, END_HIT, .25):
    i = int(round((t - OFF) / (BEAT / 4)))
    ch = chord_at(t); m = (ch + [ch[0] + 12])[[0, 1, 2, 3, 2, 1, 3, 2][i % 8]] + 24
    g = 1.0 if t >= DROP else .4
    add(music, t, pluck(m), .16 * g)
# intro pad
n = int(LAND * SR) + int(.6 * SR); tt = np.arange(n) / SR
pad = sum(saw(midi(m + 12), n, detune=(-10, 10)) for m in [48, 52, 55, 60])
add(music, 0, pad * np.minimum(1, tt / .8) * np.clip((LAND + .6 - tt) / .6, 0, 1), .07)

# intro low-pass sweep: blend from heavily smoothed to dry over the build
mw = smooth(music, 60); ramp = np.clip(np.arange(N) / SR / LAND, 0, 1) ** 2
music = mw * (1 - ramp) + music * ramp

# sidechain duck on every kick
duck = np.ones(N)
for t in beats(LAND, END_HIT):
    s = int(t * SR); n = min(int(.22 * SR), N - s)
    duck[s:s + n] = np.minimum(duck[s:s + n], .35 + .65 * (np.arange(n) / n) ** .6)
music *= duck

# fx
riser(.3, LAND, .45); impact(LAND, .8)
for c in (MISSED, DROP, RESULTS, CLOSE): whoosh(c)
riser(DROP - 1.9, DROP, .55); impact(DROP, 1.0)
riser(RESULTS - 1.0, RESULTS, .4); impact(RESULTS, .7)
riser(END_HIT - 1.4, END_HIT, .35)
# final hit: kick + stab + crash
impact(END_HIT, 1.0); add(music, END_HIT, stab([48, 52, 55, 60], 1.0), .5)

out = drums * .9 + music + fx * .8
fade = np.clip((DUR - np.arange(N) / SR) / .3, 0, 1)
out = np.tanh(out * 1.2) * fade
out /= np.max(np.abs(out)) / .9
pcm = (out * 32767).astype(np.int16)
stereo = np.stack([pcm, pcm], axis=1)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())
