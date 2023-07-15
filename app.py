import os
import numpy as np

from stl import mesh
from PIL import Image
from sklearn.cluster import KMeans
from scipy.spatial import distance

import streamlit as st 

from tools.tools import load_env

path = "data/files"
file = ""
load_env()

n_main_colors = 5
main_colors = []
heights = {}

def download_file(fn):
    with open(f"data/stl/{fn}", 'rb') as file:
        contents = file.read()
        st.sidebar.download_button(
            label="Yüklemek için tıklayınız",
            data=contents,
            file_name=fn,
            mime='text/plain'        )
    
def generate_colors(image):
    pixel_values = np.array(image)
    n_pixels = pixel_values.shape[0] * pixel_values.shape[1]
    reshaped_pixels = pixel_values.reshape(n_pixels, 3)
    
    kmeans = KMeans(n_clusters=n_main_colors, random_state=0).fit(reshaped_pixels)
    main_colors = kmeans.cluster_centers_.astype(int)
    converted_pixels = main_colors[kmeans.labels_]
    converted_pixels = converted_pixels.reshape(pixel_values.shape)
    
    
    
    return pixel_values, converted_pixels, main_colors


def calculate_height_based_on_color(color, main_colors, heights):
    # Convert the color to a string representation
    conv_color = str(color)

    # Check if the converted color exists in the main_colors array
    if conv_color in main_colors:
        # Retrieve the height value from the heights dictionary
        return heights[conv_color]
    else:
        # Find the closest color to the available colors
        distances = [distance.euclidean(color, c) for c in main_colors]

        closest_color_index = np.argmin(distances)

        closest_color = main_colors[closest_color_index]
 

        # Convert the closest color to its string representation
        conv_closest_color = str(closest_color)

        # Retrieve the height value from the heights dictionary for the closest color
        return heights[conv_closest_color]
    

def calculate_stl(pixel_values, main_colors, heights, step):
    vertices = []
    faces = []

    for i in range(0, pixel_values.shape[0], step):
        for j in range(0, pixel_values.shape[1], step):
            color = tuple(pixel_values[i][j])
            height = calculate_height_based_on_color(color, main_colors, heights)
            vertices.append([i, j, height])

            if i > 0 and j > 0:
                faces.append([len(vertices) - 1, len(vertices) - 2, len(vertices) - pixel_values.shape[1]//step - 2])
            if i > 0 and j < pixel_values.shape[1] - 1:
                faces.append([len(vertices) - 1, len(vertices) - pixel_values.shape[1]//step - 2, len(vertices) - pixel_values.shape[1]//step - 1])

    stl_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            stl_mesh.vectors[i][j] = vertices[face[j] // step]

    filename = file.name.replace('jpeg', 'stl')
    stl_file_path = f"data/stl/{filename}"
    stl_mesh.save(stl_file_path)
    print('Bitti...')
    st.experimental_rerun()
    
def main():
    global file, n_main_colors, main_colors, heights, step
    with st.sidebar: 
        file = st.file_uploader('Dosyayı sürükleyin yada yükleyin', type=["jpeg"], help='Stl ye çevrilecek dosyayı yükleyin')
        n_main_colors = st.slider('Renk sayısı', 1,5,5,1)
        step = st.slider('Mesh sıklığı (pixel)', 1,10,1,1)
        
        file_list = os.listdir(path=path.replace('files', 'stl'))
         # Display chat titles and delete icons
        st.write('Oluşturulan STL dosyası:')
        reversed_keys = reversed(list(file_list))
        for fn in reversed_keys:
            empt = st.empty()
            col1, col2, col3 = empt.columns([6, 2, 2])
            if col1.button(fn, key = f"title{fn}" ):
                print(f'File name : {fn}')
                    
            if col2.button("❌", key = f"del{fn}"):
                st.session_state['delete'] = fn
                                    
            if col3.button('📥', key = f"edit{fn}"):
                download_file(fn)
                    # Check if we're in editing mode for this chat
            if 'delete' in st.session_state and st.session_state['delete'] == fn:
                if st.button(f'Eminmisiniz... \n\n{fn}?', key="custom_button"):
                    # Store the id of the chat we're deleting
                    print(f'Delete chat is {fn}')
                    os.remove(f"data/stl/{fn}")
                    del file_list[file_list.index(fn)]
                    del st.session_state['delete']  # Exit delete mode after confirmation
                    
                else:
                    print(f'Waiting for confirmation to delete chat {fn}')
               
    
    if file:
        image = Image.open(file) 
        # Convert RGBA image to RGB mode
        image = image.convert('RGB')
        ratio = image.size[0] / image.size[1]
        new_width = 518
        new_height = int(new_width / ratio)
        image = image.resize((new_width, new_height))
        image.save(f'{path}/{file.name}')
                
        # Generate colors 
        pixel_values, converted_pixels, main_colors = generate_colors(image)
        
        ## 
        with st.sidebar:
            st.write('Renklere göre yükseklik belirleyin (mm)')  
            empt = st.empty()
            col1, col2 = empt.columns([4, 6])     
            for color in main_colors:
                # Display the color as a 15x15 colored box
                col1.image(Image.fromarray(np.tile(color, (25, 25, 1)).astype(np.uint8)), caption='', width=40, use_column_width=False)
                # Prompt the user for the height value
                heights[str(color)] = col2.number_input("",0,1000, 10, label_visibility="collapsed", key=f"{color}")
                
        button=st.button('Yan panelde verilen yüksekliklere göre çevir ')
        if button:
            calculate_stl(converted_pixels, main_colors, heights, step)
        st.write('Renk kodları:')
        st.write(main_colors)
        st.image(converted_pixels, 'converted_pixels')

if __name__=='__main__':
    main()
    