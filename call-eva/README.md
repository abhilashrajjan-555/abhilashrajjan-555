# Call Eva promo video

30s animation in the Live Chat Agent video style: 16:9 (1920x1080) and 9:16 (1080x1920) for LinkedIn / Reels.

- `index.html`: the animation. `render(t)` draws the frame at `t` seconds.
- `vertical.html`: the 9:16 layout, same timings.
- `music_vertical.py`: chill-trap / lo-fi track (90 BPM) for the vertical cut.
- `render.js`: captures 900 frames with Playwright and encodes them with ffmpeg.
- `music.py`: generates the original upbeat music bed (124 BPM, synced to scene changes, no third-party audio).

```bash
node render.js silent.mp4
python3 music.py raw.wav
ffmpeg -i raw.wav -af loudnorm=I=-14:TP=-1:LRA=11 -ar 44100 music.wav
ffmpeg -i silent.mp4 -i music.wav -c:v copy -c:a aac -b:a 192k -shortest call-eva.mp4
```

Vertical:

```bash
node render.js --vertical vsilent.mp4
python3 music_vertical.py raw_v.wav
ffmpeg -i raw_v.wav -af loudnorm=I=-14:TP=-1:LRA=11 -ar 44100 music_v.wav
ffmpeg -i vsilent.mp4 -i music_v.wav -c:v copy -c:a aac -b:a 192k -shortest call-eva-vertical.mp4
```

Numbers come from one dealer group's dashboard, 1-10 Nov 2026 (dealer name removed).
