import os
import json
from PIL import Image, ImageEnhance, ImageFilter

def enhance_image(img_path):
    if not os.path.exists(img_path):
        return False
    
    try:
        with Image.open(img_path) as img:
            img = img.convert('RGB')
            w, h = img.size
            
            # Upscale if too small for high-DPI displays
            target_min_dim = 600
            if min(w, h) < target_min_dim:
                scale = target_min_dim / min(w, h)
                new_w, new_h = int(w * scale), int(h * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # 1. Unsharp Mask for fine architectural & detail sharpening
            unsharp = img.filter(ImageFilter.UnsharpMask(radius=1.8, percent=140, threshold=2))
            
            # 2. Sharpening filter
            enhancer_sharp = ImageEnhance.Sharpness(unsharp)
            img_sharp = enhancer_sharp.enhance(1.35)
            
            # 3. Contrast adjustment for clarity and removing haziness
            enhancer_contrast = ImageEnhance.Contrast(img_sharp)
            img_contrast = enhancer_contrast.enhance(1.08)
            
            # 4. Color saturation vibrancy
            enhancer_color = ImageEnhance.Color(img_contrast)
            img_final = enhancer_color.enhance(1.06)
            
            # Save in high quality JPEG
            img_final.save(img_path, 'JPEG', quality=95, subsampling=0, optimize=True)
            return True
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return False

def main():
    hotels_file = 'data/hotels.json'
    with open(hotels_file, 'r', encoding='utf-8') as f:
        hotels = json.load(f)
    
    print(f"Enhancing clarity for {len(hotels)} hotel images...")
    
    for h in hotels:
        filename = h.get('image_filename')
        if not filename:
            continue
        
        static_p = os.path.join('static/images', filename)
        root_p = os.path.join('images', filename)
        
        ok1 = enhance_image(static_p)
        ok2 = enhance_image(root_p)
        
        print(f"  [OK] Enhanced clarity for {h['name']} ({filename})")

if __name__ == '__main__':
    main()
