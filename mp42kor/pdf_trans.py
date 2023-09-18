import os
import pdfplumber
import tkinter as tk
from tkinter import filedialog
import whisper
from whisper.utils import get_writer
from deep_translator import GoogleTranslator
import text_extraction_translation as textExtractor

def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")

# Open a folder selection dialog
root = tk.Tk()
root.withdraw()  # Hide the main window
directory = filedialog.askdirectory()  # Open the folder selection dialog

# Iterate over all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a .mp4 file
    if os.path.splitext(filename)[1] in ['.pdf']:
        pdf_file_path = os.path.join(directory, filename)
        
        # Check the file size and load the appropriate Whisper model
        folder = directory + "/output"
        createDirectory(folder)
        textExtractor.extract_and_translate_file(
        file_path=pdf_file_path, destination_path=(str(folder) + "/"), paths_relative=False)
        
        
