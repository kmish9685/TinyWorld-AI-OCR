from PIL import Image, ImageDraw, ImageFont
import os

def create_demo_image():
    # Create white image
    img = Image.new('RGB', (800, 600), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Try to load a default font, otherwise default
    try:
        font = ImageFont.truetype("arial.ttf", 36)
        # Make the small font a bit bigger and use uppercase logic
        small_font = ImageFont.truetype("arial.ttf", 28)
    except IOError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        
    # Add text - USING UPPERCASE to help the tiny model
    # The model seems to struggle with small lowercase letters
    d.text((50, 50), "TINYWORLD OCR", fill=(0,0,0), font=font)
    d.text((50, 120), "1. WORKS OFFLINE", fill=(0,0,0), font=small_font)
    d.text((50, 170), "2. LOW MEMORY USAGE", fill=(0,0,0), font=small_font)
    d.text((50, 220), "3. NO CLOUD API NEEDED", fill=(0,0,0), font=small_font)
    d.text((50, 320), "HELLO WORLD 123", fill=(0,0,0), font=font)
    
    # Save
    img.save("demo_image.png")
    print("demo_image.png created successfully (Optimized for Uppercase).")

if __name__ == "__main__":
    create_demo_image()
