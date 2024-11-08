import easyocr
import re
import os
import cv2

def extract_npk_from_image(image_path):
    # Initialize the EasyOCR reader with the English language
    reader = easyocr.Reader(['en'], gpu=True)

    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Check if the image is horizontal (wider than it is tall)
    height, width = image.shape[:2]
    if width > height:
        # Rotate the image to make it vertical
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    # Save the rotated image temporarily to use with EasyOCR
    temp_image_path = 'temp_rotated_image.jpg'
    cv2.imwrite(temp_image_path, image)

    # Perform OCR on the image
    result = reader.readtext(temp_image_path, detail=0)

    # Combine the text into one string
    full_text = ' '.join(result)

    # Find NPK pattern (e.g., 30-10-10)
    match = re.search(r'\b(\d+)-(\d+)-(\d+)\b', full_text)
    if match:
        n, p, k = match.groups()
        return int(n), int(p), int(k)
    else:
        return None  # No NPK pattern found

# Directory path to your images
image_dir = r'C:\Users\mdtnd\OneDrive\Desktop\work\Fertilizer Bag Analyzer\images'

# Loop through and extract NPK
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        file_path = os.path.join(image_dir, filename)
        print(f"Processing {filename}...")
        npk_values = extract_npk_from_image(file_path)
        if npk_values:
            n, p, k = npk_values
            print(f"  NPK values: N={n}%, P={p}%, K={k}%")
        else:
            print("  No NPK values found.")
