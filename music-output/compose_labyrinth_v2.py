#!/usr/bin/env python3
"""
"Candlelight in the Dead Labyrinth — Dust Mix" v2
Dark ambient grown into dusty trip-hop / lo-fi:
  - dusty, swung, humanized drums (+ vinyl crackle, tape wow/flutter, saturation)
  - voices: choir swells + chopped vocal stabs
  - broken melodies: syncopated, off-grid fragments with stutter glitches
  - jazzy-dark Rhodes chords over a cavernous pad/sub foundation
music21 -> MIDI -> FluidSynth (FluidR3_GM) -> scipy post -> wav/mp3.  Seamless loop.
"""
import os, random
import numpy as np
from music21 import stream, note, chord, tempo, meter
from mido import MidiFile, Message
from midi2audio import FluidSynth
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile
from pydub import AudioSegment

random.seed(11)
rng = np.random.default_rng(11)
OUT = "/home/user/cmu2/music-output"
SF  = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
BPM = 80
BARS = 32
BPBAR = 4
TOTAL = BARS * BPBAR          # 128 beats -> 96 s loop
SR = 44100

def hum(t, amt=0.04):
    """humanize an offset (in beats) by +/- a little, dusty/loose feel."""
    return round(max(0.0, t + random.uniform(-amt, amt)), 3)

def mknote(midi_num, vel):
    """drum hit: a music21 note by MIDI number with a set velocity."""
    n = note.Note(midi_num, quarterLength=0.25)
    n.volume.velocity = vel
    return n

# ----------------------------------------------------------------------------
# 1) COMPOSE
# ----------------------------------------------------------------------------
score = stream.Score()
drums   = stream.Part()   # tr1  channel 9
sub     = stream.Part()   # tr2  prog 89 sub drone
pad     = stream.Part()   # tr3  prog 92 cold pad (root+5th)
rhodes  = stream.Part()   # tr4  prog 4  e-piano jazzy-dark chords
bass    = stream.Part()   # tr5  prog 32 upright-ish bass (broken)
choir   = stream.Part()   # tr6  prog 52 choir aahs (swells)
vox     = stream.Part()   # tr7  prog 53 voice oohs (chops)
lead    = stream.Part()   # tr8  prog 8  celesta broken melody
glints  = stream.Part()   # tr9  prog 11 vibraphone accents

sub.insert(0, tempo.MetronomeMark(number=BPM))
sub.insert(0, meter.TimeSignature('4/4'))

# Harmony: Am9 - Dm9 - Fmaj7(9) - E7b9  (8 bars each) -> dark, resolves & loops
SECTIONS = [
    dict(off=0,  root='A1',
         rhodes=['A2','C3','E3','G3','B3'],
         pad=['A2','E3'], shimmer='B4'),
    dict(off=32, root='D2',
         rhodes=['D3','F3','A3','C4','E4'],
         pad=['D2','A2'], shimmer='E5'),
    dict(off=64, root='F1',
         rhodes=['F2','A2','C3','E3','G3'],
         pad=['F2','C3'], shimmer='E5'),
    dict(off=96, root='E2',
         rhodes=['E3','G#3','B3','D4','F4'],   # E7b9 tension
         pad=['E2','B2'], shimmer='F5'),
]

# --- drones / pads / sub (continuous => seamless) ---
for s in SECTIONS:
    sub.insert(s['off'], note.Note(s['root'], quarterLength=32.0))
    for p in s['pad']:
        pad.insert(s['off'], note.Note(p, quarterLength=32.0))

# --- Rhodes: broken, syncopated chord stabs (not sustained) ---
# per-bar rhythm (beat offsets, duration) — swung, leaves space
rh_rhythm = [(0.0, 1.5), (1.75, 0.5), (2.5, 0.5), (3.5, 0.5)]
for s in SECTIONS:
    for bar in range(8):
        base = s['off'] + bar * 4
        # drop some stabs for a broken feel
        for k, (bt, d) in enumerate(rh_rhythm):
            if random.random() < 0.2:        # occasional dropout
                continue
            c = chord.Chord(s['rhodes'], quarterLength=d)
            c.volume.velocity = random.randint(48, 70)
            rhodes.insert(hum(base + bt), c)

