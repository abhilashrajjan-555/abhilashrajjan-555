"""Generates an original 30s music bed for the Call Eva promo (no third-party samples, so no licence issues).
Usage: python3 music.py out.wav"""
import sys, wave
import numpy as np

SR, DUR, BPM = 44100, 30.0, 100
N = int(SR * DUR)
t = np.arange(N) / SR
beat = 60 / BPM
rng = np.random.default_rng(3)
out = np.zeros(N)

def note(m):
    return 440 * 2 ** ((m - 69) / 12)

def env(n, a, r):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    e[:ai] = np.linspace(0, 1, ai)
    e[-ri:] *= np.linspace(1, 0, ri)
    return e

# chord progression, 2 bars each (8 beats): C, Am, F, G
chords = [[48, 55, 60, 64, 67], [45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [43, 50, 55, 59, 62]]
bar2 = 8 * beat
# pad
for k in range(int(DUR / bar2) + 1):
    s = int(k * bar2 * SR); n = min(int(bar2 * SR) + int(.6 * SR), N - s)
    if n <= 0: break
    tt = np.arange(n) / SR
    sig = np.zeros(n)
    for m in chords[k % 4]:
        f = note(m)
        for d in (-0.12, 0.12):
            sig += np.sin(2 * np.pi * f * (1 + d / 100) * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)
    out[s:s + n] += 0.035 * sig * env(n, 0.8, 0.8)

# pluck arpeggio from 9s (Eva enters)
step = beat / 2
for i in range(int(9 / step), int(29 / step)):
    st = i * step; k = int(st / bar2) % 4
    ch = chords[k]; m = ch[[2, 3, 4, 3][i % 4]] + 12
    s = int(st * SR); n = min(int(0.5 * SR), N - s)
    tt = np.arange(n) / SR
    out[s:s + n] += 0.05 * np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * 9)

# kick + hats from 9s to 28s
for i in range(int(9 / beat), int(28 / beat)):
    s = int(i * beat * SR); n = min(int(0.35 * SR), N - s)
    tt = np.arange(n) / SR
    f = 50 + 70 * np.exp(-tt * 30)
    out[s:s + n] += 0.22 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
    hs = int((i * beat + beat / 2) * SR); hn = min(int(0.06 * SR), N - hs)
    if hn > 0:
        h = rng.standard_normal(hn); h = np.diff(np.concatenate([[0], h]))
        out[hs:hs + hn] += 0.03 * h * np.exp(-np.arange(hn) / SR * 60)

# whooshes into each scene change
for c in (4.3, 9.2, 19.4, 25.5):
    s = int((c - 0.6) * SR); n = int(0.9 * SR)
    noise = rng.standard_normal(n)
    sm = np.convolve(noise, np.ones(40) / 40, mode='same')
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    out[s:s + n] += 0.25 * sm * e

# low sub swell at the hook number
s = int(0.2 * SR); n = int(2.2 * SR); tt = np.arange(n) / SR
out[s:s + n] += 0.12 * np.sin(2 * np.pi * 65.4 * tt) * env(n, 1.2, 0.9)

out *= env(N, 0.4, 1.5)
out = np.tanh(out * 1.6)
out /= np.max(np.abs(out)) / 0.8
pcm = (out * 32767).astype(np.int16)
stereo = np.repeat(pcm[:, None], 2, axis=1)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())
