

import os
import numpy as np

from stl import mesh
import pygltflib

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
EXPORT_FILE_FORMAT = 'gltf'

def download_file(fn):
with open(f"data/{EXPORT_FILE_FORMAT}/{fn}", 'rb') as file:
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
def convert_jpg_to_gltf(pixel_values, main_colors, heights, step):
# convert jpg to gltf. And each color height will get from
# calculate_height_based_on_color()
pass

def main():
global file, n_main_colors, main_colors, heights, step
with st.sidebar:
file = st.file_uploader('Dosyayı sürükleyin yada yükleyin', type=["jpeg"], help=f'{EXPORT_FILE_FORMAT} ye çevrilecek dosyayı yükleyin')
n_main_colors = st.slider('Renk sayısı', 1,5,5,1)
step = st.slider('Mesh sıklığı (pixel)', 1,10,1,1)

    file_list = os.listdir(path=path.replace('files', EXPORT_FILE_FORMAT))
     # Display chat titles and delete icons
    st.write(f'Oluşturulan {EXPORT_FILE_FORMAT} dosyası:')
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
                os.remove(f"data/{EXPORT_FILE_FORMAT}/{fn}")
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
        ## convert jpg tp gltf
        convert_jpg_to_gltf(converted_pixels, main_colors, heights, step)
        
    st.write('Renk kodları:')
    st.write(main_colors)
    st.image(converted_pixels, 'converted_pixels')
if name=='main':
main()
def yyy(): 
    heights_array = np.zeros(pixel_values.shape[:2])
    # For a start we will only set heights of pixel_values for which colors are found in main_colors

    for h, color in enumerate(main_colors):
        heights_array[np.all(pixel_values == color, axis=-1)] = heights[str(color)]
    print(heights_array)
    

    heightmap_mesh = trimesh.creation.heightmap(heights_array, height=1e-3, fill=True)
    vertices, faces = heightmap_mesh.vertices, heightmap_mesh.faces

    # Data that will be packed into buffer
    buffer_data = b''

    # Create the GLTF object
    gltf = GLTF2()
    buffer = Buffer()
    gltf.buffers.append(buffer)

    buffer_view = BufferView(buffer=0, byteLength=vertices.nbytes, target=pygltflib.ARRAY_BUFFER)
    gltf.bufferViews.append(buffer_view)
    buffer_view_index = len(gltf.bufferViews) - 1

    accessor = Accessor(bufferView=buffer_view_index, byteOffset=0, componentType=pygltflib.FLOAT,
                        count=len(vertices), type=pygltflib.VEC3, max=vertices.max(axis=0).tolist(),
                        min=vertices.min(axis=0).tolist())
    gltf.accessors.append(accessor)
    position_accessor_index = len(gltf.accessors) - 1

    buffer_view = BufferView(buffer=0, byteLength=faces.nbytes, target=pygltflib.ARRAY_BUFFER)
    gltf.bufferViews.append(buffer_view)
    buffer_view_index = len(gltf.bufferViews) - 1

    accessor = Accessor(bufferView=buffer_view_index, byteOffset=0, componentType=pygltflib.UNSIGNED_INT,
                        count=len(faces), type=pygltflib.SCALAR)
    gltf.accessors.append(accessor)

    indices_accessor_index = len(gltf.accessors) - 1

    buffer_data += vertices.flatten().tobytes() + faces.flatten().tobytes()

    materials_dict = {}
    for i, main_color in enumerate(main_colors):
        pbr = PbrMetallicRoughness(baseColorFactor=[main_color[0]/255.0, 
                                                    main_color[1]/255.0, 
                                                    main_color[2]/255.0, 
                                                    1.0]
                                )
        
        material = Material(pbrMetallicRoughness=pbr)
        color = str(tuple(main_color))  # Convert the color to a string for indexing
        materials_dict[color] = material
        gltf.materials.append(material)

    # Primitive
    primitive = Primitive(attributes={'POSITION': position_accessor_index}, 
                          indices=indices_accessor_index
                         )
    # Finding material_index for the primitive
    material_index = gltf.materials.index(materials_dict[color])
    primitive.material = material_index
    gltf.primitives.append(primitive)

    # Mesh
    mesh = Mesh(primitives=[len(gltf.primitives) - 1])
    gltf.meshes.append(mesh)

    # Node that refers to the mesh
    node = Node(mesh=len(gltf.meshes) - 1)
    gltf.nodes.append(node)

    scene = Scene(nodes=[len(gltf.nodes) - 1])
    gltf.scenes.append(scene)
    gltf.scene = len(gltf.scenes) - 1

    buffer.byteLength = len(buffer_data)
    gltf.buffers.append(buffer)



