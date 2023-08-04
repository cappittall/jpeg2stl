# 3D Modelleme Uygulaması (3D Modeling Application)
Bu kod, renkli 2D görüntülerden 3D modeller oluşturur. (This code creates 3D models from colored 2D images.)
## İçindekiler (Table of Contents)
1. [Başlangıç (Getting Started)](#başlangıç-getting-started)
   - [Ortam Oluşturma (Creating Environment)](#ortam-oluşturma-creating-environment)
   - [Gereksinimler (Prerequisites)](#gereksinimler-prerequisites)
   - [Kurulum (Installation)](#kurulum-installation)
   - [Çalıştırma (Running)](#çalıştırma-running)
2. [Kullanım (Usage)](#kullanım-usage)
3. [Özellikler (Features)](#özellikler-features)
   - [Renk-Yükseklik Eşleştirmesi (Color-to-Height Mapping)](#renk-yükseklik-eşleştirmesi-color-to-height-mapping)
   - [3D Model Dönüşümü (3D Model Transformation)](#3d-model-dönüşümü-3d-model-transformation)
   - [3D Blok Oluşturma (3D Block Creation)](#3d-blok-oluşturma-3d-block-creation)
   - [İhracat Formatları (Export Formats)](#ihracat-formatları-export-formats)
   - [İndirme İşlemi (Download Process)](#indirme-İşlemi-download-process)
   - [Statik Dosya Sunumu (Static File Serving)](#statik-dosya-sunumu-static-file-serving)
4. [İletişim (Contact)](#İletişim-contact)
5. [Lisans (License)](#lisans-license)
## Başlangıç (Getting Started)
### Ortam Oluşturma (Creating Environment)
#### Windows
Windows'ta bir sanal ortam oluşturmak için:
```bash
python -m venv myenv
```
Aktive etmek için:
```
myenv\\Scripts\\activate
```
#### MacOS veya Linux 
macOS veya Linux'ta bir sanal ortam oluşturmak için:
```
python3 -m venv myenv
```
Active etmek için
```
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
## Kullanım (Usage)
Uygulamayı başlatmak için `app` nesnesini kullanın. (Use the `app` object to start the application.)
Örnek (Example):
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Tarayıcıda http://localhost:8000/ adresine giderek API belgelerine erişebilirsiniz. (You can access the API documentation by navigating to http://localhost:8000/ in the browser.)
## Özellikler (Features)
### CORS İzinleri (CORS Permissions)
Bu uygulama, CORS için tüm kökenlere izin verir. Bu ayarı ihtiyacınıza göre özelleştirebilirsiniz. (This application allows all origins for CORS. You can customize this setting according to your needs.)
### Renk-Yükseklik Eşleştirmesi (Color-to-Height Mapping)
Giriş resmindeki belirli renklerin 3D modeldeki yüksekliklere nasıl eşlendiğini belirleyebilirsiniz. (You can specify how particular colors in the input image are mapped to heights in the 3D model.) Önceden tanımlanmış renklerle yükseklikler arasında bir eşleme yapılır, ve bu, 3D modelleme sürecinin temelidir. (Predefined colors are mapped to heights, and this forms the basis for the 3D modeling process.)
### 3D Model Dönüşümü (3D Model Transformation)
Yüklenen 2D resim, belirlenen renkler temelinde 3D bir modele dönüştürülür ve GLTF, OBJ ve diğer formatlarda dışa aktarılır. (The uploaded 2D image is transformed into a 3D model based on specified colors and exported in GLTF, OBJ, and other formats.) Resim işleme adımları, yeniden boyutlandırma ve renk eşleme gibi işlemleri içerir. (Image processing steps include operations like resizing and color mapping.)### 3D Blok Oluşturma (3D Block Creation)
3D bloklar, belirli boyutlar ve renklerle oluşturulur. Renkli ve renksiz 3D bloklar oluşturmak için işlevler mevcuttur. (3D blocks are created with specific dimensions and colors. Functions are available to create 3D blocks both with and without color.)
### İhracat Formatları (Export Formats)
3D modeller, GLTF, OBJ ve PLY (yorumlanmış) gibi farklı dosya formatlarında dışa aktarılabilir. (3D models can be exported in different file formats such as GLTF, OBJ, and PLY (commented out).)
### İndirme İşlemi (Download Process)
Dışa aktarılan dosyalar sıkıştırılır ve indirme bağlantısı oluşturulur. Yanıt, dosya yolu ve indirme bağlantısını içeren JSON olarak döner. (Exported files are zipped, and a download link is created. The response is returned as JSON with the file path and download link.)

### Statik Dosya Sunumu (Static File Serving)
Uygulama, statik dosyaları sunabilir, bu sayede dönüştürülen 3D modellere erişilebilir. (The application can serve static files, allowing access to the converted 3D models.)

## İletişim (Contact)
Daha fazla bilgi veya yardım için, lütfen bizimle iletişime geçin. (For more information or assistance, please contact us.)

Hakan Çetin 
Mail: netcat16@gmail.com 
Tel: +90(532) 602 3450 
