import cv2
import numpy as np

def to_grayscale(image):
    """Converts image to grayscale if not already."""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def denoise(image):
    """Applies Gaussian Blur to remove noise."""
    return cv2.GaussianBlur(image, (5, 5), 0)

def binarize(image):
    """
    Applies Adaptive Thresholding and ensures white text on black background.
    """
    # 1. Speckle removal (Vital for textured backgrounds)
    image = cv2.medianBlur(image, 3)
    
    # 2. Otsu's Binarization (Better for solid text/screenshots)
    # This automatically finds the best threshold and keeps text solid (not hollow)
    ret, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 3. Smart Inversion (Border-aware)
    # Check average intensity of the 2px border
    h, w = thresh.shape
    border_pixels = []
    border_pixels.append(thresh[0:2, :]) # Top
    border_pixels.append(thresh[h-2:h, :]) # Bottom
    border_pixels.append(thresh[:, 0:2]) # Left
    border_pixels.append(thresh[:, w-2:w]) # Right
    
    avg_border = np.mean([np.mean(b) for b in border_pixels])
    
    # If border is mostly white (background), invert to get white-on-black text
    if avg_border > 127:
        return cv2.bitwise_not(thresh)
    else:
        return thresh

def preprocess_image(image_path=None, image_array=None):
    """
    Main preprocessing pipeline.
    Args:
        image_path: Path to image file
        image_array: numpy array of image (if already loaded)
    Returns:
        processed_image: Binary image ready for segmentation
        original_image: The loaded original image (for display)
    """
    if image_array is not None:
        img = image_array
    elif image_path:
        img = cv2.imread(image_path)
    else:
        raise ValueError("No image provided")

    if img is None:
        raise ValueError("Could not load image")
    
    # Step 1: Image Input & Normalization
    # Resize max width <= 800 px (maintain aspect ratio)
    h, w = img.shape[:2]
    if w > 800:
        scale = 800 / w
        new_h = int(h * scale)
        img = cv2.resize(img, (800, new_h))
        
    gray = to_grayscale(img)
    
    # Apply Gaussian blur to remove camera noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Step 2: Contrast Enhancement
    # Apply adaptive histogram equalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    
    # Step 3: Binarization
    binary = binarize(enhanced)
    
    # Step 3: Deskewing (New)
    angle = get_skew_angle(binary)
    if abs(angle) > 0.5:
        binary = rotate_image(binary, angle)
        # Also rotate the original debug image so they match
        img = rotate_image(img, angle)
    
    # Step 4: Morphological cleaning
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    return binary, img

def get_skew_angle(image):
    """
    Calculate skew angle of an image using minimum area rectangle.
    """
    # Find all white pixels
    coords = np.column_stack(np.where(image > 0))
    
    # If no text found, return 0
    if len(coords) < 10:
        return 0
        
    # Get minimum area rectangle
    angle = cv2.minAreaRect(coords)[-1]
    
    # Correct the angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    return angle

def rotate_image(image, angle):
    """
    Rotate the image around its center.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
