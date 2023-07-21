
from PIL import Image
import streamlit as st
import numpy as np 
import cv2
from app import generate_colors

import pytesseract

# Set the path to the Tesseract executable (change this to your installation path)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

st.title("JPEG to 3D Printable File Converter")

# Input JPEG image
image_file = st.file_uploader("JPEG Dosyasını YÜKLE", type=["jpeg", "jpg"]) 

if image_file is not None:
    # Read JPEG with OpenCV
    # Load image with PIL
    _img = Image.open(image_file) 
    
    extracted_text = pytesseract.image_to_string(_img)
    print('Extracted text', extracted_text)
    st.image(_img)
    st.write(extracted_text)
    # Convert to NumPy array
    img_array = np.asarray(_img)  

    # Convert RGB to BGR for OpenCV
    img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR) 
    # Get unique colors
    _, _, unique_colors = generate_colors(img)
    
    st.write('Base colors..')
    for color in unique_colors:
        # Display the color as a 15x15 colored box
        st.image(Image.fromarray(np.tile(color, (25, 25, 1)).astype(np.uint8)), caption='', width=40, use_column_width=False)
    st.write(unique_colors)
   