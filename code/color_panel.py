import tkinter as tk
from tkinter import colorchooser

# This variable stores the selected color in BGR format 
selected_color = (0, 255, 0)  

def open_color_panel():
    #Opens a color picking dialog where the user can choose a color.
    global selected_color
    
    root = tk.Tk()
    root.withdraw() 

    color_code = colorchooser.askcolor(title="Choose Text Color")[0]

    if color_code:  
        r, g, b = map(int, color_code)  # Convert RGB values to integers
        selected_color = (b, g, r)  # Swap to BGR format for OpenCV

    root.destroy()  

def get_selected_color():
    return selected_color
