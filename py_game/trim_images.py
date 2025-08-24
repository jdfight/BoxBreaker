from PIL import Image
import os

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "res", "pixmaps")

for filename in os.listdir(IMAGE_DIR):
    if filename.endswith(".png"):
        filepath = os.path.join(IMAGE_DIR, filename)
        try:
            image = Image.open(filepath)
            image = image.convert("RGBA")
            bbox = image.getbbox()
            if bbox:
                trimmed_image = image.crop(bbox)
                trimmed_image.save(filepath)
                print(f"Trimmed {filename}")
        except Exception as e:
            print(f"Failed to trim {filename}: {e}")