# --- Bass: broken, syncopated, octave 1-2 (root / fifth / octave) ---
def shift(pitch, semis):
    n = note.Note(pitch); n.pitch.midi += semis; return n.nameWithOctave
for s in SECTIONS:
    r = s['root']
    fifth = shift(r, 7)
    octv  = shift(r, 12)
    bass_fig = [(0.0, r, 1.0), (1.5, octv, 0.25), (2.0, fifth, 0.5),
                (2.75, r, 0.25), (3.5, fifth, 0.25)]
    for bar in range(8):
        base = s['off'] + bar * 4
        for bt, p, d in bass_fig:
            if random.random() < 0.15:
                continue
            n = note.Note(p, quarterLength=d)
            n.volume.velocity = random.randint(72, 90)
            bass.insert(hum(base + bt), n)

# --- DUSTY DRUMS (channel 9), swung 16ths, humanized, ghost notes ---
SWING = 0.06   # delay on off-16ths (in beats)
for bar in range(BARS):
    base = bar * 4
    # kick: beat 1 + syncopated "and of 2" + ghost on "a of 3"
    drums.insert(hum(base + 0.0, .02), mknote(36, 96))
    if random.random() < 0.85:
        drums.insert(hum(base + 1.5, .03), mknote(36, 70))
    if random.random() < 0.4:
        drums.insert(hum(base + 2.75, .03), mknote(36, 55))
    # snare backbeat (beats 2 & 4) + occasional ghost snares
    drums.insert(hum(base + 1.0, .02), mknote(38, 86))
    drums.insert(hum(base + 3.0, .02), mknote(38, 88))
    if random.random() < 0.3:
        drums.insert(hum(base + 2.5, .03), mknote(38, 40))   # ghost
    if random.random() < 0.25:
        drums.insert(hum(base + 3.75, .03), mknote(37, 45))  # side-stick
    # hats: swung 16ths with ghost-note dynamics, random dropouts
    for i in range(8):
        t = base + i * 0.5
        if i % 2 == 1:
            t += SWING
        if random.random() < 0.12:
            continue
        v = random.choice([26, 30, 34, 60])     # mostly ghost, occasional accent
        nt = 46 if (i == 5 and random.random() < 0.3) else 42  # rare open hat
        drums.insert(hum(t, .02), mknote(nt, v))
    # end-of-8-bars dusty fill (stutter snare roll)
    if bar % 8 == 7:
        for j in range(4):
            drums.insert(hum(base + 3.0 + j * 0.25, .015),
                         mknote(38, 40 + j * 14))

# --- VOICES: choir swells (atmos) + chopped vocal stabs (rhythmic) ---
for o, p, d in [(16,'E4',12),(32,'A4',16),(64,'F4',18),(96,'B3',14),(110,'E4',10)]:
    choir.insert(float(o), note.Note(p, quarterLength=float(d)))
# vocal chops: short, syncopated, follow chord tones, with stutters
for s in SECTIONS:
    tones = [t for t in s['rhodes'] if note.Note(t).pitch.midi >= note.Note('A3').pitch.midi]
    if not tones:
        tones = s['rhodes'][-2:]
    for bar in range(8):
        base = s['off'] + bar * 4
        if random.random() < 0.55:
            p = random.choice(tones)
            bt = random.choice([0.5, 1.5, 2.5, 3.5])
            if random.random() < 0.35:        # stutter chop
                for j in range(random.choice([2, 3])):
                    nn = note.Note(p, quarterLength=0.2)
                    nn.volume.velocity = random.randint(45, 62)
                    vox.insert(hum(base + bt + j * 0.25, .01), nn)
            else:
                nn = note.Note(p, quarterLength=random.choice([0.4, 0.6]))
                nn.volume.velocity = random.randint(45, 64)
                vox.insert(hum(base + bt), nn)