def xxxx():   
    vertices = []
    faces = []
    vertex_colors = []

    for i in range(0, pixel_values.shape[0], step):
        for j in range(0, pixel_values.shape[1], step):
            color = tuple(pixel_values[i][j])
            height = calculate_height_based_on_color(color, main_colors, heights)
            vertices.append([i, j, height])
            vertex_colors.append(color)

            if i > 0 and j > 0:
                faces.append([len(vertices) - 1, len(vertices) - 2, len(vertices) - pixel_values.shape[1]//step - 2])
            if i > 0 and j < pixel_values.shape[1] - 1:
                faces.append([len(vertices) - 1, len(vertices) - pixel_values.shape[1]//step - 2, len(vertices) - pixel_values.shape[1]//step - 1])

    # Create a colorized glTF mesh
    positions = np.array(vertices, dtype=np.float32)
    colors = np.array(vertex_colors, dtype=np.float32)
    indices = np.array(faces, dtype=np.uint32).flatten()

    primitive = pygltflib.Primitive(
        attributes={
            'POSITION': pygltflib.Accessor(bufferView=0, componentType=pygltflib.FLOAT, count=len(positions), type=pygltflib.VEC3),
            'COLOR_0': pygltflib.Accessor(bufferView=1, componentType=pygltflib.FLOAT, count=len(colors), type=pygltflib.VEC3)
        },
        indices=pygltflib.Accessor(bufferView=2, componentType=pygltflib.UNSIGNED_INT, count=len(indices), type=pygltflib.SCALAR),
        material=0
    )

    # Create a mesh with the primitive
    mesh = pygltflib.Mesh(primitives=[primitive])

    # Create a scene and add the mesh to it
    scene = pygltflib.Scene(nodes=[pygltflib.Node(mesh=0)])
    # Create a glTFData object and add the scene to it
    gltf_data = pygltflib.GLTF2(scenes=[scene], asset=pygltflib.Asset(version='2.0'))

    # Save the colorized mesh in GLTF format
    filename = file.name.replace(os.path.splitext(file.name)[1], EXPORT_FILE_FORMAT)
    gltf_file_path = f"data/{EXPORT_FILE_FORMAT}/{filename}"
    with open(gltf_file_path, 'w') as f:
        pygltflib.GLTF2Exporter(gltf_data).export(f)
   

    print('Bitti...')
    st.experimental_rerun()
    
    
    
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
    
def calculate_wrl(pixel_values, main_colors, heights, step):
    vertices = []
    faces = []
    vertex_colors = []

    for i in range(pixel_values.shape[0]):
        for j in range(pixel_values.shape[1]):
            color = tuple(pixel_values[i][j])
            height = calculate_height_based_on_color(color, main_colors, heights)
            vertices.append([i, j, height])
            vertex_colors.append(color)

            if i > 0 and j > 0:
                faces.append([len(vertices) - 1, len(vertices) - 2, len(vertices) - pixel_values.shape[1] - 2])
            if i > 0 and j < pixel_values.shape[1] - 1:
                faces.append([len(vertices) - 1, len(vertices) - pixel_values.shape[1] - 2, len(vertices) - pixel_values.shape[1] - 1])

    stl_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            stl_mesh.vectors[i][j] = vertices[face[j]]

    # Create a colorized trimesh
    colorized_mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), vertex_colors=np.array(vertex_colors))

    # Save the colorized mesh directly in VRML format
    filename = file.name.replace('jpeg', 'wrl')
    vrml_file_path = f"data/vrml/{filename}"
    colorized_mesh.export(vrml_file_path, file_type="vrml")
    print('Bitti...')
    st.experimental_rerun()