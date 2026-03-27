import customtkinter as ctk
import math
import tkinter as tk
import sounddevice as sd
import numpy as np
from PIL import Image
from frequencies import note_to_frequency
from guitar import play_synth_tone, string_list

app = ctk.CTk()
app.title("Guitar Tuner App")
app.geometry("1000x800")
app.resizable(False, False)

app_logo = tk.PhotoImage(file="images/guitarimage.png")
app.iconphoto(True, app_logo)

current_hz = 0.0 
is_tuning = False
audio_stream = None

button_to_tune = None

def process_audio(indata, frames, time, status):
    global current_hz
    
    audio_data = indata.flatten() 
    
    fft_data = np.fft.rfft(audio_data)
    frequencies = np.fft.rfftfreq(len(audio_data), 1.0 / 44100)
    magnitudes = np.abs(fft_data)
    
    # Find the loudest pitch
    peak_index = np.argmax(magnitudes)
    
    if magnitudes[peak_index] > 0.1: 
        current_hz = round(frequencies[peak_index], 2)

def tune_string(index: int, button: ctk.CTkButton):
    global button_to_tune
    global is_tuning, audio_stream
    if button_to_tune == button:
        is_tuning = False
        button_to_tune = None
        if audio_stream:
            audio_stream.stop()
            audio_stream.close()
    else:
        is_tuning = True
        button_to_tune = button
        note = strings_to_tune[index][0]
        guitar_sound = play_synth_tone(note)

        audio_stream = sd.InputStream(channels=1, samplerate=44100, callback=process_audio)
        audio_stream.start()

        update_tuning()

def tune_up(index: int, button: ctk.CTkButton):
    note = strings_to_tune[index][0]
    note_position = string_list.index(note)
    if note_position < len(string_list) - 1:
        new_note = string_list[note_position + 1]
        strings_to_tune[index][0] = new_note
        button.configure(text=new_note)

def tune_down(index: int, button: ctk.CTkButton):
    note = strings_to_tune[index][0]
    note_position = string_list.index(note)
    if note_position > 0:
        new_note = string_list[note_position - 1]
        strings_to_tune[index][0] = new_note
        button.configure(text=new_note)


ctk.set_appearance_mode("dark")
app.configure(fg_color="#1a1a1a")

strings_to_tune = [
    ["E2", 25, 500],
    ["A2", 25, 300],
    ["D3", 25, 100],
    ["G3", 600, 100],
    ["B3", 600, 300],
    ["E4", 600, 500]
]

separator_colors = ["#ff0000", "#f0850c", "#fafa05", "#09fa05", "#0000ff", "#7b00ff"]

guitar_image = ctk.CTkImage(dark_image=Image.open("images/guitarimage.png"), size=(500,500))
guitar_label = ctk.CTkLabel(master=app, image=guitar_image, text="")
guitar_label.place(x=145, y=125)

guitar_tuner_label = ctk.CTkLabel(master=app,
                                  text="Guitar Tuner",
                                  width=800,
                                  font=(".AppleSystemUIFont", 50, "bold"),
                                  anchor="center")
guitar_tuner_label.place(x=0, y=15)

string_buttons: list[ctk.CTkButton] = []#

for i, string in enumerate(strings_to_tune):
    btn_size = 125
    
    string_btn = ctk.CTkButton(master=app,
                        text=string[0],
                        font=(".AppleSystemUIFont", 40, "bold"),
                        width=btn_size,
                        height=btn_size,
                        border_spacing=10,
                        corner_radius=math.inf,
                        fg_color="#1DB954",
                        hover_color="#1ed760",
                        anchor="center")
    
    string_btn.configure(command=lambda idx=i, btn=string_btn: tune_string(idx, btn))

    string_btn.place(x=string[1], y=string[2])
    string_buttons.append(string_btn)

    tuning_label = ctk.CTkLabel(master=app,
                                text=f"{i+1}:",
                                font=(".AppleSystemUIFont", 30, "bold"),
                                anchor="center"
                                )
    tuning_label.place(x=900, y=(i*125)+30)

    tune_up_button = ctk.CTkButton(master=app,
                            text="↑",
                            font=(".AppleSystemUIFont", 30, "bold"),
                            fg_color="#3c3c3c",
                            hover_color="#3c3c3c",
                            anchor="center",
                            corner_radius=0,
                            border_spacing=2,
                            width=0,
                            height=60)
    
    tune_up_button.place(x=850, y=(i*125)+75)
    tune_up_button.configure(command=lambda idx=i, button=string_btn: tune_up(idx, button))

    tune_down_button = ctk.CTkButton(master=app,
                            text="↓",
                            font=(".AppleSystemUIFont", 30, "bold"),
                            fg_color="#3c3c3c",
                            hover_color="#3c3c3c",
                            anchor="center",
                            corner_radius=0,
                            border_spacing=2,
                            width=0,
                            height=60)
    
    tune_down_button.place(x=950, y=(i*125)+75)
    tune_down_button.configure(command=lambda idx=i, button=string_btn: tune_down(idx, button))

    separator = ctk.CTkLabel(master=app,
                             text="",
                             fg_color=separator_colors[i],
                             anchor="center",
                             width=70,
                             height=60)
    
    separator.place(x=880, y=(i*125)+75)

def check_active_button():
    for button in string_buttons:
        if button == button_to_tune:
            button.configure(fg_color="#ffffff", hover_color="#ffffff", text_color="#000000")
        else:
            button.configure(fg_color="#1DB954", hover_color="#1ed760", text_color="#ffffff")
    
    # Check again every 100 milliseconds
    app.after(5, check_active_button)

# Start the checking loop
check_active_button()

def update_tuning():
    if is_tuning:
        print(current_hz)
        
        # Loop this function again in 50 milliseconds!
        app.after(50, update_tuning)

app.mainloop()