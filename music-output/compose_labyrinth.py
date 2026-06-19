#!/usr/bin/env python3
"""
"Candlelight in the Dead Labyrinth" — dark ambient, loopable.
music21 -> MIDI -> FluidSynth (FluidR3_GM) -> cavernous convolution reverb
+ lo-fi warmth (scipy) -> wav/mp3.
"""
import os, random
import numpy as np
from music21 import stream, note, chord, tempo, meter
from mido import MidiFile, Message
from midi2audio import FluidSynth
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile
from pydub import AudioSegment

random.seed(7)
OUT = "/home/user/cmu2/music-output"
os.makedirs(OUT, exist_ok=True)
SF = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
BPM = 52
TOTAL = 128          # beats (32 bars of 4/4) -> seamless loop on the tonic
SR = 44100

# ----------------------------------------------------------------------------
# 1) COMPOSE
# ----------------------------------------------------------------------------
score = stream.Score()
sub      = stream.Part()   # track 1  sub-bass drone   (prog 89)
lowpad   = stream.Part()   # track 2  cold bowed pad   (prog 92)
halo     = stream.Part()   # track 3  dissonant shimmer(prog 94)
choir    = stream.Part()   # track 4  ghostly aahs     (prog 52)
celesta  = stream.Part()   # track 5  fragile lead     (prog 8)
musicbox = stream.Part()   # track 6  rare high glints (prog 10)
heart    = stream.Part()   # track 7  heartbeat        (prog 47 timpani)

sub.insert(0, tempo.MetronomeMark(number=BPM))
sub.insert(0, meter.TimeSignature('4/4'))

# Harmony: i - VI - iv - i  (Am - F - Dm - Am), 8 bars (32 beats) each.
sections = [
    (0,   ['A2', 'C3', 'E3'], 'A1', ['E4', 'A4'], 'B-4'),   # Am  (+b9 shimmer)
    (32,  ['F2', 'A2', 'C3'], 'F1', ['A4', 'C5'], 'E5'),    # F   (maj7 shimmer)
    (64,  ['D2', 'F2', 'A2'], 'D1', ['A4', 'D5'], 'E-5'),   # Dm  (tritone-ish)
    (96,  ['A2', 'C3', 'E3'], 'A1', ['E4', 'A4'], 'B-4'),   # Am  -> loops home
]

for off, triad, subroot, halo_dyad, shimmer in sections:
    # cold sustained pad (whole 32-beat block, each voice one long tone)
    for p in triad:
        lowpad.insert(off, note.Note(p, quarterLength=32.0))
    # faint sub-bass drone
    sub.insert(off, note.Note(subroot, quarterLength=32.0))
    # high halo: consonant dyad + barely-there dissonant shimmer
    for p in halo_dyad:
        halo.insert(off, note.Note(p, quarterLength=32.0))
    halo.insert(off + 4, note.Note(shimmer, quarterLength=24.0))  # shimmer

# Ghostly wordless choir: slow swells, enters after the intro, taper before loop
choir_events = [
    (18, 'E4', 12), (30, 'A4', 16),
    (48, 'C5', 14), (64, 'F4', 18), (82, 'A4', 12),
    (96, 'E4', 14), (110, 'C5', 9),
]
for o, p, d in choir_events:
    choir.insert(float(o), note.Note(p, quarterLength=float(d)))

# Fragile celesta lead — sparse, hesitant, childlike-but-eerie fragments.
# A natural minor with Phrygian b2 (Bb) colour. Long silences between motifs.
motifs = [
    ['A4', 'C5', 'B4'],
    ['E5', 'D5', 'C5'],
    ['A4', 'B-4', 'A4'],
    ['C5', 'B4', 'A4', 'E4'],
    ['E5', 'A4'],
    ['D5', 'C5', 'E5'],
    ['A4', 'C5', 'E5', 'D5'],
]
pos = 9.0
mi = 0
while pos < 116 and mi < 40:
    motif = motifs[mi % len(motifs)]
    mi += 1
    for p in motif:
        dur = random.choice([1.0, 1.0, 1.5, 2.0])
        n = note.Note(p, quarterLength=dur)
        n.volume.velocity = random.randint(60, 78)   # soft, present
        celesta.insert(round(pos, 2), n)
        pos += dur + random.choice([0.0, 0.5, 1.0])   # hesitant micro-gaps
    pos += random.choice([5, 7, 9, 11, 13])           # long silence between

# Music box: very rare single high glints echoing the lead
for o, p in [(40, 'A5'), (76, 'E5'), (104, 'C6')]:
    n = note.Note(p, quarterLength=2.0); n.volume.velocity = 50
    musicbox.insert(float(o), n)

# Distant heartbeat (lub-dub), continuous so the loop boundary stays smooth
t = 2.0
while t < TOTAL - 1:
    lub = note.Note('A1', quarterLength=0.4); lub.volume.velocity = 34
    dub = note.Note('E1', quarterLength=0.4); dub.volume.velocity = 27
    heart.insert(round(t, 2), lub)
    heart.insert(round(t + 0.45, 2), dub)
    t += 4.0   # ~one beat-pair per bar -> slow, subliminal

