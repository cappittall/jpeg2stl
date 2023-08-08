import sys
import warnings
from mangum import Mangum

from fastapi.templating import Jinja2Templates
import markdown
import numpy as np
from PIL import Image
import trimesh
from scipy.spatial.distance import cdist
from scipy.spatial import distance

from fastapi import Request
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pathlib import Path
import shutil
import tempfile
import os
from zipfile import ZipFile
import glob
import cv2

app = FastAPI()
# Verilerin klasör olarak sunulması (Serve the data directory as static files)
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory="templates")
warnings.filterwarnings('ignore')

# CORS için tüm kökenlere izin ver (Allow all origins for CORS - You can customize this to your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Renk-yükseklik eşleştirmesini tanımla (Define the color-to-height mapping in millimeters)
color_to_height = {
    (0, 0, 0): 5,   # siyah (black)
    (255, 255, 0): 10, # sarı (yellow)
    (0, 0, 255): 15,  # mavi (blue)
    (255, 255, 255): 20, # beyaz (white)
    (255, 0, 0): 25   # kırmızı (red)
}

def preprocess_image(image_path):
    # Read the image
    
    image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    
    if image is not None:
        print("Image loaded successfully.")
    else:
        print("Failed to load image.")
        
    # If it's a 4-channel image (RGBA), convert to RGB
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    # Apply a Gaussian blur to reduce noise
    image = cv2.GaussianBlur(image, (5, 5), 0)
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Mirror the image horizontally
    image = cv2.flip(image, 1)
    return image

def process_image(image):
    global image_array, predefined_colors, resized_image, resized_image_array, resized_mapped_heights, resized_block_width, resized_block_length
    # Resmi yükle (Load the image)
    
    # Resmi NumPy dizisine dönüştür (Convert the image to a NumPy array)
    image_array = np.array(image)
    # Önceden tanımlanmış renkleri belirle (Define predefined colors)
    predefined_colors = np.array(list(color_to_height.keys()))
    # Daha hızlı işleme için resmi küçük bir çözünürlüğe yeniden boyutlandır (Resize the image to a smaller resolution for faster processing)
    resize_factor = 0.1
    height, width = image.shape[:2]
    resized_image = cv2.resize(image, (int(width * resize_factor), int(height * resize_factor)))
    # Yeniden boyutlandırılan resmi NumPy dizisine dönüştür (Convert the resized image to a NumPy array)
    resized_image_array = np.array(resized_image)
    # Yeniden boyutlandırılan resim için eşleştirilmiş yükseklikleri saklamak için bir dizi oluştur (Create an array to store the mapped heights for the resized image)
    resized_mapped_heights = np.zeros((resized_image_array.shape[0], resized_image_array.shape[1]), dtype=np.float32)
    # Yeniden boyutlandırılan resmi dolaşarak renkleri en yakın önceden tanımlanmış renge eşleştir (Iterate through the resized image and map colors to the closest predefined color)
    for i in reversed(range(resized_image_array.shape[0])):
        for j in range(resized_image_array.shape[1]):
            pixel_color = np.array([resized_image_array[i, j][:3]])
            closest_idx = cdist(pixel_color, predefined_colors).argmin()
            closest_color = tuple(predefined_colors[closest_idx])
            resized_mapped_heights[i, j] = color_to_height[closest_color]

    # 3D modelin toplam boyutunu tanımla (Define the total size of the 3D model in mm)
    total_size = 150
    # Yeniden boyutlandırılmış resim için her bloğun boyutunu hesapla (Calculate the size of each block for the resized image)
    resized_block_width = total_size / resized_image_array.shape[1]
    resized_block_length = total_size / resized_image_array.shape[0]


# En yakın önceden tanımlanmış rengi bulan işlev (Function to find the closest predefined color)
def find_closest_color(pixel_color):
    min_dist = float('inf')
    closest_color = None
    for predefined_color, _ in color_to_height.items():
        dist = distance.euclidean(pixel_color, predefined_color)
        if dist < min_dist:
            min_dist = dist
            closest_color = predefined_color

    return closest_color

# Renkli bir 3D blok oluşturan işlev (Function to create a 3D block with color)
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

@app.get('/')
def root(request: Request = None):
    # return ({"Error":"bellek kapasitesi aşıldı"} - Return an error response if the memory capacity is exceeded)
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/readme", response_class=HTMLResponse)
def readme_file():
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "README.md")
    with open(file_path, "r", encoding="utf-8") as file:
        readme_content = file.read()
        html_content = markdown.markdown(readme_content)
        styled_html = f"""
        <html>
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 40px;
                    }}
                    .github-markdown {{
                        max-width: 800px;
                        margin: auto;
                        box-sizing: border-box;
                    }}
                </style>
            </head>
            <body>
                <article class="markdown-body github-markdown">
                    {html_content}
                </article>
            </body>
        </html>
        """
        return HTMLResponse(content=styled_html)

