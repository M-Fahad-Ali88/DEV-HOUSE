import pytesseract
from PIL import Image

# If tesseract is not in PATH, uncomment and set your path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = Image.open('test.png')  # create a simple PNG with text
print(pytesseract.image_to_string(img))