for part in [sub, lowpad, halo, choir, celesta, musicbox, heart]:
    score.append(part)

mid_path = os.path.join(OUT, "labyrinth_candlelight.mid")
score.write('midi', fp=mid_path)
print("MIDI written")

# ----------------------------------------------------------------------------
# 2) ASSIGN GM PROGRAMS + VELOCITIES (mido)
# ----------------------------------------------------------------------------
PROG = {1: 89, 2: 92, 3: 94, 4: 52, 5: 8, 6: 10, 7: 47}   # track -> GM program
VEL  = {1: 48, 2: 50, 3: 26, 4: 42, 5: None, 6: None, 7: None}  # None = keep per-note

def insert_program(track, program):
    pos = 0
    for j, msg in enumerate(track):
        if msg.type == 'track_name':
            pos = j + 1; break
    track.insert(pos, Message('program_change', program=program, time=0))

mid = MidiFile(mid_path)
for i, track in enumerate(mid.tracks):
    if i in PROG:
        insert_program(track, PROG[i])
        if VEL[i] is not None:
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    msg.velocity = VEL[i]
mid.save(mid_path)
print("Instruments + mix set")

# ----------------------------------------------------------------------------
# 3) RENDER (FluidSynth) -> raw wav
# ----------------------------------------------------------------------------
raw_wav = os.path.join(OUT, "_raw.wav")
FluidSynth(SF, sample_rate=SR).midi_to_audio(mid_path, raw_wav)
print("FluidSynth rendered")

# ----------------------------------------------------------------------------
# 4) POST: cavernous reverb + lo-fi warmth (scipy)
# ----------------------------------------------------------------------------
sr, data = wavfile.read(raw_wav)
if data.dtype == np.int16:
    x = data.astype(np.float32) / 32768.0
else:
    x = data.astype(np.float32)
    x /= (np.max(np.abs(x)) or 1.0)
if x.ndim == 1:
    x = np.stack([x, x], axis=1)

def make_ir(seconds, decay, predelay_ms, seed):
    rng = np.random.default_rng(seed)
    n = int(seconds * sr)
    env = np.exp(-np.linspace(0, 1, n) / decay)
    ir = rng.standard_normal(n) * env
    # smooth, dark tail (reverb is not bright)
    sos = butter(2, 3500, 'low', fs=sr, output='sos')
    ir = sosfilt(sos, ir)
    pre = np.zeros(int(predelay_ms / 1000 * sr))
    ir = np.concatenate([pre, ir])
    return (ir / (np.max(np.abs(ir)) or 1.0)).astype(np.float32)

# decorrelated L/R impulses -> wide, cavernous space (full tail kept)
irL = make_ir(3.8, 0.42, 28, 1)
irR = make_ir(4.0, 0.45, 41, 2)
N = len(x)
wetL = fftconvolve(x[:, 0], irL)
wetR = fftconvolve(x[:, 1], irR)
L = max(len(wetL), len(wetR))
wet = np.zeros((L, 2), dtype=np.float32)
wet[:len(wetL), 0] = wetL
wet[:len(wetR), 1] = wetR
wet /= (np.max(np.abs(wet)) or 1.0)

WET = 0.55
x_pad = np.zeros((L, 2), dtype=np.float32)
x_pad[:N] = x
y_full = (1.0 - WET) * x_pad + WET * wet

# --- make it a SEAMLESS LOOP ---
# Fix length to the exact musical grid, then wrap everything that spills past
# the loop point (note releases + reverb tail) back onto the start.
loop_N = int(round(TOTAL * 60.0 / BPM * sr))
y = y_full[:loop_N].copy()
tail = y_full[loop_N:]
M = min(len(tail), loop_N)
y[:M] += tail[:M]

# lo-fi warmth: gentle high cut + sub-rumble clean-up
sos_lp = butter(4, 6500, 'low', fs=sr, output='sos')
sos_hp = butter(2, 28, 'high', fs=sr, output='sos')
y = sosfilt(sos_lp, y, axis=0)
y = sosfilt(sos_hp, y, axis=0)

# leave headroom (brief asks for lots of headroom): peak ~ -3.5 dBFS
peak = np.max(np.abs(y)) or 1.0
y = y / peak * (10 ** (-3.5 / 20))

out16 = (np.clip(y, -1, 1) * 32767).astype(np.int16)
proc_wav = os.path.join(OUT, "labyrinth_candlelight.wav")
wavfile.write(proc_wav, sr, out16)
print("Post-processing done")

# ----------------------------------------------------------------------------
# 5) MP3
# ----------------------------------------------------------------------------
mp3_path = os.path.join(OUT, "labyrinth_candlelight.mp3")
seg = AudioSegment.from_wav(proc_wav)
seg.export(mp3_path, format='mp3', bitrate='192k')
print("MP3 exported")

os.remove(raw_wav)
dur_s = len(seg) / 1000.0
print(f"DONE  duration={dur_s:.1f}s  dBFS={seg.dBFS:.1f}  max={seg.max_dBFS:.1f}")
