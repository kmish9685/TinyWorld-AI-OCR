import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import cv2
import os
import sys

# Add src to path if needed (though running from root usually works)
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import preprocess, segment, recognize, postprocess
from src.premium_style import PremiumButton, GlassPanel, create_divider

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TinyWorld AI - OCR Prototype")
        self.root.geometry("1400x800")
        
        # HEADLESSUI-INSPIRED DARK THEME
        self.bg_dark = "#0F0F1E"           # Deep dark background
        self.bg_gradient_1 = "#1A1A2E"     # Dark purple-blue
        self.bg_gradient_2 = "#16213E"     # Dark blue
        self.glass_bg = "#1E1E3F"          # Glassmorphism panel
        self.glass_border = "#2D2D5F"      # Glass border
        self.card_bg = "#1C1C35"           # Card background
        self.primary = "#6366F1"           # Indigo (primary action)
        self.primary_hover = "#4F46E5"     # Darker indigo
        self.accent = "#8B5CF6"            # Purple accent
        self.success = "#10B981"           # Green success
        self.text_primary = "#F9FAFB"      # Almost white
        self.text_secondary = "#9CA3AF"    # Gray text
        self.text_muted = "#6B7280"        # Muted gray
        self.border_subtle = "#374151"     # Subtle border
        
        self.root.configure(bg=self.bg_dark)
        
        # 0. MODERN DARK HEADER
        header = tk.Frame(self.root, bg=self.bg_gradient_1, height=80)
        header.pack(fill="x")
        
        # Title with gradient effect (simulated with shadow)
        title = tk.Label(header, text="TinyWorld AI", 
                        font=("Segoe UI", 28, "bold"), bg=self.bg_gradient_1, fg=self.text_primary)
        title.pack(pady=(15, 0))
        
        subtitle = tk.Label(header, text="Offline OCR • Multi-Language • Lightweight", 
                           font=("Segoe UI", 10), bg=self.bg_gradient_1, fg=self.text_secondary)
        subtitle.pack(pady=(2, 15))
        
        # Initialize State & Recognizer FIRST
        self.current_image_path = None
        self.current_cv_image = None
        self.recognizer = recognize.Recognizer()
        
        # UI Elements (Now can access self.recognizer)
        self.setup_ui()

        
    def setup_ui(self):
        # MINIMAL PIPELINE INDICATOR
        pipeline_frame = tk.Frame(self.root, bg=self.bg_dark, height=50)
        pipeline_frame.pack(fill="x", pady=(0, 10))
        
        self.pipeline_steps = {}
        steps = ["Preprocessing", "OCR Processing", "Post-Processing", "Complete"]
        for i, step in enumerate(steps):
            lbl = tk.Label(pipeline_frame, text=step, font=("Segoe UI", 9), 
                          bg=self.bg_dark, fg=self.text_muted, padx=12, pady=6)
            lbl.pack(side="left", padx=8, pady=10)
            self.pipeline_steps[i] = lbl
        

        
        # Main Layout with Dark Theme
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # DARK GLASSMORPHISM CONTROL PANEL (Wider for better proportions)
        control_panel = GlassPanel(main_frame, glass_bg=self.glass_bg, border_color=self.glass_border, width=280)
        control_panel.pack(side="left", fill="y", padx=(0, 25), ipadx=15)
        
        # Panel Header
        tk.Label(control_panel, text="Controls", font=("Segoe UI", 18, "bold"), 
                bg=self.glass_bg, fg=self.text_primary).pack(pady=(20, 15), padx=25)
        
        # PREMIUM UPLOAD BUTTON with hover effect
        self.btn_upload = PremiumButton(control_panel, text="📁 Upload Image", 
                                        base_bg=self.card_bg, hover_bg=self.glass_border, active_bg=self.border_subtle,
                                        fg=self.text_primary,
                                        font=("Segoe UI", 11, "bold"), width=20, 
                                        relief="flat", bd=0, cursor="hand2",
                                        padx=20, pady=14,
                                        command=self.upload_image)
        self.btn_upload.pack(pady=(0, 12), padx=25)
        
        # PREMIUM EXTRACT BUTTON with gradient-like hover
        self.btn_extract = PremiumButton(control_panel, text="✨ Extract Text", 
                                         base_bg=self.primary, hover_bg=self.primary_hover, active_bg="#3730A3",
                                         fg="white", 
                                         font=("Segoe UI", 12, "bold"), width=20,
                                         relief="flat", bd=0, cursor="hand2",
                                         padx=20, pady=16,
                                         command=self.start_extraction)
        self.btn_extract.pack(pady=(0, 12), padx=25)
        
        # Subtle Divider with helper function
        create_divider(control_panel, color=self.border_subtle, height=1, pady=18)
        
        # PREMIUM SUCCESS BUTTON
        self.btn_demo = PremiumButton(control_panel, text="🎬 Run Demo", 
                                      base_bg=self.success, hover_bg="#059669", active_bg="#047857",
                                      fg="white", 
                                      font=("Segoe UI", 11, "bold"), width=20,
                                      relief="flat", bd=0, cursor="hand2",
                                      padx=20, pady=14,
                                      command=self.run_demo)
        self.btn_demo.pack(pady=(0, 12), padx=25)
        
        create_divider(control_panel, color=self.border_subtle, height=1, pady=18)
        
        # LANGUAGE SELECTOR
        tk.Label(control_panel, text="🌍 Language", 
                font=("Segoe UI", 11, "bold"), bg=self.glass_bg, fg=self.text_primary).pack(pady=(10, 6), padx=25)
        
        
        from tkinter import ttk
        self.language_var = tk.StringVar(value="English")
        self.language_options = {
            "English": "eng",
            "Hindi (हिंदी)": "hin",
            "Urdu (اردو)": "urd",
            "Sanskrit (संस्कृत)": "san",
            "Arabic (العربية)": "ara",
            "French": "fra",
            "Spanish": "spa",
            "German": "deu",
            "Chinese (中文)": "chi_sim",
            "Multi (Eng+Hin)": "eng+hin"
        }
        
        # Style the dropdown for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TCombobox', 
                       fieldbackground=self.card_bg,
                       background=self.card_bg,
                       foreground=self.text_primary,
                       bordercolor=self.border_subtle,
                       arrowcolor=self.text_secondary)
        
        lang_dropdown = ttk.Combobox(control_panel, textvariable=self.language_var, 
                                     values=list(self.language_options.keys()),
                                     state="readonly", width=20, font=("Segoe UI", 9),
                                     style='Dark.TCombobox')
        lang_dropdown.pack(pady=(0, 10), padx=25)
        
        tk.Frame(control_panel, height=1, bg=self.border_subtle).pack(fill="x", pady=15, padx=25)
        
        # MODERN TOGGLE SWITCHES (Checkboxes)
        self.safe_mode_var = tk.BooleanVar(value=True)
        self.chk_safe = tk.Checkbutton(control_panel, text="✓ Safe Mode", 
                                       variable=self.safe_mode_var, bg=self.glass_bg,
                                       font=("Segoe UI", 10, "bold"), fg=self.text_primary,
                                       activebackground=self.glass_bg,
                                       selectcolor=self.card_bg)
        self.chk_safe.pack(pady=(10, 4), anchor="w", padx=25)
        tk.Label(control_panel, text="Minimal Correction", 
                font=("Segoe UI", 9), bg=self.glass_bg, fg=self.text_muted).pack(anchor="w", padx=25)
        
        self.honesty_var = tk.BooleanVar(value=False)
        self.chk_honest = tk.Checkbutton(control_panel, text="✓ Honesty Filter", 
                                         variable=self.honesty_var, bg=self.glass_bg,
                                         font=("Segoe UI", 10, "bold"), fg=self.text_primary,
                                         activebackground=self.glass_bg,
                                         selectcolor=self.card_bg)
        self.chk_honest.pack(pady=(14, 4), anchor="w", padx=25)
        tk.Label(control_panel, text="Mask low confidence", 
                font=("Segoe UI", 9), bg=self.glass_bg, fg=self.text_muted).pack(anchor="w", padx=25)
        
        tk.Frame(control_panel, height=1, bg=self.border_subtle).pack(fill="x", pady=18, padx=25)
        
        # DARK METRICS PANEL
        tk.Label(control_panel, text="System Metrics", 
                font=("Segoe UI", 12, "bold"), bg=self.glass_bg, fg=self.text_primary).pack(pady=(12, 10), padx=25)
        
        # Metric Cards
        self.lbl_model_size = tk.Label(control_panel, text="Model: Checking...", 
                                       font=("Segoe UI", 10), bg=self.glass_bg, fg=self.text_secondary)
        self.lbl_model_size.pack(pady=4)

        # Highlighted Metric with accent color
        self.lbl_params = tk.Label(control_panel, text="Params/Char: ...", 
                                   font=("Segoe UI", 9, "bold"), bg=self.accent, 
                                   fg="white", padx=12, pady=5)
        self.lbl_params.pack(pady=8)
        
        self.lbl_time = tk.Label(control_panel, text="Time: 0ms", 
                                font=("Segoe UI", 10), bg=self.glass_bg, fg=self.text_secondary)
        self.lbl_time.pack(pady=4)
        
        # Status at bottom
        self.lbl_status = tk.Label(control_panel, text="• Ready", 
                                  font=("Segoe UI", 10, "italic"), bg=self.glass_bg, fg=self.primary)
        self.lbl_status.pack(side="bottom", pady=20)

        # Update Metrics
        size_mb = self.recognizer.get_model_size_mb()
        self.lbl_model_size.config(text=f"Model: {size_mb:.2f} MB")
        
        # Calculate Params/Char (Approx)
        # Size in Bytes / 37 characters
        if size_mb > 0:
            size_bytes = size_mb * 1024 * 1024
            params_per_char_kb = (size_bytes / 37) / 1024
            self.lbl_params.config(text=f"Params/Char: ~{params_per_char_kb:.1f} KB")

        # Column 2: Image Views (Middle) - Optimized Layout
        image_panel = tk.Frame(main_frame, bg=self.bg_dark)
        image_panel.pack(side="left", fill="both", expand=True)
        
        view_frame = tk.Frame(image_panel, bg=self.bg_dark)
        view_frame.pack(fill="both", expand=True)
        
        # Original - Dark Glass Frame with better proportions
        frame_orig = tk.LabelFrame(view_frame, text="Original Input", bg=self.glass_bg,
                                  fg=self.text_primary, font=("Segoe UI", 11, "bold"),
                                  bd=2, relief="flat", highlightbackground=self.glass_border,
                                  highlightthickness=2)
        frame_orig.pack(side="left", fill="both", expand=True, padx=6, pady=5)
        self.lbl_image_orig = tk.Label(frame_orig, text="No Image", bg=self.card_bg, fg=self.text_muted,
                                      font=("Segoe UI", 10))
        self.lbl_image_orig.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Vision - Dark Glass Frame with better proportions
        frame_vision = tk.LabelFrame(view_frame, text="AI Vision (Processed)", bg=self.glass_bg,
                                    fg=self.text_primary, font=("Segoe UI", 11, "bold"),
                                    bd=2, relief="flat", highlightbackground=self.glass_border,
                                    highlightthickness=2)
        frame_vision.pack(side="left", fill="both", expand=True, padx=6, pady=5)
        self.lbl_image_vision = tk.Label(frame_vision, text="Waiting...", bg=self.card_bg, fg=self.text_muted,
                                        font=("Segoe UI", 10))
        self.lbl_image_vision.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Column 3: DARK OUTPUT PANEL with optimized width
        output_panel = GlassPanel(main_frame, glass_bg=self.glass_bg, border_color=self.glass_border, width=340)
        output_panel.pack(side="right", fill="both", padx=(20, 0))
        
        # Success Header for Results
        output_header = tk.Frame(output_panel, bg=self.success, height=50)
        output_header.pack(fill="x")
        output_header.pack_propagate(False)
        tk.Label(output_header, text="📄 Extracted Text", 
                font=("Segoe UI", 14, "bold"), bg=self.success, fg="white").pack(pady=12)
        
        
        from tkinter import ttk
        
        # Style notebook for dark theme
        style = ttk.Style()
        style.configure('Dark.TNotebook', background=self.glass_bg, borderwidth=0)
        style.configure('Dark.TNotebook.Tab', background=self.card_bg, foreground=self.text_primary,
                       padding=[12, 8], font=("Segoe UI", 9, "bold"))
        style.map('Dark.TNotebook.Tab', background=[('selected', self.primary)],
                 foreground=[('selected', 'white')])
        
        notebook = ttk.Notebook(output_panel, style='Dark.TNotebook')
        notebook.pack(fill="both", expand=True, pady=(12,8), padx=12)
        
        # Tab 1: Final Output with Dark Styling
        self.tab_raw = tk.Frame(notebook, bg=self.card_bg)
        notebook.add(self.tab_raw, text="Final Output")
        self.txt_output = scrolledtext.ScrolledText(self.tab_raw, font=("Segoe UI", 11), 
                                                    width=32, wrap=tk.WORD,
                                                    bg=self.card_bg, fg=self.text_primary,
                                                    relief="flat", padx=12, pady=12,
                                                    insertbackground=self.text_primary)
        self.txt_output.pack(fill="both", expand=True)
        
        # Tab 2: Debug
        self.tab_struct = tk.Frame(notebook, bg=self.card_bg)
        notebook.add(self.tab_struct, text="Raw/Debug")
        self.txt_debug = scrolledtext.ScrolledText(self.tab_struct, font=("Consolas", 9), 
                                                   width=32, fg=self.text_secondary, bg=self.card_bg,
                                                   relief="flat", padx=12, pady=12,
                                                   insertbackground=self.text_secondary)
        self.txt_debug.pack(fill="both", expand=True)
        
        # Premium Save Button with hover effect
        save_btn = PremiumButton(output_panel, text="💾 Save to File", 
                                base_bg=self.primary, hover_bg=self.primary_hover, active_bg="#3730A3",
                                fg="white", font=("Segoe UI", 11, "bold"),
                                relief="flat", bd=0, cursor="hand2",
                                padx=18, pady=14,
                                command=self.save_text)
        save_btn.pack(pady=14, padx=14, fill="x")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")])
        if file_path:
            self.current_image_path = file_path
            self.load_image_preview(file_path, is_original=True)
            self.lbl_image_vision.config(image='', text="Waiting for extraction...")
            self.lbl_status.config(text="Image Loaded")
            self.txt_output.delete("1.0", tk.END)
            self.txt_debug.delete("1.0", tk.END)

    def load_image_preview(self, path, is_original=True):
        try:
            image = Image.open(path)
            # Resize logic to fit 300x400 approx
            image.thumbnail((300, 400)) 
            tk_image = ImageTk.PhotoImage(image)
            
            if is_original:
                self.tk_image_orig = tk_image # Keep ref
                self.lbl_image_orig.config(image=tk_image, text="")
            else:
                self.tk_image_vision = tk_image # Keep ref
                self.lbl_image_vision.config(image=tk_image, text="")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def start_extraction(self):
        if not self.current_image_path:
            messagebox.showwarning("Warning", "Please upload an image first.")
            return
            
        self.btn_extract.config(state="disabled")
        self.lbl_status.config(text="Starting Pipeline...")
        self.txt_output.delete("1.0", tk.END)
        self.txt_debug.delete("1.0", tk.END)
        
        # Reset Pipeline Highlight
        for lbl in self.pipeline_steps.values():
            lbl.config(fg="#999", font=("Arial", 9))
        
        thread = threading.Thread(target=self.process_image)
        thread.start()

    def run_demo(self):
        """
        One-click demo: Loads 'demo_image.png' AND turns off Safe Mode.
        """
        demo_path = os.path.join(os.path.dirname(__file__), "..", "demo_image.png")
        demo_path = os.path.abspath(demo_path)
        
        if not os.path.exists(demo_path):
            messagebox.showerror("Demo Error", "Demo image not found.")
            return
            
        # FORCE DEMO SETTINGS
        self.safe_mode_var.set(False) # Turn off Safe Mode for Demo
        self.honesty_var.set(False)   # Turn off Honesty Filter for Demo
        
        self.current_image_path = demo_path
        self.load_image_preview(demo_path, is_original=True)
        self.lbl_status.config(text="Demo Loaded")
        
        self.root.after(500, self.start_extraction)
        
    def highlight_step(self, step_idx):
        self.root.after(0, lambda: self._highlight_step_ui(step_idx))
        
    def _highlight_step_ui(self, step_idx):
        # Dark theme smooth transitions
        for lbl in self.pipeline_steps.values():
             lbl.config(fg=self.text_muted, bg=self.bg_dark, font=("Segoe UI", 9))
        # Highlight active step with primary indigo
        if step_idx in self.pipeline_steps:
             self.pipeline_steps[step_idx].config(fg=self.primary, bg=self.bg_dark, font=("Segoe UI", 9, "bold"))

    def process_image(self):
        import time
        start_time = time.time()
        try:
            safe_mode = self.safe_mode_var.get()
            honest_mode = self.honesty_var.get()
            
            # Step 1: Cleaning
            self.highlight_step(0)
            self.update_status("Step 1: Cleaning Image...")
            binary, original = preprocess.preprocess_image(self.current_image_path)
            
            # Save and Show Debug Vision (preprocessed image)
            cv2.imwrite("debug_segmentation.png", binary)
            self.update_preview_vision("debug_segmentation.png")
            
            # Step 2 & 3: Tesseract Recognition (handles detection + recognition)
            self.highlight_step(1)
            self.update_status("Step 2-3: Tesseract OCR Processing...")
            
            
            # Get selected language
            selected_lang_name = self.language_var.get()
            lang_code = self.language_options.get(selected_lang_name, "eng")
            
            # Use Tesseract to extract text directly from preprocessed image
            extracted_text, confidence = self.recognizer.extract_text_with_layout(binary, lang=lang_code)
            
            if not extracted_text:
                self.finish_processing("No text detected.", "", success=False, time_taken=time.time()-start_time)
                return
            
            raw_text = extracted_text
            debug_text = f"Average Confidence: {confidence:.2%}\n\n{extracted_text}"
            
            # (Tesseract handles all recognition - no character loop needed)
                
            # Step 4: Rule Correction
            self.highlight_step(3)
            self.update_status("Step 4: Rule-based Correction...")
            final_text = postprocess.clean_text(raw_text, safe_mode=safe_mode)
            
            self.finish_processing(final_text, debug_text, success=True, time_taken=time.time()-start_time)
            
        except Exception as e:
            self.finish_processing(f"Error: {str(e)}", "", success=False, time_taken=time.time()-start_time)

    def update_preview_vision(self, path):
        self.root.after(0, lambda: self.load_image_preview(path, is_original=False))

    def update_status(self, text):
        self.root.after(0, lambda: self.lbl_status.config(text=text))

    def finish_processing(self, text, debug_text, success, time_taken):
        self.root.after(0, lambda: self._update_ui_finished(text, debug_text, success, time_taken))
        
    def _update_ui_finished(self, text, debug_text, success, time_taken):
        self.btn_extract.config(state="normal")
        self.lbl_status.config(text="Analysis Complete" if success else "Failed")
        
        self.txt_output.insert(tk.END, text)
        self.txt_debug.insert(tk.END, debug_text)
        
        self.lbl_time.config(text=f"Time: {time_taken*1000:.0f} ms")
        
        # Reset pipeline highlights
        for lbl in self.pipeline_steps.values():
             lbl.config(fg="#999", font=("Arial", 9))

    def save_text(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Success", "Text saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

