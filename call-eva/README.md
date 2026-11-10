# Call Eva promo video

30s, 1920x1080 animation in the Live Chat Agent video style.

- `index.html`: the animation. `render(t)` draws the frame at `t` seconds.
- `render.js`: captures 900 frames with Playwright and encodes them with ffmpeg.
- `music.py`: generates the original music bed (no third-party audio).

```bash
node render.js silent.mp4
python3 music.py music.wav
ffmpeg -i silent.mp4 -i music.wav -c:v copy -c:a aac -b:a 192k -shortest call-eva.mp4
```

Numbers come from one dealer group's dashboard, 1-10 Nov 2026 (dealer name removed).
