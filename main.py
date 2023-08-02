import warnings
from fastapi.templating import Jinja2Templates
import numpy as np
from PIL import Image
import trimesh
from scipy.spatial.distance import cdist
from scipy.spatial import distance

from fastapi import Request
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import tempfile
import os
from zipfile import ZipFile
import glob

app = FastAPI()
# Serve the data directory as static files
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory="templates")
warnings.filterwarnings('ignore')

# Allow all origins for CORS (You can customize this to your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the color-to-height mapping (in millimeters)
color_to_height = {
    (0, 0, 0): 5,   # black
    (255, 255, 0): 15, # yellow
    (0, 0, 255): 10,  # blue
    (255, 255, 255): 30, # white
    (255, 0, 0): 25   # red
}

def process_image(image_path):
    global image, image_array, predefined_colors, resized_image, resized_image_array, resized_mapped_heights, resized_block_width, resized_block_length
    # Load the image
    image = Image.open(image_path)
    # Convert the image to a NumPy array
    image_array = np.array(image)
    # Define predefined colors
    predefined_colors = np.array(list(color_to_height.keys()))
    # Resize the image to a smaller resolution for faster processing
    resize_factor = 0.1
    resized_image = image.resize((int(image.width * resize_factor), int(image.height * resize_factor)))
    # Convert the resized image to a NumPy array
    resized_image_array = np.array(resized_image)
    # Create an array to store the mapped heights for the resized image
    resized_mapped_heights = np.zeros((resized_image_array.shape[0], resized_image_array.shape[1]), dtype=np.float32)
    # Iterate through the resized image and map colors to the closest predefined color
    for i in reversed(range(resized_image_array.shape[0])):
        for j in range(resized_image_array.shape[1]):
            pixel_color = np.array([resized_image_array[i, j][:3]])
            closest_idx = cdist(pixel_color, predefined_colors).argmin()
            closest_color = tuple(predefined_colors[closest_idx])
            resized_mapped_heights[i, j] = color_to_height[closest_color]

    # Define the total size of the 3D model (in mm)
    total_size = 1200
    # Calculate the size of each block for the resized image
    resized_block_width = total_size / resized_image_array.shape[1]
    resized_block_length = total_size / resized_image_array.shape[0]


# Function to find the closest predefined color
def find_closest_color(pixel_color):
    min_dist = float('inf')
    closest_color = None
    for predefined_color, _ in color_to_height.items():
        dist = distance.euclidean(pixel_color, predefined_color)
        if dist < min_dist:
            min_dist = dist
            closest_color = predefined_color

    return closest_color

# Function to create a 3D block with color
def create_block_with_color(x, y, height, color):
    vertices = [
        [x, y, 0],
        [x + resized_block_width, y, 0],
        [x + resized_block_width, y + resized_block_length, 0],
        [x, y + resized_block_length, 0],
        [x, y, height],
        [x + resized_block_width, y, height],
        [x + resized_block_width, y + resized_block_length, height],
        [x, y + resized_block_length, height]
    ]
    faces = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7]
    ]
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    vertex_colors = np.tile(color, (8, 1))
    mesh.visual.vertex_colors = vertex_colors
    return mesh

# Function to create a 3D block
def create_block(x, y, height):
    vertices = [
        [x, y, 0],
        [x + resized_block_width, y, 0],
        [x + resized_block_width, y + resized_block_length, 0],
        [x, y + resized_block_length, 0],
        [x, y, height],
        [x + resized_block_width, y, height],
        [x + resized_block_width, y + resized_block_length, height],
        [x, y + resized_block_length, height]
    ]
    faces = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7]
    ]
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def create_colorfull():
    # Create an array to store the mapped heights for the resized image
    resized_mapped_heights = np.zeros((resized_image_array.shape[0], resized_image_array.shape[1]), dtype=np.float32)

    # Create the 3D model by combining the blocks for the resized image with color
    resized_meshes_with_color = []
    for i in range(resized_image_array.shape[0]):
        for j in range(resized_image_array.shape[1]):
            # Find the closest predefined color
            pixel_color = resized_image_array[i, j][:3]
            closest_color = find_closest_color(pixel_color)
            height = color_to_height[closest_color]
            resized_mapped_heights[i, j] = height
            
            # Normalize color for vertex colors
            normalized_color = np.array(closest_color) / 255.0
            
            x = j * resized_block_width
            y = i * resized_block_length
            block = create_block_with_color(x, y, height, normalized_color)
            resized_meshes_with_color.append(block)

    # Combine all the blocks into a single mesh
    resized_final_mesh_with_color = trimesh.util.concatenate(resized_meshes_with_color)

    # Export to GLTF
    output_path_with_color = "output_with_color2.gltf"
    resized_final_mesh_with_color.export(output_path_with_color)

    # Export to PLY
    # output_path_with_color_ply = "output_with_color2.ply"
    # resized_final_mesh_with_color.export(output_path_with_color_ply, file_type='ply')
    
def create_monocolor():
    # Create the 3D model by combining the blocks for the resized image
    resized_meshes = []
    for i in range(resized_image_array.shape[0]):
        for j in range(resized_image_array.shape[1]):
            height = resized_mapped_heights[i, j]
            x = j * resized_block_width
            y = i * resized_block_length
            block = create_block(x, y, height)
            resized_meshes.append(block)

    # Combine all the blocks into a single mesh
    resized_final_mesh = trimesh.util.concatenate(resized_meshes)

    # Export to GLTF
    output_path = "output.gltf"
    resized_final_mesh.export(output_path)

@app.get('/')
def root(request: Request = None):
    return ({"Error":"memory capacity exceeded"})
    return templates.TemplateResponse("index.html", {"request":request})
    
@app.post("/img2gltfxxx")
async def img2gltf(request: Request, file: UploadFile = File(...)):
    # Get the original filename without extension
    original_filename = os.path.splitext(file.filename)[0]
    # Get the base URL from the request
    base_url = str(request.base_url)
    # Create a temporary directory to hold the image and output files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the uploaded image
        image_path = os.path.join(temp_dir, file.filename)
        # Define the directory to hold the files
        folder_path = Path(f"data/{original_filename}")
        folder_path.mkdir(parents=True, exist_ok=True)
        # Save the uploaded image
        image_path = folder_path / file.filename
        
        with open(image_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the uploaded image
        process_image(image_path)
    
        # Process the image
        global image
        image = Image.open(image_path)
        create_colorfull()  # Call your existing function to create the GLTF file
         # Define the GLTF and BIN file names based on the original filename
        gltf_filename = f"{original_filename}.gltf"
        zip_path = folder_path / f"{original_filename}.zip"
        
        # Rename the GLTF file and move to the specific folder
        shutil.move("output_with_color2.gltf", folder_path / gltf_filename)
        
        # Zip the GLTF and BIN files
        with ZipFile(zip_path, 'w') as zipf:
            zipf.write(folder_path / gltf_filename, arcname=gltf_filename)  # Set the relative path inside ZIP
            # Include all BIN files
            bin_files = glob.glob("gltf_buffer_*.bin")
            for bin_file in bin_files:
                arcname = os.path.basename(bin_file)  # Get the filename without the directory
                zipf.write(bin_file, arcname=arcname)  # Set the relative path inside ZIP

        # Create the download link
        download_link = f"{base_url}data/{original_filename}/{original_filename}.zip"

        # Return the response as JSON with the file path and download link
        return JSONResponse(content={"file": str(zip_path), "download_link": download_link, 'Hakan cep':'05326023450'})
    