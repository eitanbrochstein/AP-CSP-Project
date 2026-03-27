import sounddevice as sd
import numpy as np

def note_to_frequency(note_string):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    octave = int(note_string[-1])
    note = note_string[:-1]
    
    note_index = notes.index(note)
    a4_index = notes.index('A')
    
    n = (note_index - a4_index) + ((octave - 4) * 12)
    
    frequency = 440 * (2 ** (n / 12))
    
    return round(frequency, 2)

def get_microphone_frequency():
    sample_rate = 44100
    duration = 0.25
    
    print("Listening...")
    
    audio_data = sd.rec(int(sample_rate * duration), 
                        samplerate=sample_rate, 
                        channels=1, 
                        blocking=True)
    
    audio_data = audio_data.flatten() 
    
    fft_data = np.fft.rfft(audio_data)
    frequencies = np.fft.rfftfreq(len(audio_data), 1.0 / sample_rate)
    
    magnitudes = np.abs(fft_data)
    
    peak_index = np.argmax(magnitudes)
    
    dominant_frequency = frequencies[peak_index]
    
    return round(dominant_frequency, 2)