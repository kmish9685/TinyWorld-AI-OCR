"""
Model Size Calculator for TinyWorld AI OCR
Shows judges exactly what counts as "model size" and how it's calculated
"""

import os
import sys

def get_file_size_mb(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0

def get_dir_size_mb(dirpath):
    """Get directory size in MB"""
    total = 0
    if os.path.exists(dirpath):
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    return total / (1024 * 1024)

def show_model_size():
    """
    Calculate and display model size breakdown
    """
    print("=" * 70)
    print("🎯 TinyWorld AI - MODEL SIZE BREAKDOWN")
    print("=" * 70)
    print()
    
    # Find Tesseract installation
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        "/usr/share/tesseract-ocr",
        "/usr/local/share/tessdata"
    ]
    
    tesseract_path = None
    for path in tesseract_paths:
        if os.path.exists(path):
            tesseract_path = path
            break
    
    print("📊 MODEL COMPONENTS:")
    print("-" * 70)
    
    # 1. Core Python Code (our implementation)
    src_size = get_dir_size_mb("src")
    print(f"1. Our Code (src/)                    : {src_size:.2f} MB")
    print(f"   - preprocess.py, recognize.py, ui.py, etc.")
    
    # 2. Tesseract OCR Engine
    if tesseract_path:
        tessdata_path = os.path.join(tesseract_path, "tessdata")
        
        # English model (required)
        eng_traineddata = os.path.join(tessdata_path, "eng.traineddata")
        eng_size = get_file_size_mb(eng_traineddata)
        
        print(f"\n2. Tesseract OCR Engine (English)     : {eng_size:.2f} MB")
        print(f"   - Location: {eng_traineddata}")
        print(f"   - This is the core OCR model")
        
        # Additional language models (if installed)
        print(f"\n3. Additional Language Models:")
        lang_files = ['hin', 'ara', 'fra', 'spa', 'deu', 'chi_sim', 'san', 'urd']
        total_lang_size = 0
        
        for lang in lang_files:
            lang_file = os.path.join(tessdata_path, f"{lang}.traineddata")
            lang_size = get_file_size_mb(lang_file)
            if lang_size > 0:
                total_lang_size += lang_size
                lang_name = {
                    'hin': 'Hindi', 'ara': 'Arabic', 'fra': 'French',
                    'spa': 'Spanish', 'deu': 'German', 'chi_sim': 'Chinese',
                    'san': 'Sanskrit', 'urd': 'Urdu'
                }.get(lang, lang)
                print(f"   - {lang_name:15} : {lang_size:.2f} MB")
        
        if total_lang_size == 0:
            print(f"   - None installed (optional)")
        
        print()
        print("=" * 70)
        print("📈 TOTAL MODEL SIZE CALCULATION:")
        print("=" * 70)
        
        # Total calculation
        total_model_size = eng_size  # Core model (English only)
        total_with_langs = eng_size + total_lang_size  # With all languages
        
        print(f"\n✅ CORE MODEL (English only)          : {total_model_size:.2f} MB")
        print(f"   - This is what counts for competition!")
        print(f"   - Calculation: Tesseract English model")
        
        if total_lang_size > 0:
            print(f"\n📦 WITH ALL LANGUAGES (Optional)      : {total_with_langs:.2f} MB")
            print(f"   - English + {len([l for l in lang_files if get_file_size_mb(os.path.join(tessdata_path, f'{l}.traineddata')) > 0])} additional languages")
        
        print(f"\n💻 OUR CODE SIZE                      : {src_size:.2f} MB")
        print(f"   - Pure Python implementation")
        print(f"   - Preprocessing, UI, post-processing")
        
        print()
        print("=" * 70)
        print("🎯 FOR JUDGES:")
        print("=" * 70)
        print(f"""
The MODEL SIZE is: {total_model_size:.2f} MB (Tesseract English model)

WHY THIS SIZE?
- Tesseract is a pre-trained OCR engine (not trained by us)
- We use it as a library/dependency
- Our contribution is the preprocessing, UI, and post-processing
- Model size = Size of the OCR engine we're using

COMPARISON:
- Google Cloud Vision API: Cloud-based (GB-sized models)
- Azure OCR: Cloud-based (GB-sized models)
- Our solution: {total_model_size:.2f} MB offline model

CALCULATION METHOD:
1. Locate Tesseract installation: {tesseract_path}
2. Find English model: eng.traineddata
3. Check file size: {total_model_size:.2f} MB
4. This is the core OCR model size
        """)
        
    else:
        print("❌ Tesseract not found!")
        print("   Please install Tesseract OCR first")
        print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    print()
    print("=" * 70)
    print("📝 TO SHOW JUDGES:")
    print("=" * 70)
    print("""
1. Run this script: python show_model_size.py
2. Show the output above
3. Navigate to Tesseract folder and show eng.traineddata file
4. Right-click → Properties → Size
5. This proves the model size calculation!
    """)
    print("=" * 70)

if __name__ == "__main__":
    show_model_size()
