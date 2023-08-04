# 3D Modelleme Uygulaması (3D Modeling Application)

Bu kod, renkli 2D görüntülerden 3D modeller oluşturur. (This code creates 3D models from colored 2D images.)

## Başlangıç (Getting Started)

Bu projede, belirli renklere karşılık gelen yükseklik değerleri kullanılarak renkli bir resmi 3D modeline dönüştüren bir FastAPI uygulaması bulunmaktadır. (In this project, you will find a FastAPI application that transforms a colored image into a 3D model using height values corresponding to specific colors.)

## İçindekiler (Table of Contents)

1. [Başlangıç (Getting Started)](#başlangıç-getting-started)
   - [Gereksinimler (Prerequisites)](#gereksinimler-prerequisites)
   - [Kurulum (Installation)](#kurulum-installation)
   - [Çalıştırma (Running)](#çalıştırma-running)
2. [API Kullanımı (API Usage)](#api-kullanımı-api-usage)
3. [Lisans (License)](#lisans-license)

## Başlangıç (Getting Started)

### Ortam Oluşturma (Creating Environment)

#### Windows

Windows'ta bir sanal ortam oluşturmak için:

```bash
python -m venv myenv
```

Aktive etmek için:

```bash
myenv\Scripts\activate
```

#### MacOS veya Linux

macOS veya Linux'ta bir sanal ortam oluşturmak için:

```bash
python3 -m venv myenv

```

Active etmek için

```bash
source myenv/bin/activate
```

### Gereksinimler (Prerequisites)

Bu projeyi çalıştırmadan önce aşağıdaki kütüphanelerin yüklü olduğundan emin olun: (Before running this project, ensure the following libraries are installed:)

- FastAPI
- Jinja2
- numpy
- PIL (Pillow)
- trimesh
- scipy

### Kurulum (Installation)

Projenin ana dizininde, gerekli kütüphaneleri yüklemek için aşağıdaki komutu çalıştırın: (In the project's main directory, run the following command to install the required libraries:)

```bash
pip install fastapi jinja2 numpy Pillow trimesh scipy

```

veya (or)

```bash
pip install -r requirements.txt 
```

## Kullanım (Usage)

Uygulamayı başlatmak için `app` nesnesini kullanın. (Use the `app` object to start the application.)

Örnek (Example):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

Tarayıcıda <http://localhost:8000/> adresine giderek API belgelerine erişebilirsiniz. (You can access the API documentation by navigating to <http://localhost:8000/> in the browser.)

## Özellikler (Features)

CORS İzinleri (CORS Permissions)
Bu uygulama, CORS için tüm kökenlere izin verir. Bu ayarı ihtiyacınıza göre özelleştirebilirsiniz. (This application allows all origins for CORS. You can customize this setting according to your needs.)

### CORS için tüm kökenlere izin ver (Allow all origins for CORS - You can customize this to your needs)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Renk-Yükseklik Eşleştirmesi (Color-to-Height Mapping)

Giriş resmindeki belirli renklerin 3D modeldeki yüksekliklere nasıl eşlendiğini belirleyebilirsiniz. (You can specify how particular colors in the input image are mapped to heights in the 3D model.)

```python
# Renk-yükseklik eşleştirmesini tanımla (Define the color-to-height mapping in millimeters)
color_to_height = {
    (0, 0, 0): 5,   # siyah (black)
    (255, 255, 0): 25, # sarı (yellow)
    (0, 0, 255): 40,  # mavi (blue)
    (255, 255, 255): 30, # beyaz (white)
    (255, 0, 0): 50   # kırmızı (red)
}

```

## 3D Model Dönüşümü (3D Model Transformation)

3D modeller, GLTF, OBJ ve PLY ( # ile yorumlanmış) gibi farklı dosya formatlarında dışa aktarılabilir. (3D models can be exported in different file formats such as GLTF, OBJ, and PLY (commented out).)

## Statik Dosya Sunumu (Static File Serving)

Uygulama, statik dosyaları sunabilir, bu sayede dönüştürülen 3D modellere erişilebilir. (The application can serve static files, allowing access to the converted 3D models.)

## İletişim (Contact)

Daha fazla bilgi veya yardım için, lütfen bizimle iletişime geçin. (For more information or assistance, please contact us.)

Hakan Çetin

E-Mail: <netcat16@gmail.com>

Tel: +90(532) 602 3450
