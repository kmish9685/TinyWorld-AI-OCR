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

class OCRApp:
    def __init__(self, root):
        self.root = root
        
        # APPLE-INSPIRED PREMIUM COLOR SCHEME
        self.bg_gradient_start = "#F5F7FA"  # Light gradient start
        self.bg_gradient_end = "#E8EAF6"    # Light gradient end
        self.bg_color = "#F2F4F8"           # Soft background
        self.card_bg = "#FFFFFF"            # Pure white cards
        self.card_glass = "#F8F9FA"         # Frosted glass effect
        self.primary = "#007AFF"            # iOS Blue
        self.accent_color = "#5E5CE6"       # iOS Purple
        self.success = "#34C759"            # iOS Green
        self.text_color = "#1D1D1F"         # Apple text
        self.text_secondary = "#86868B"     # Apple secondary text
        self.border_light = "#E5E7EB"       # Subtle border
        self.shadow = "#00000010"           # Soft shadow
        
        self.root.configure(bg=self.bg_color)
        
        # Initialize State & Recognizer FIRST
        self.current_image_path = None
        self.current_cv_image = None
        self.recognizer = recognize.Recognizer()
        
        # UI Elements (Now can access self.recognizer)
        self.setup_ui()

        
    def setup_ui(self):
        # 0. PREMIUM iOS-STYLE HEADER
        banner = tk.Frame(self.root, bg="#1D1D1F", height=28)
        banner.pack(fill="x")
        tk.Label(banner, text="designed for offline devices  |  accuracy traded for size & speed  |  non-universal", 
                 font=("Segoe UI", 8), bg="#1D1D1F", fg=self.text_secondary).pack(pady=5)

        # iOS-STYLE GRADIENT HEADER
        header = tk.Frame(self.root, bg=self.primary, height=75)
        header.pack(fill="x")
        title = tk.Label(header, text="TinyWorld AI - OCR Prototype", 
                        font=("Segoe UI", 24, "bold"), bg=self.primary, fg="white")
        title.pack(pady=18)
        
        # iOS-STYLE PILL PIPELINE STEPS
        self.pipeline_frame = tk.Frame(self.root, bg="#FAFAFA", height=40)
        self.pipeline_frame.pack(fill="x", pady=0)
        
        self.pipeline_steps = {}
        steps = ["1. Cleaning", "2. Detection", "3. Recognition", "4. Rules"]
        for i, step in enumerate(steps):
             # Pill-shaped step indicators
             lbl = tk.Label(self.pipeline_frame, text=step, font=("Segoe UI", 9, "bold"), 
                           bg="#F0F0F0", fg=self.text_secondary,
                           padx=16, pady=6)
             lbl.pack(side="left", padx=12, pady=8)
             self.pipeline_steps[i] = lbl
        
        # Main Layout with Premium Spacing
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=24, pady=16)
        
        # GLASSMORPHISM CONTROL PANEL (iOS-inspired)
        control_panel = tk.Frame(main_frame, bg=self.card_glass, bd=0, relief="flat", 
                                highlightbackground=self.border_light, highlightthickness=1)
        control_panel.pack(side="left", fill="y", padx=(0, 20))
        
        # Panel Header
        tk.Label(control_panel, text="Controls", font=("Segoe UI", 15, "bold"), 
                bg=self.card_glass, fg=self.text_color).pack(pady=18, padx=20)
        
        # iOS-STYLE UPLOAD BUTTON (Secondary)
        self.btn_upload = tk.Button(control_panel, text="📁 Upload Image", 
                                    bg="#F0F0F0", fg=self.text_color,
                                    font=("Segoe UI", 10, "bold"), width=16, 
                                    relief="flat", bd=0, cursor="hand2",
                                    activebackground="#E8E8E8",
                                    padx=16, pady=10,
                                    command=self.upload_image)
        self.btn_upload.pack(pady=6, padx=18)
        
        # iOS-STYLE EXTRACT BUTTON (Primary with gradient effect)
        self.btn_extract = tk.Button(control_panel, text="✨ Extract Text", 
                                     bg=self.primary, fg="white", 
                                     font=("Segoe UI", 11, "bold"), width=16,
                                     relief="flat", bd=0, cursor="hand2",
                                     activebackground="#0051D5",
                                     padx=16, pady=12,
                                     command=self.start_extraction)
        self.btn_extract.pack(pady=10, padx=18)
        
        # Subtle Divider
        tk.Frame(control_panel, height=1, bg=self.border_light).pack(fill="x", pady=14, padx=18)
        
        # iOS-STYLE SUCCESS BUTTON
        self.btn_demo = tk.Button(control_panel, text="🎬 Run Demo", 
                                  bg=self.success, fg="white", 
                                  font=("Segoe UI", 10, "bold"), width=16,
                                  relief="flat", bd=0, cursor="hand2",
                                  activebackground="#28A745",
                                  padx=16, pady=10,
                                  command=self.run_demo)
        self.btn_demo.pack(pady=6, padx=18)
        
        tk.Frame(control_panel, height=1, bg=self.border_light).pack(fill="x", pady=14, padx=18)
        
        # iOS-STYLE TOGGLE SWITCHES (Checkboxes)
        self.safe_mode_var = tk.BooleanVar(value=True)
        self.chk_safe = tk.Checkbutton(control_panel, text="✓ Safe Mode", 
                                       variable=self.safe_mode_var, bg=self.card_glass,
                                       font=("Segoe UI", 10, "bold"), fg=self.text_color,
                                       activebackground=self.card_glass,
                                       selectcolor=self.card_glass)
        self.chk_safe.pack(pady=6, anchor="w", padx=22)
        tk.Label(control_panel, text="Minimal Correction", 
                font=("Segoe UI", 9), bg=self.card_glass, fg=self.text_secondary).pack(anchor="w", padx=22)
        
        self.honesty_var = tk.BooleanVar(value=False)
        self.chk_honest = tk.Checkbutton(control_panel, text="✓ Honesty Filter", 
                                         variable=self.honesty_var, bg=self.card_glass,
                                         font=("Segoe UI", 10, "bold"), fg=self.text_color,
                                         activebackground=self.card_glass,
                                         selectcolor=self.card_glass)
        self.chk_honest.pack(pady=(12, 6), anchor="w", padx=22)
        tk.Label(control_panel, text="Mask low confidence", 
                font=("Segoe UI", 9), bg=self.card_glass, fg=self.text_secondary).pack(anchor="w", padx=22)
        
        tk.Frame(control_panel, height=1, bg=self.border_light).pack(fill="x", pady=14, padx=18)
        
        # iOS-STYLE METRICS PANEL
        tk.Label(control_panel, text="System Metrics", 
                font=("Segoe UI", 12, "bold"), bg=self.card_glass, fg=self.text_color).pack(pady=10)
        
        # Metric Cards
        self.lbl_model_size = tk.Label(control_panel, text="Model: Checking...", 
                                       font=("Segoe UI", 10), bg=self.card_glass, fg=self.text_secondary)
        self.lbl_model_size.pack(pady=3)

        # Highlighted Metric
        self.lbl_params = tk.Label(control_panel, text="Params/Char: ...", 
                                   font=("Segoe UI", 9, "bold"), bg="#FFF4E6", 
                                   fg="#C77700", padx=10, pady=4)
        self.lbl_params.pack(pady=6)
        
        self.lbl_time = tk.Label(control_panel, text="Time: 0ms", 
                                font=("Segoe UI", 10), bg=self.card_glass, fg=self.text_secondary)
        self.lbl_time.pack(pady=3)
        
        # Status at bottom
        self.lbl_status = tk.Label(control_panel, text="• Ready", 
                                  font=("Segoe UI", 10, "italic"), bg=self.card_glass, fg=self.primary)
        self.lbl_status.pack(side="bottom", pady=18)

        # Update Metrics
        size_mb = self.recognizer.get_model_size_mb()
        self.lbl_model_size.config(text=f"Model: {size_mb:.2f} MB")
        
        # Calculate Params/Char (Approx)
        # Size in Bytes / 37 characters
        if size_mb > 0:
            size_bytes = size_mb * 1024 * 1024
            params_per_char_kb = (size_bytes / 37) / 1024
            self.lbl_params.config(text=f"Params/Char: ~{params_per_char_kb:.1f} KB")

        # Column 2: Image Views (Middle)
        image_panel = tk.Frame(main_frame, bg=self.bg_color)
        image_panel.pack(side="left", fill="both", expand=True)
        
        view_frame = tk.Frame(image_panel, bg=self.bg_color)
        view_frame.pack(fill="both", expand=True)
        
        # Original
        frame_orig = tk.LabelFrame(view_frame, text="Original Input", bg=self.bg_color)
        frame_orig.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_image_orig = tk.Label(frame_orig, text="No Image", bg="#e0e0e0")
        self.lbl_image_orig.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Vision
        frame_vision = tk.LabelFrame(view_frame, text="AI Vision (Processed)", bg=self.bg_color)
        frame_vision.pack(side="left", fill="both", expand=True, padx=5)
        self.lbl_image_vision = tk.Label(frame_vision, text="Waiting...", bg="#333", fg="white")
        self.lbl_image_vision.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Column 3: PREMIUM Output Panel
        output_panel = tk.Frame(main_frame, bg=self.card_bg, bd=0, relief="flat",
                               highlightbackground="#E5E7EB", highlightthickness=1, width=320)
        output_panel.pack(side="right", fill="both", padx=(15, 0))
        
        # Green Header for Results
        output_header = tk.Frame(output_panel, bg=self.success, height=45)
        output_header.pack(fill="x")
        output_header.pack_propagate(False)
        tk.Label(output_header, text="📄 Extracted Text", 
                font=("Segoe UI", 13, "bold"), bg=self.success, fg="white").pack(pady=10)
        
        from tkinter import ttk
        
        notebook = ttk.Notebook(output_panel)
        notebook.pack(fill="both", expand=True, pady=(10,5), padx=10)
        
        # Tab 1: Final Output with Better Styling
        self.tab_raw = tk.Frame(notebook, bg=self.card_bg)
        notebook.add(self.tab_raw, text="Final Output")
        self.txt_output = scrolledtext.ScrolledText(self.tab_raw, font=("Segoe UI", 11), 
                                                    width=30, wrap=tk.WORD,
                                                    bg=self.card_bg, fg=self.text_color,
                                                    relief="flat", padx=10, pady=10)
        self.txt_output.pack(fill="both", expand=True)
        
        # Tab 2: Debug
        self.tab_struct = tk.Frame(notebook, bg=self.card_bg)
        notebook.add(self.tab_struct, text="Raw/Debug")
        self.txt_debug = scrolledtext.ScrolledText(self.tab_struct, font=("Consolas", 9), 
                                                   width=30, fg="#6B7280", bg=self.card_bg,
                                                   relief="flat", padx=10, pady=10)
        self.txt_debug.pack(fill="both", expand=True)
        
        # Modern Save Button
        tk.Button(output_panel, text="💾 Save to File", 
                 bg=self.primary, fg="white", font=("Segoe UI", 10, "bold"),
                 relief="flat", bd=0, cursor="hand2",
                 command=self.save_text).pack(pady=10, padx=10, fill="x")

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
        # iOS-style smooth transitions
        for lbl in self.pipeline_steps.values():
             lbl.config(fg=self.text_secondary, bg="#F0F0F0", font=("Segoe UI", 9, "bold"))
        # Highlight active step with iOS blue
        if step_idx in self.pipeline_steps:
             self.pipeline_steps[step_idx].config(fg="white", bg=self.primary, font=("Segoe UI", 9, "bold"))

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
            
            # Use Tesseract to extract text directly from preprocessed image
            extracted_text, confidence = self.recognizer.extract_text_with_layout(binary)
            
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

