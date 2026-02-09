from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image():
    # Create white image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load Arial (standard windows font)
    try:
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 40)
            small_font = ImageFont.truetype(font_path, 24)
        else:
             # Fallback
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        
    # Text to write
    text_lines = [
        "TINY WORLD AI OCR",
        "HELLO JUDGES",
        "THIS IS A TEST 12345",
        "THE QUICK BROWN FOX",
        "JUMPS OVER THE DOG",
        "ABCDEFGHIJKLM",
        "NOPQRSTUVWXYZ",
        "0123456789"
    ]
    
    y = 50
    for line in text_lines:
        # Draw text in black
        w, h = draw.textsize(line, font=font) if hasattr(draw, "textsize") else (200, 40)
        x = (width - w) // 2
        
        draw.text((x, y), line, font=font, fill='black')
        y += h + 20 # Add line spacing
        
    output_path = "ideal_test_image.png"
    img.save(output_path)
    print(f"Test image saved to {output_path}")

if __name__ == "__main__":
    create_test_image()
