import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread(
    r"D:\DEV HOUSE\Pyhton\CAPTCHA\captcha.png"
)

if img is None:
    print("Image not found")
    exit()

# -----------------------------------
# Show original
# -----------------------------------
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()

# -----------------------------------
# Crop white margins
# -----------------------------------
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

mask_text = gray < 245

coords = np.column_stack(np.where(mask_text))

y1, x1 = coords.min(axis=0)
y2, x2 = coords.max(axis=0)

crop = img[y1:y2+1, x1:x2+1]

plt.imshow(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()

# -----------------------------------
# HSV RED DETECTION
# -----------------------------------
hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

lower1 = np.array([0, 50, 50])
upper1 = np.array([15, 255, 255])

lower2 = np.array([160, 50, 50])
upper2 = np.array([180, 255, 255])

mask1 = cv2.inRange(hsv, lower1, upper1)
mask2 = cv2.inRange(hsv, lower2, upper2)

mask = cv2.bitwise_or(mask1, mask2)

plt.imshow(mask, cmap="gray")
plt.axis("off")
plt.show()

# -----------------------------------
# Morphology
# -----------------------------------
kernel = np.ones((2,2), np.uint8)

clean = cv2.morphologyEx(
    mask,
    cv2.MORPH_CLOSE,
    kernel,
    iterations=1
)

clean = cv2.dilate(
    clean,
    kernel,
    iterations=1
)

plt.imshow(clean, cmap="gray")
plt.axis("off")
plt.show()

# -----------------------------------
# Contours
# -----------------------------------
contours, _ = cv2.findContours(
    clean,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

img2 = crop.copy()

for i, c in enumerate(contours):

    x, y, w, h = cv2.boundingRect(c)

    if w < 3 or h < 3:
        continue

    cv2.rectangle(
        img2,
        (x, y),
        (x+w, y+h),
        (0,255,0),
        1
    )

plt.imshow(cv2.cvtColor(img2,
                         cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()

print("Contours:", len(contours))