# --- BROKEN MELODY: celesta fragments, off-grid, with stutter glitches ---
SCALE = {  # dark scale per section (natural minor / Phrygian colour)
    0: ['A4','B4','C5','D5','E5','F5','G5'],
    1: ['D4','E4','F4','G4','A4','B-4','C5'],
    2: ['F4','G4','A4','C5','E5','D5'],
    3: ['E4','F4','G#4','B4','D5','C5'],
}
for si, s in enumerate(SECTIONS):
    notes_pool = SCALE[si]
    pos = s['off'] + random.choice([1.0, 2.0, 3.0])
    while pos < s['off'] + 30:
        if random.random() < 0.30:            # stutter glitch (broken)
            p = random.choice(notes_pool)
            reps = random.choice([3, 4, 5])
            for j in range(reps):
                nn = note.Note(p, quarterLength=0.25)
                nn.volume.velocity = random.randint(55, 78)
                lead.insert(hum(pos + j * 0.25, .01), nn)
            pos += reps * 0.25 + random.choice([1.5, 2.5, 3.5])
        else:                                 # short broken phrase
            n_notes = random.choice([2, 3, 4])
            for _ in range(n_notes):
                p = random.choice(notes_pool)
                d = random.choice([0.25, 0.5, 0.5, 0.75])
                nn = note.Note(p, quarterLength=d)
                nn.volume.velocity = random.randint(58, 80)
                lead.insert(hum(pos, .02), nn)
                pos += d + random.choice([0.0, 0.25, 0.5])
            pos += random.choice([2.0, 3.0, 4.0, 5.0])

# --- vibraphone glints (sparse high accents) ---
for o, p in [(20,'A5'),(52,'D5'),(80,'C6'),(112,'E5')]:
    nn = note.Note(p, quarterLength=2.0); nn.volume.velocity = 52
    glints.insert(float(o), nn)

for part in [drums, sub, pad, rhodes, bass, choir, vox, lead, glints]:
    score.insert(0, part)   # parallel placement (append would stack sequentially)

mid_path = os.path.join(OUT, "labyrinth_dustmix.mid")
score.write('midi', fp=mid_path)
print("MIDI written")

# ----------------------------------------------------------------------------
# 2) GM PROGRAMS + CHANNELS (mido)
# ----------------------------------------------------------------------------
PROG = {2: 89, 3: 92, 4: 4, 5: 32, 6: 52, 7: 53, 8: 8, 9: 11}  # track->program

def insert_program(track, program):
    pos = 0
    for j, msg in enumerate(track):
        if msg.type == 'track_name':
            pos = j + 1; break
    track.insert(pos, Message('program_change', program=program, time=0))

mid = MidiFile(mid_path)
for i, track in enumerate(mid.tracks):
    if i == 1:                       # drums -> channel 9
        for msg in track:
            if hasattr(msg, 'channel'):
                msg.channel = 9
    elif i in PROG:
        insert_program(track, PROG[i])
mid.save(mid_path)
print("Instruments + channels set")

# ----------------------------------------------------------------------------
# 3) RENDER
# ----------------------------------------------------------------------------
raw_wav = os.path.join(OUT, "_raw2.wav")
FluidSynth(SF, sample_rate=SR).midi_to_audio(mid_path, raw_wav)
print("FluidSynth rendered")

sr, data = wavfile.read(raw_wav)
x = (data.astype(np.float32) / 32768.0) if data.dtype == np.int16 else data.astype(np.float32)
if x.ndim == 1:
    x = np.stack([x, x], axis=1)
N = len(x)

# ----------------------------------------------------------------------------
# 4) TAPE WOW/FLUTTER (dusty pitch wobble) — periodic over the loop
# ----------------------------------------------------------------------------
loop_N = int(round(TOTAL * 60.0 / BPM * sr))
n_idx = np.arange(N)
# integer cycles over the loop keep the wobble seamless at the boundary
wow   = (0.0022 * sr) * np.sin(2*np.pi * 8   / loop_N * n_idx)   # slow drift
flut  = (0.0006 * sr) * np.sin(2*np.pi * 220 / loop_N * n_idx)   # fast flutter
read = n_idx + wow + flut
read = np.clip(read, 0, N - 1)
xw = np.empty_like(x)
for ch in range(2):
    xw[:, ch] = np.interp(read, n_idx, x[:, ch])
