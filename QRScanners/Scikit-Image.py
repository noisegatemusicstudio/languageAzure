from pyzbar.pyzbar import decode
from skimage import filters, img_as_ubyte, exposure
from skimage.color import rgb2gray
from skimage.morphology import erosion, dilation, disk
from skimage.feature import canny
from skimage.filters import threshold_local
import numpy as np
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def read_qr_code(image_path):
    image = plt.imread(image_path)

    # Check the number of channels in the image
    num_channels = image.shape[2] if len(image.shape) == 3 else 1

    # If the image has 4 channels (such as an RGBA image), only take the first 3 channels
    if num_channels == 4:
        image = image[..., :3]

    # Convert to grayscale if the image is not already grayscale
    gray = rgb2gray(image) if num_channels >= 3 else image
    gray_ubyte = img_as_ubyte(gray)

    preprocessing_methods = [
        lambda img: img_as_ubyte(filters.gaussian(img, sigma=1)),
        lambda img: img_as_ubyte(filters.median(img)),
        lambda img: img_as_ubyte(filters.sobel(img)),
        lambda img: img_as_ubyte(img > threshold_local(img, 51, method='gaussian')),
        lambda img: img_as_ubyte(exposure.equalize_hist(img)),
        lambda img: img_as_ubyte(exposure.adjust_log(img)),
        lambda img: img_as_ubyte(exposure.adjust_sigmoid(img)),
        lambda img: img_as_ubyte(canny(img)),
        lambda img: img_as_ubyte(dilation(erosion(img))),
        lambda img: img_as_ubyte(filters.rank.enhance_contrast(img, disk(5)))
    ]

    for preprocess in preprocessing_methods:
        processed_image = preprocess(gray_ubyte)
        decoded_objects = decode(processed_image)

        for obj in decoded_objects:
            print("QR Code Detected!")
            print("Decoded Information:", obj.data.decode('utf-8'))

            # Draw the bounding box (optional)
            if len(obj.polygon) == 4:
                fig, ax = plt.subplots(1)
                ax.imshow(image)
                poly = patches.Polygon(obj.polygon, edgecolor='r', facecolor="none")
                ax.add_patch(poly)

            # Display the image with the bounding box (optional)
            plt.show(block=False)  # Display without blocking
            plt.pause(2)  # Pause for 2 seconds
            plt.close()  # Close the figure
            return

    print("No QR code detected.")

def upload_and_read():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
    if file_path:
        read_qr_code(file_path)
    else:
        print("No file selected.")

upload_and_read()
