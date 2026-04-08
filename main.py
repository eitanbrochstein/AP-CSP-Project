import customtkinter as ctk
import math
import sys
import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import numpy as np
from PIL import Image
import guitar

if sys.platform == "win32":
    UI_FONT = "Segoe UI"
elif sys.platform == "darwin":
    UI_FONT = ".AppleSystemUIFont"
else:
    UI_FONT = "DejaVu Sans"

app = ctk.CTk()
app.title("Guitar Tuner App")
app.geometry("1000x800")
app.resizable(False, False)

app_logo = tk.PhotoImage(file="images/guitarimage.png")
app.iconphoto(True, app_logo)

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
                                  font=(UI_FONT, 50, "bold"),
                                  anchor="center")
guitar_tuner_label.place(x=0, y=15)

string_buttons: list[ctk.CTkButton] = []#

for i, string in enumerate(strings_to_tune):
    btn_size = 125
    
    string_btn = ctk.CTkButton(master=app,
                        text=string[0],
                        font=(UI_FONT, 40, "bold"),
                        width=btn_size,
                        height=btn_size,
                        border_spacing=10,
                        corner_radius=math.inf,
                        fg_color="#1DB954",
                        hover_color="#1ed760",
                        anchor="center")
    
    string_btn.configure(command=lambda idx=i, btn=string_btn: guitar.tune_string(idx, btn, strings_to_tune, update_tuning))

    string_btn.place(x=string[1], y=string[2])
    string_buttons.append(string_btn)

    separator = ctk.CTkLabel(master=app,
                             text="",
                             fg_color=separator_colors[i],
                             anchor="center",
                             width=70,
                             height=60)
    
    separator.place(x=880, y=(i*125)+75)

    tuning_label = ctk.CTkLabel(master=app,
                                text=f"{i+1}:",
                                font=(UI_FONT, 30, "bold"),
                                anchor="center"
                                )
    tuning_label.place(x=900, y=(i*125)+30)

    tune_up_button = ctk.CTkButton(master=app,
                            text="↑",
                            font=(UI_FONT, 30, "bold"),
                            fg_color="#3c3c3c",
                            hover_color="#3c3c3c",
                            anchor="center",
                            corner_radius=0,
                            border_spacing=2,
                            width=0,
                            height=60)
    
    tune_up_button.place(x=860, y=(i*125)+75)
    tune_up_button.configure(command=lambda idx=i, button=string_btn: guitar.tune_up(idx, button, strings_to_tune, error_msg))

    tune_down_button = ctk.CTkButton(master=app,
                            text="↓",
                            font=(UI_FONT, 30, "bold"),
                            fg_color="#3c3c3c",
                            hover_color="#3c3c3c",
                            anchor="center",
                            corner_radius=0,
                            border_spacing=2,
                            width=0,
                            height=60)
    
    tune_down_button.place(x=950, y=(i*125)+75)
    tune_down_button.configure(command=lambda idx=i, button=string_btn: guitar.tune_down(idx, button, strings_to_tune, error_msg))

def check_active_button():
    for button in string_buttons:
        if button == guitar.button_to_tune:
            button.configure(fg_color="#ffffff", hover_color="#ffffff", text_color="#000000")
        else:
            button.configure(fg_color="#1DB954", hover_color="#1ed760", text_color="#ffffff")
    
    app.after(5, check_active_button)

check_active_button()


tuner_meter = ctk.CTkProgressBar(master=app, width=500, height=50)
tuner_meter.set(0.5)
tuner_meter.place(x=175, y=700)

tuner_text = ctk.CTkLabel(master=app,
                          text="Start Tuning!",
                          font=(UI_FONT, 30, "bold"),
                          bg_color="transparent")
tuner_text.place(in_=tuner_meter, relx=0.5, rely=0.5, anchor="center")


def update_tuning():
    if guitar.is_tuning:
        if guitar.current_hz > 0:
            cents = 1200 * math.log2(guitar.current_hz / guitar.target_hz)
            meter_value = 0.5 + (cents / 100)
            tuner_meter.set(max(0, min(1, meter_value)))
            tuner_text.configure(text=f"{round(cents)} ¢")

            if abs(cents) <= 5:
                tuner_meter.configure(progress_color="#1DB954")
            elif cents > 5:
                tuner_meter.configure(progress_color="#FF4B4B")
            else:
                tuner_meter.configure(progress_color="#3B8ED0")
    else:
        tuner_text.configure(text="Start Tuning!")
        tuner_meter.set(0.5)
        tuner_meter.configure(progress_color="#3B8ED0")
    app.after(50, update_tuning)

# Error Message

def click_error_msg(error_msg: ctk.CTkButton):
    error_label.place_forget()

error_label = ctk.CTkButton(master=app, 
                            text="",
                            anchor="center",
                            font=(UI_FONT, 30, "bold"),
                            fg_color="#FF746C",
                            hover_color="#A64A45",
                            height=70,
                            corner_radius=0,
                            width=650)

error_label.place_forget()
error_label.configure(command=lambda error=error_label: click_error_msg(error))

def error_msg(message: str, title: str = "Error"):
    error_label.place(relx=0.5, y=50, anchor="center")
    error_label.configure(text=message)

app.mainloop()