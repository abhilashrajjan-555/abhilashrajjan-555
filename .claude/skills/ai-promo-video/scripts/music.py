"""Generates an original 30s music bed synced to the template's scene timings (no third-party audio).
Usage: python3 music.py --style upbeat|lofi out.wav
  upbeat: 124 BPM dance-pop (used for the 16:9 Call Eva video)
  lofi:   90 BPM chill trap / lo-fi (used for the 9:16 LinkedIn / Reels cut)"""
import sys, runpy, os
args = sys.argv[1:]
style = 'upbeat'
if '--style' in args:
    i = args.index('--style'); style = args[i + 1]; del args[i:i + 2]
if style not in ('upbeat', 'lofi'):
    sys.exit(f'unknown style {style!r}: use upbeat or lofi')
sys.argv = [sys.argv[0]] + args
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'music_{style}.py'), run_name='__main__')
