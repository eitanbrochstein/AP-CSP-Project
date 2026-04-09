import numpy as np
import pygame
import customtkinter as ctk
import sounddevice as sd
from frequencies import note_to_frequency

current_hz = 0.0
is_tuning = False
audio_stream = None
note_to_tune = None
target_hz = 0.0
button_to_tune = None

pygame.mixer.init()

string_list=[
    "C2",
    "C#2",
    "D2",
    "D#2",
    "E2",
    "F2",
    "F#2",
    "G2",
    "G#2",
    "A2",
    "A#2",
    "B2",
    "C3",
    "C#3",
    "D3",
    "D#3",
    "E3",
    "F3",
    "F#3",
    "G3",
    "G#3",
    "A3",
    "A#3",
    "B3",
    "C4",
    "C#4",
    "D4",
    "D#4",
    "E4",
    "F4",
    "F#4",
    "G4",
    "G#4",
    "A4",
    "A#4",
    "B4",
    "C5",
    "C#5",
    "D5",
    "D#5",
    "E5",
    "F5",
    "F#5",
    "G5",
    "G#5",
    "A5",
    "A#5"
]

# go into fl studio, get a guitar, and convert all the notes to sounds, and put it in a file

def play_synth_tone(note_name):
    try:
        sound = pygame.mixer.Sound(f"guitarnotes/{note_name}.wav")
        sound.play()
    except FileNotFoundError:
        print(f"Could not find audio file for {note_name}!")


def process_audio(indata, frames, time, status):
    global current_hz

    audio_data = indata.flatten()

    rms = np.sqrt(np.mean(audio_data ** 2))
    rms_threshold = 0.05
    if rms < rms_threshold:
        return

    fft_data = np.fft.rfft(audio_data)
    frequencies = np.fft.rfftfreq(len(audio_data), 1.0 / 44100)
    magnitudes = np.abs(fft_data)

    peak_index = np.argmax(magnitudes)

    # Parabolic interpolation for sub-bin accuracy
    if 1 <= peak_index < len(magnitudes) - 1:
        alpha = magnitudes[peak_index - 1]
        beta = magnitudes[peak_index]
        gamma = magnitudes[peak_index + 1]
        correction = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)
        loudest_freq = frequencies[peak_index] + correction * (frequencies[1] - frequencies[0])
    else:
        loudest_freq = frequencies[peak_index]
    peak_volume = magnitudes[peak_index]

    if target_hz > 0 and (target_hz * 1.8) <= loudest_freq <= (target_hz * 2.2):
        loudest_freq = loudest_freq / 2.0

    min_hz = 70.0
    max_hz = 1500.0
    volume_threshold = 0.5

    if target_hz > 0 and abs(loudest_freq - target_hz) > 40:
        return

    if peak_volume > volume_threshold and min_hz <= loudest_freq <= max_hz:
        current_hz = round(loudest_freq, 2)

def tune_string(index: int, button: ctk.CTkButton, strings_to_tune, update_tuning_callback):
    global button_to_tune
    global is_tuning, audio_stream, target_hz, note_to_tune
    if button_to_tune == button and is_tuning:
        is_tuning = False
        button_to_tune = None
        note_to_tune = None
        if audio_stream:
            audio_stream.stop()
            audio_stream.close()
    else:
        is_tuning = True
        button_to_tune = button
        note = strings_to_tune[index][0]
        play_synth_tone(note)
        get_note_frequency = note_to_frequency(note)

        note_to_tune = note
        target_hz = get_note_frequency
        audio_stream = sd.InputStream(channels=1, samplerate=44100, blocksize=16384, callback=process_audio)
        audio_stream.start()

        update_tuning_callback()

def tune_up(index: int, button: ctk.CTkButton, strings_to_tune, error_callback=None):
    note = strings_to_tune[index][0]
    note_position = string_list.index(note)
    if note_position < len(string_list) - 1 and note_to_tune is None:
        new_note = string_list[note_position + 1]
        strings_to_tune[index][0] = new_note
        button.configure(text=new_note)
    elif note_to_tune is not None and error_callback is not None:
        error_callback("You can't change the note while tuning.")

def tune_down(index: int, button: ctk.CTkButton, strings_to_tune, error_callback=None):
    note = strings_to_tune[index][0]
    note_position = string_list.index(note)
    if note_position > 0 and note_to_tune is None:
        new_note = string_list[note_position - 1]
        strings_to_tune[index][0] = new_note
        button.configure(text=new_note)
    elif note_to_tune is not None and error_callback is not None:
        error_callback("You can't change the note while tuning.")