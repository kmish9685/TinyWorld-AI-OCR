import os
import pickle
import numpy as np
import string
import glob
from PIL import Image, ImageDraw, ImageFont
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import cv2

# Config
DATA_DIR = "data"
MODEL_PATH = os.path.join(DATA_DIR, "char_model.pkl")
IMG_SIZE = 28  
SAMPLES_PER_CHAR = 100 # Balanced for speed/quality

def get_system_fonts():
    """Scans Windows font directory for TTF files."""
    font_dir = "C:\\Windows\\Fonts"
    fonts = glob.glob(os.path.join(font_dir, "*.ttf"))
    # Also check local folder if any
    fonts += glob.glob("fonts/*.ttf")
    
    # Filter out symbol fonts if possible
    valid_fonts = [f for f in fonts if "wingding" not in f.lower() and "symbol" not in f.lower()]
    return valid_fonts

def apply_augmentation(img_np):
    """
    Apply realistic destructive noise (like a bad screenshot).
    """
    h, w = img_np.shape[:2]
    
    # 1. Random Rotation (-5 to +5)
    angle = np.random.uniform(-5, 5)
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
    img_np = cv2.warpAffine(img_np, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)
    
    # 2. Blur (Simulate out of focus)
    if np.random.rand() > 0.5:
        k = np.random.choice([3, 5])
        img_np = cv2.GaussianBlur(img_np, (k, k), 0)
        
    # 3. Erosion/Dilation (Simulate ink spread or fade)
    if np.random.rand() > 0.5:
        kernel = np.ones((2,2), np.uint8)
        if np.random.rand() > 0.5:
            img_np = cv2.erode(img_np, kernel, iterations=1)
        else:
            img_np = cv2.dilate(img_np, kernel, iterations=1)
            
    # 4. Salt and Pepper Noise
    if np.random.rand() > 0.3:
        noise = np.random.randint(0, 50, img_np.shape)
        img_np = cv2.add(img_np, noise.astype(np.uint8))
        
    return img_np

def resize_and_pad_high_res(roi):
    h, w = roi.shape[:2]
    if h == 0 or w == 0: return None
    
    # Scale to fit in 24x24 box
    scale = 24.0 / max(h, w)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    
    resized = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    canvas = np.zeros((IMG_SIZE, IMG_SIZE), dtype="uint8")
    x_off = (IMG_SIZE - new_w) // 2
    y_off = (IMG_SIZE - new_h) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
    
    return canvas

def generate_data():
    print("Finding system fonts...")
    font_paths = get_system_fonts()
    print(f"Found {len(font_paths)} fonts.")
    
    # Load fonts (limit to 60 to keep generation time reasonable, priority to standard ones)
    priority_fonts = ["arial", "times", "segoe", "calibri", "verdana", "tahoma", "comic"]
    
    selected_fonts = []
    
    def load_font(path):
        try: return ImageFont.truetype(path, 32)
        except: return None

    # Load priority first
    for p in priority_fonts:
        for f in font_paths:
            if p in f.lower():
                ft = load_font(f)
                if ft: selected_fonts.append(ft)
                
    # Fill rest with random
    import random
    random.shuffle(font_paths)
    for f in font_paths:
        if len(selected_fonts) > 60: break
        ft = load_font(f)
        if ft: selected_fonts.append(ft)
        
    print(f"Generating data using {len(selected_fonts)} fonts...")
    
    chars = string.ascii_uppercase + string.digits + " .,"
    X = []
    y = []
    
    count = 0
    total_samples = len(chars) * len(selected_fonts) * SAMPLES_PER_CHAR
    print(f"Targeting ~{total_samples} samples.")

    for char in chars:
        for font in selected_fonts:
            for _ in range(SAMPLES_PER_CHAR):
                img = Image.new('L', (48, 48), color=0)
                draw = ImageDraw.Draw(img)
                try: w, h = draw.textsize(char, font=font)
                except: 
                    bbox = draw.textbbox((0,0), char, font=font)
                    w, h = bbox[2], bbox[3]
                
                # Center roughly
                draw.text(((48-w)//2, (48-h)//2), char, font=font, fill=255)
                
                img_np = np.array(img)
                
                # Augment!
                img_np = apply_augmentation(img_np)
                
                # Find tight box
                coords = cv2.findNonZero(img_np)
                if coords is not None:
                    bx, by, bw, bh = cv2.boundingRect(coords)
                    roi = img_np[by:by+bh, bx:bx+bw]
                    processed = resize_and_pad_high_res(roi)
                    if processed is not None:
                        X.append(processed.flatten() / 255.0)
                        y.append(char)
                        count += 1
                        if count % 5000 == 0:
                            print(f"Generated {count} samples...")

    return np.array(X), np.array(y)

def train():
    os.makedirs(DATA_DIR, exist_ok=True)
    abs_model_path = os.path.abspath(MODEL_PATH)
    print(f"Target Model Path: {abs_model_path}")
    
    X, y = generate_data()
    
    # Cast X to float32 to save memory and ensure type safety
    X = X.astype(np.float32)
    
    print(f"Total dataset size: {len(X)}")
    
    # Encode labels to integers
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.1, random_state=42)
    
    print("Training MLPClassifier (Neural Network)...")
    model = MLPClassifier(hidden_layer_sizes=(512, 256), 
                          activation='relu', 
                          solver='adam', 
                          alpha=0.0001, 
                          batch_size=256, 
                          learning_rate='adaptive', 
                          max_iter=500, 
                          early_stopping=True, 
                          verbose=True, 
                          # warm_start=True, # Could help if we looped, but for now just fit
                          random_state=42)
                          
    model.fit(X_train, y_train)
    
    acc = model.score(X_test, y_test)
    print(f"Neural Network Accuracy: {acc * 100:.2f}%")
    
    try:
        print(f"Saving model to {abs_model_path}...")
        if os.path.exists(abs_model_path):
            os.remove(abs_model_path) # Force remove old
            
        # Attach the class mapping to the model so recognize.py can decode
        model.custom_classes_ = le.classes_
        
        with open(abs_model_path, 'wb') as f:
            pickle.dump(model, f)
        print("Model saved successfully.")
    except Exception as e:
        print(f"FAILED TO SAVE MODEL: {e}")
    
    if os.path.exists(abs_model_path):
        size_mb = os.path.getsize(abs_model_path) / (1024 * 1024)
        print(f"Verified File Size: {size_mb:.2f} MB")
    else:
        print("CRITICAL: File does not exist after save!")

if __name__ == "__main__":
    train()
