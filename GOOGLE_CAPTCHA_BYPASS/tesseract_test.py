import pytesseract
from PIL import Image, ImageDraw

# Uncomment and set your path if needed:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = Image.new('RGB', (200, 50), 'white')
draw = ImageDraw.Draw(img)
draw.text((10, 10), "ABCD1234", fill='black')
img.save('test.png')
text = pytesseract.image_to_string(Image.open('test.png'))
print(f"OCR result: '{text}'")