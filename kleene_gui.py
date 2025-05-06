import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from kleene_core import regex_to_nfa


class KleeneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de AFND - Algoritmo de Kleene")

        self.setup_widgets()

    def setup_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(sticky='nsew')  # Allow frame to expand with the window

    # Configure the grid to stretch
        self.root.grid_rowconfigure(0, weight=1)  # Row 0 (frame) will expand
        self.root.grid_columnconfigure(0, weight=1)  # Column 0 (frame) will expand

    # Expresión Regular label and entry
        ttk.Label(frm, text="Expresión Regular:").grid(column=0, row=0, sticky='w')
        self.entry = ttk.Entry(frm, width=40)
        self.entry.grid(column=1, row=0, sticky='ew')  # Make entry expand horizontally

    # Button to generate AFND
        self.button = ttk.Button(frm, text="Generar AFND", command=self.process_input)
        self.button.grid(column=2, row=0, sticky='ew')  # Make button expand horizontally

    # Text widget for displaying results
        self.text = tk.Text(frm, width=60, height=15)
        self.text.grid(column=0, row=1, columnspan=3, pady=10, sticky='nsew')  # Allow Text to resize

    # Label for displaying the image
        self.image_label = ttk.Label(frm)
        self.image_label.grid(column=0, row=2, columnspan=3, sticky='nsew')  # Allow image to resize
        

    # Make the frame resize properly when the window is resized
        frm.grid_rowconfigure(1, weight=1)  
        frm.grid_columnconfigure(0, weight=1)  
        frm.grid_columnconfigure(1, weight=1)  
        frm.grid_columnconfigure(2, weight=1)  

    def process_input(self):
        expr = self.entry.get().strip()
        if not expr:
            messagebox.showerror("Error", "Ingrese una expresión regular.")
            return

        try:
            postfix, transitions = regex_to_nfa(expr)
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, f"Postfija: {postfix}\n\n{transitions}")
            self.show_image("nfa_output.png")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_image(self, path):
        if os.path.exists(path):
            img = Image.open(path)
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo)
            self.image_label.image = photo

if __name__ == "__main__":
    root = tk.Tk()
    app = KleeneApp(root)
    root.mainloop()