def create_colorfull():
    # Create an array to store the mapped heights for the resized image
    resized_mapped_heights = np.zeros((resized_image_array.shape[0], resized_image_array.shape[1]), dtype=np.float32)
    # Renkli blokları birleştirerek 3D modeli oluştur (Create the 3D model by combining the blocks for the resized image with color)
    resized_meshes_with_color = []
    for i in range(resized_image_array.shape[0]):
        for j in range(resized_image_array.shape[1]):
            # En yakın önceden tanımlanmış rengi bul (Find the closest predefined color)
            pixel_color = resized_image_array[i, j][:3]
            closest_color = find_closest_color(pixel_color)
            height = color_to_height[closest_color]
            resized_mapped_heights[i, j] = height
            
            # Vertex renkleri için renkleri normalleştir (Normalize color for vertex colors)
            normalized_color = np.array(closest_color) / 255.0
            
            x = j * resized_block_width
            y = i * resized_block_length
            block = create_block_with_color(x, y, height, normalized_color)
            resized_meshes_with_color.append(block)

    # Tüm blokları tek bir mesh'e birleştir (Combine all the blocks into a single mesh)
    resized_final_mesh_with_color = trimesh.util.concatenate(resized_meshes_with_color)

    # GLTF'ye aktar (Export to GLTF)
    output_path_with_color = "output_with_color2.gltf"
    resized_final_mesh_with_color.export(output_path_with_color)

    # Export to OBJ
    output_path_with_color_obj = "output_with_color2.obj"
    resized_final_mesh_with_color.export(output_path_with_color_obj, file_type='obj')
    
    # Export to STL
    output_path_with_color_stl = "output_with_color2.stl"
    resized_final_mesh_with_color.export(output_path_with_color_stl, file_type='stl')


    # PLY'ye aktar (Export to PLY)
    # output_path_with_color_ply = "output_with_color2.ply"
    # resized_final_mesh_with_color.export(output_path_with_color_ply, file_type='ply')
    
@app.post("/img2gltf")
async def img2gltf(request: Request, 
                file: UploadFile = File(...),
                black_height: int = Form(5),
                yellow_height: int = Form(10),
                blue_height: int = Form(15),
                white_height: int = Form(20),
                red_height: int = Form(25)):
    
    # Update the color_to_height dictionary with new values
    color_to_height[(0, 0, 0)] = black_height
    color_to_height[(255, 255, 0)] = yellow_height
    color_to_height[(0, 0, 255)] = blue_height
    color_to_height[(255, 255, 255)] = white_height
    color_to_height[(255, 0, 0)] = red_height
    print("color_to_height",color_to_height)
    # Uzantısı olmadan yüklenen dosyanın adını al (Get the original filename without extension)
    original_filename = os.path.splitext(file.filename)[0]
    # İstekten temel URL'yi al (Get the base URL from the request)
    base_url = str(request.base_url)
    # Resim ve çıktı dosyalarını tutacak geçici bir dizin oluştur (Create a temporary directory to hold the image and output files)
    with tempfile.TemporaryDirectory() as temp_dir:
        # Yüklenen resmi kaydet (Save the uploaded image)
        image_path = os.path.join(temp_dir, file.filename)
        # Dosyaları tutacak dizini tanımla (Define the directory to hold the files)
        folder_path = Path(f"data/{original_filename}")
        folder_path.mkdir(parents=True, exist_ok=True)
        # Yüklenen resmi kaydet (Save the uploaded image)
        image_path = folder_path / file.filename
        
        with open(image_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
            

        # Yüklenen resmi işle (Process the uploaded image)

        image = preprocess_image(image_path)

        process_image(image)
    
        # Resmi işle (Process the image)
        # Varolan işlevinizi çağırarak GLTF dosyasını oluştur (Call your existing function to create the GLTF file)
        create_colorfull()  
        
        # Orijinal dosya adına göre GLTF ve BIN dosya adlarını tanımla (Define the GLTF and BIN file names based on the original filename)
        gltf_filename = f"{original_filename}.gltf"
        zip_path = folder_path / f"{original_filename}.zip"
        
        # Define the OBJ file name based on the original filename
        obj_filename = f"{original_filename}.obj"
        
        # Define the STL file name based on the original filename
        stl_filename = f"{original_filename}.stl"
        
        # GLTF dosyasını yeniden adlandır ve belirli klasöre taşı (Rename the GLTF file and move to the specific folder)
        shutil.move("output_with_color2.gltf", folder_path / gltf_filename)
        
        # Rename the OBJ file and move it to the specific folder
        shutil.move("output_with_color2.obj", folder_path / obj_filename)  # For the colored version

        # Rename the STL file and move it to the specific folder
        shutil.move("output_with_color2.stl", folder_path / stl_filename)  # For the colored version

        # GLTF ve BIN dosyalarını ZIP olarak sıkıştır (Zip the GLTF and BIN files)
        with ZipFile(zip_path, 'w') as zipf:
            zipf.write(folder_path / gltf_filename, arcname=gltf_filename)  # Set the relative path inside ZIP
            # Add the OBJ file to the ZIP
            zipf.write(folder_path / obj_filename, arcname=obj_filename)  # Set the relative path inside ZIP

            # Add the STL file to the ZIP
            zipf.write(folder_path / stl_filename, arcname=stl_filename)  # Set the relative path inside ZIP

            # Tüm BIN dosyalarını dahil et (Include all BIN files)
            bin_files = glob.glob("gltf_buffer_*.bin")
            for bin_file in bin_files:
                arcname = os.path.basename(bin_file)  # Dizin olmadan dosya adını al (Get the filename without the directory)
                zipf.write(bin_file, arcname=arcname)  # ZIP içindeki göreli yolu belirle (Set the relative path inside ZIP)

        # İndirme bağlantısını oluştur (Create the download link)
        download_link = f"{base_url}data/{original_filename}/{original_filename}.zip"

        # Yanıtı dosya yolunu ve indirme bağlantısını içeren JSON olarak döndür (Return the response as JSON with the file path and download link)
        return JSONResponse(content={"file": str(zip_path), "download_link": download_link, 'Hakan cep':'05326023450'})

handler = Mangum(app)

