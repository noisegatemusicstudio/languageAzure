import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def read_qr_code(image_path):
    # Read the image file
    image = cv2.imread(image_path)

    # Initialize the QRCodeDetector
    qr_code_detector = cv2.QRCodeDetector()

    # Detect and decode the QR code
    decoded_info, points, _ = qr_code_detector.detectAndDecode(image)

    if points is not None:
        # If a QR code is detected, print the decoded information
        print("QR Code Detected!")
        print("Decoded Information:", decoded_info)

        # Draw a bounding box around the detected QR code
        points = np.int32(points.reshape(-1, 2))
        cv2.polylines(image, [points], True, (0, 255, 0), 2)

        # Display the image with the bounding box (optional)
        cv2.imshow("QR Code Detection", image)
        cv2.waitKey(5000) # Wait for 5 seconds or a key press
        cv2.destroyAllWindows()

    else:
        print("No QR code detected.")

def upload_and_read():
    root = tk.Tk()
    root.withdraw() # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        read_qr_code(file_path)
    else:
        print("No file selected.")

# Example usage
upload_and_read()
