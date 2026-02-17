
from PIL import Image, ImageDraw, ImageFont
import os

def create_evidence_image():
    # Create a 800x600 image with a dark background
    img = Image.new('RGB', (800, 600), color=(50, 50, 50))
    d = ImageDraw.Draw(img)
    
    # Draw some "Network Traffic" lines
    for i in range(0, 600, 40):
        d.line([(0, i), (800, i)], fill=(60, 60, 60), width=1)
    for i in range(0, 800, 40):
        d.line([(i, 0), (i, 600)], fill=(60, 60, 60), width=1)
        
    # Add text simulating a "Suspicious Screenshot"
    d.text((50, 50), "EVIDENCE FILE: #99281", fill=(255, 0, 0))
    d.text((50, 80), "Source IP: 192.168.1.105 (Suspicious)", fill=(0, 255, 0))
    d.text((50, 110), "Target: Core Database", fill=(0, 255, 0))
    
    # Save it
    path = os.path.abspath("evidence.png")
    img.save(path)
    print(f"Created evidence at: {path}")

if __name__ == "__main__":
    create_evidence_image()
