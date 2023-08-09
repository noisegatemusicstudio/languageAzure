import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def read_qr_code(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    preprocessing_methods = [
        lambda img: cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        lambda img: cv2.adaptiveThreshold(cv2.GaussianBlur(img, (9, 9), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        lambda img: cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        lambda img: cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]
    ]

    for preprocess in preprocessing_methods:
        processed_image = preprocess(gray)
        qr_code_detector = cv2.QRCodeDetector()
        decoded_info, points, _ = qr_code_detector.detectAndDecode(processed_image)

        if points is not None:
            print("QR Code Detected!")
            print("Decoded Information:", decoded_info)
            points = np.int32(points.reshape(-1, 2))
            cv2.polylines(image, [points], True, (0, 255, 0), 2)
            cv2.imshow("QR Code Detection", image)
            print("Press any key to close the image display/Wait for 5 seconds")
            cv2.waitKey(5000)
            cv2.destroyAllWindows()
            return

    print("No QR code detected.")

def upload_and_read():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        read_qr_code(file_path)
    else:
        print("No file selected.")

upload_and_read()
