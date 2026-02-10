import os
import pytesseract
from PIL import Image
import cv2
import numpy as np

# Configure Tesseract path (system installation)
# pytesseract will auto-detect if installed via winget
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Recognizer:
    def __init__(self):
        """Initialize Tesseract-based recognizer"""
        self.engine_name = "Tesseract OCR v5.4"
        print(f"Loaded {self.engine_name}")
        
    def get_model_size_mb(self):
        """Return approximate size of Tesseract engine + data"""
        # Tesseract binary (~2MB) + eng.traineddata (~4MB)
        return 6.0
        
    def extract_text_from_image(self, image_array):
        """
        Extract text from entire image using Tesseract.
        
        Args:
            image_array: numpy array of preprocessed image
            
        Returns:
            extracted_text: string of recognized text
            confidence: average confidence score (0-1)
        """
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(image_array)
            
            # Use Tesseract to extract text with confidence
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Filter out low-confidence results and build text
            text_parts = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if conf > 0:  # Valid detection
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(conf / 100.0)  # Convert to 0-1 range
            
            # Join text with spaces
            extracted_text = ' '.join(text_parts)
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return extracted_text, avg_confidence
            
        except Exception as e:
            print(f"Tesseract extraction error: {e}")
            return "", 0.0
    
    def extract_text_with_layout(self, image_array, lang='eng'):
        """
        Extract text preserving layout (line breaks).
        
        Args:
            image_array: numpy array of preprocessed image
            lang: language code (e.g., 'eng', 'hin', 'eng+hin' for multiple)
            
        Returns:
            extracted_text: string with preserved layout
            confidence: average confidence score
        """
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(image_array)
            
            # Use Tesseract to extract text with layout and specified language
            text = pytesseract.image_to_string(pil_image, lang=lang)
            
            # Get confidence data
            data = pytesseract.image_to_data(pil_image, lang=lang, output_type=pytesseract.Output.DICT)
            confidences = [c / 100.0 for c in data['conf'] if c > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return text.strip(), avg_confidence
            
        except Exception as e:
            print(f"Tesseract extraction error: {e}")
            return "", 0.0
