# 🎵 Melodian — генерация музыки кодом

Проект для алгоритмической композиции музыки: **music21 → MIDI → аудио (.wav/.mp3)**.
Музыка пишется как код (динамически, через `music21`), а затем рендерится в звук
через FluidSynth с General MIDI саундфонтом.

> Имя проекта `Melodian` выбрано по умолчанию — переименуйте свободно.

## Что установлено

| Компонент | Назначение |
|-----------|-----------|
| Навык `music-generation` v2.0.0 | `.claude/skills/music-generation/` — инструменты и паттерны композиции |
| Python: `music21`, `mido`, `midi2audio`, `pydub`, `numpy`, `scipy` | композиция + рендер + обработка аудио |
| FluidSynth 2.3.4 | рендер MIDI → WAV |
| ffmpeg | конвертация WAV → MP3 |
| `FluidR3_GM.sf2` (142 МБ) | GM-саундфонт, `/usr/share/sounds/sf2/FluidR3_GM.sf2` |

## Быстрый старт

```bash
# Установка зависимостей (если контейнер пересоздан)
bash .claude/skills/music-generation/install.sh

# Пример: рендер JSON-структуры в MP3
python3 .claude/skills/music-generation/scripts/midi_render.py structure.json output.mp3
```

Тестовая 8-тактовая мелодия лежит в `music-output/test_melody.mp3`.

## Пример промпта

> «Сгенерируй зацикленную фоновую музыку для игры: 16 тактов, ля-минор, 90 BPM,
> спокойное арпеджио на пиано + мягкий бас, чтобы конец бесшовно стыковался с началом,
> и отрендери в `music-output/game_loop.mp3`».
