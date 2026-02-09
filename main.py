import tkinter as tk
from src.ui import OCRApp

def main():
    root = tk.Tk()
    root.title("TinyWorld AI - Offline OCR")
    root.geometry("900x700")
    
    app = OCRApp(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
