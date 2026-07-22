import cv2
import easyocr

reader = easyocr.Reader(['en'], gpu=False)

def solve_captcha(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found.")
        return

    green = img[:, :, 1]
    _, thresh = cv2.threshold(green, 180, 255, cv2.THRESH_BINARY)
    thresh = cv2.medianBlur(thresh, 3)
    scaled = cv2.resize(thresh, None, fx=5, fy=5, interpolation=cv2.INTER_LINEAR)

    results = reader.readtext(scaled, detail=0)
    if results:
        word = results[0].strip().lower()
        print(f"Extracted Text: {word}")
        return word
    print("No text found.")

if __name__ == "__main__":
    solve_captcha(r"D:\DEV HOUSE\Pyhton\CAPTCHA\Captcha (1).jfif")