x = xw

# ----------------------------------------------------------------------------
# 5) CAVERNOUS REVERB (decorrelated L/R, full tail kept)
# ----------------------------------------------------------------------------
def make_ir(seconds, decay, predelay_ms, seed):
    g = np.random.default_rng(seed)
    n = int(seconds * sr)
    env = np.exp(-np.linspace(0, 1, n) / decay)
    ir = g.standard_normal(n) * env
    ir = sosfilt(butter(2, 3500, 'low', fs=sr, output='sos'), ir)
    ir = np.concatenate([np.zeros(int(predelay_ms/1000*sr)), ir])
    return (ir / (np.max(np.abs(ir)) or 1.0)).astype(np.float32)

irL = make_ir(3.4, 0.40, 26, 1)
irR = make_ir(3.6, 0.43, 39, 2)
wetL = fftconvolve(x[:, 0], irL)
wetR = fftconvolve(x[:, 1], irR)
L = max(len(wetL), len(wetR))
wet = np.zeros((L, 2), dtype=np.float32)
wet[:len(wetL), 0] = wetL; wet[:len(wetR), 1] = wetR
wet /= (np.max(np.abs(wet)) or 1.0)

WET = 0.34                           # lighter than v1 so drums keep punch
xpad = np.zeros((L, 2), dtype=np.float32); xpad[:N] = x
y_full = (1.0 - WET) * xpad + WET * wet

# wrap reverb tail / releases back onto the start -> seamless loop
y = y_full[:loop_N].copy()
tail = y_full[loop_N:]
M = min(len(tail), loop_N)
y[:M] += tail[:M]

# ----------------------------------------------------------------------------
# 6) DUST: vinyl crackle + hiss, lo-fi filtering + soft saturation
# ----------------------------------------------------------------------------
# sparse vinyl crackle (random pops) + faint continuous hiss
crackle = np.zeros((loop_N, 2), dtype=np.float32)
n_pops = int(loop_N / sr * 55)       # ~55 pops/sec
idx = rng.integers(0, loop_N, n_pops)
amp = (rng.random(n_pops) ** 3) * 0.18
for ch in range(2):
    sel = rng.random(n_pops) < 0.9
    crackle[idx[sel], ch] += amp[sel] * rng.choice([-1, 1], sel.sum())
crackle = sosfilt(butter(2, 5000, 'low', fs=sr, output='sos'), crackle, axis=0)
hiss = rng.standard_normal((loop_N, 2)).astype(np.float32) * 0.004
y = y + crackle + hiss

# lo-fi: tame highs + clean sub, then gentle tape saturation
y = sosfilt(butter(4, 5200, 'low',  fs=sr, output='sos'), y, axis=0)
y = sosfilt(butter(2, 32,  'high', fs=sr, output='sos'), y, axis=0)
y = np.tanh(y * 1.6) / np.tanh(1.6)  # warm saturation

# headroom: peak ~ -2.5 dBFS
y = y / (np.max(np.abs(y)) or 1.0) * (10 ** (-2.5 / 20))
out16 = (np.clip(y, -1, 1) * 32767).astype(np.int16)

proc_wav = os.path.join(OUT, "labyrinth_dustmix.wav")
wavfile.write(proc_wav, sr, out16)
mp3_path = os.path.join(OUT, "labyrinth_dustmix.mp3")
seg = AudioSegment.from_wav(proc_wav)
seg.export(mp3_path, format='mp3', bitrate='192k')
os.remove(raw_wav)
print(f"DONE  duration={len(seg)/1000:.1f}s  dBFS={seg.dBFS:.1f}  max={seg.max_dBFS:.1f}")
