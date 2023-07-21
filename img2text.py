
from PIL import Image
import io
import os

import streamlit as st

# from app import generate_colors
# from oauth2client.service_account import ServiceAccountCredentials
from google.cloud import vision_v1
from google.cloud.vision_v1 import types

import pytesseract


SERVICE_ACCOUNT_FILE = 'service/quickstart.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_FILE

# Set the path to the Tesseract executable (change this to your installation path)
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

st.title("JPEG to Text Converter")


def pil_image_to_gcv_image(pil_image):
    # Create a byte stream from the PIL image
    image_byte_array = io.BytesIO()
    pil_image.save(image_byte_array, format='JPEG')
    image_byte_array.seek(0)
    image_content = image_byte_array.read()

    # Create a types.Image object
    gcv_image = types.Image(content=image_content)

    return gcv_image

def extract_text_from_image(image):
    try:
        # Create a client and specify the image to analyze
        client = vision_v1.ImageAnnotatorClient()

        # Perform OCR on the image
        response = client.text_detection(image=image)
        extracted_text = response.text_annotations[0].description if response.text_annotations else None

        return extracted_text
    except Exception as e:
        print("Error:", e)
        return None

# Input JPEG image
image_file = st.file_uploader("JPEG Dosyasını YÜKLE", type=["jpeg", "jpg"]) 

if image_file is not None:
    # Read JPEG with OpenCV
    # Load image with PIL
    _img = Image.open(image_file) 
    st.image(_img)
    
    gcv_image = pil_image_to_gcv_image(_img)
   
    extracted_text = extract_text_from_image(gcv_image)
    st.header('Extracted text with google:')
    st.write(f' {extracted_text}')
    
    
    extracted_text2 = pytesseract.image_to_string(_img)
    st.header('Extracted text with pytesseract:')
    st.write(f'{extracted_text2}')

    
 
   