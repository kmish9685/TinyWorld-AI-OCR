
import sys
import os
sys.path.append(os.getcwd())

try:
    from src.ui import OCRApp
    print(f"OCRApp imported successfully.")
    if hasattr(OCRApp, 'save_text'):
        print("SUCCESS: OCRApp has save_text method.")
    else:
        print("FAILURE: OCRApp is missing save_text method.")
        print(f"Dir: {dir(OCRApp)}")
except Exception as e:
    print(f"Error: {e}")
