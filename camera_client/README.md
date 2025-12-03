# Camera Client Simulator

Simulator de cameră embedded pentru License Plate Reconstruction System.

## 🎯 Funcționalitate

Monitorizează un folder și trimite automat orice imagine nouă la server pentru:
- Reconstrucție (Pix2Pix)
- OCR (fast-plate-ocr)
- Salvare rezultate locale

## 📋 Cerințe

```bash
pip install -r requirements.txt
```

Dependințe:
- `requests` - HTTP client pentru API calls
- `watchdog` - Folder monitoring (detectare fișiere noi)

## ⚙️ Configurare

Editează `config.json`:

```json
{
  "server_url": "http://localhost:8000",
  "username": "your_username",
  "password": "your_password",
  "watch_folder": "./sample_images",
  "results_folder": "./results",
  "auto_ocr": true,
  "save_results": true,
  "log_level": "INFO"
}
```

**Parametri:**
- `server_url`: URL-ul backend-ului (default: http://localhost:8000)
- `username/password`: Credențiale pentru autentificare JWT
- `watch_folder`: Folder monitorizat pentru imagini noi
- `results_folder`: Unde se salvează imaginile reconstruite + OCR results
- `auto_ocr`: Rulează automat OCR după reconstrucție (true/false)
- `save_results`: Salvează rezultatele local (true/false)

## 🚀 Utilizare

### 1. Pornește Backend-ul

```bash
# Din folderul principal al proiectului
.\start.ps1  # Windows
./start.sh   # Linux/macOS
```

### 2. Creează un cont (dacă nu ai deja)

Deschide http://localhost:3000 și înregistrează-te.

### 3. Actualizează config.json

Pune username-ul și parola ta în `config.json`.

### 4. Pornește Camera Client

```bash
cd camera_client
pip install -r requirements.txt
python camera_simulator.py
```

### 5. Testează

Copiază o imagine cu plăcuță în folderul `sample_images/`:

```bash
# Windows
copy path\to\license_plate.jpg sample_images\

# Linux/macOS
cp path/to/license_plate.jpg sample_images/
```

**Ce se întâmplă automat:**
1. ⏳ Așteaptă ca backend-ul să devină disponibil (max 60 secunde)
2. 🔐 Se autentifică la backend (JWT)
3. 👀 Începe monitorizarea folder-ului `sample_images/`
4. 📸 Detectează imagini noi în folder
5. 🔄 Trimite imagine la `/api/inference` pentru reconstrucție
6. 💾 Salvează în database cu `source="camera"` (POST `/api/history`)
7. 🔍 Rulează OCR pe original + reconstruită (dacă `auto_ocr: true`)
8. 📝 Actualizează database cu rezultate OCR (PUT `/api/history/{id}`)
9. 💿 Salvează rezultatele local în `results/`
10. 📋 Loghează tot în `camera_client.log`

## 📊 Output Exemple

```
🎥 License Plate Camera Client Simulator
✅ Configuration loaded from config.json
🔐 Authenticating to server...
✅ Authentication successful
👀 Watching for new images...
📂 Drop images in: D:\LPR\camera_client\sample_images
⏹️  Press Ctrl+C to stop

🆕 New image detected: plate_001.jpg
📸 Processing image: plate_001.jpg
   🔄 Sending to /api/inference...
   ✅ Reconstruction completed in 1.23s
   💾 Saved: plate_001_reconstructed_20251203_143025.png
   🔍 Running OCR on original image...
   📝 Original OCR: ABC123
   🔍 Running OCR on reconstructed image...
   📝 Reconstructed OCR: ABC123
   💾 OCR results saved: plate_001_ocr_20251203_143025.json
✅ Processing complete for plate_001.jpg
```

## 📁 Structura Folderelor

```
camera_client/
├── camera_simulator.py    # Script principal
├── config.json            # Configurare
├── requirements.txt       # Dependințe Python
├── README.md             # Documentație
├── sample_images/        # Folder monitorizat (pune imagini aici)
├── results/              # Rezultate salvate automat
│   ├── plate_001_reconstructed_20251203_143025.png
│   ├── plate_001_ocr_20251203_143025.json
│   └── ...
└── camera_client.log     # Log file detaliat
```

## 🔧 Troubleshooting

### "Cannot connect to server"
Asigură-te că backend-ul rulează:
```bash
# Verifică dacă backend-ul e pornit
curl http://localhost:8000
```

### "Authentication failed"
Verifică username/password în `config.json` - trebuie să fie un cont valid creat în aplicație.

### "Token expired"
Clientul se re-autentifică automat. Dacă problema persistă, repornește clientul.

### Nu detectează imaginile noi
- Verifică că folderul `watch_folder` din config.json există
- Asigură-te că imaginile sunt `.jpg`, `.jpeg` sau `.png`
- Verifică `camera_client.log` pentru erori

## 🎯 Use Cases

### 1. Simulare Cameră de Supraveghere
Copiază imagini în `sample_images/` pentru a simula o cameră care captează plăcuțe.

### 2. Testing Batch
Copiază mai multe imagini simultan pentru a testa procesarea în paralel.

### 3. Integrare cu Cameră Reală
Modifică scriptul să citească de la webcam/RTSP stream în loc de folder.

## 🔐 Securitate

- ✅ Autentificare JWT pe fiecare request
- ✅ Token refresh automat la expirare
- ✅ Credențiale doar în config.json local (NU commita pe Git!)
- ✅ HTTPS ready (modifică `server_url` pentru production)

## 🚀 Next Steps

Pentru integrare cu cameră reală:
1. Modifică `camera_simulator.py` să folosească OpenCV
2. Captează frame-uri de la webcam/IP camera
3. Aplică aceeași logică de trimitere la server

Exemplu webcam:
```python
import cv2

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cv2.imwrite('captured.jpg', frame)
client.process_image('captured.jpg')
```

---

**TL;DR:**
1. Editează `config.json` cu credențialele tale
2. `python camera_simulator.py`
3. Copiază imagini în `sample_images/`
4. Watch the magic happen! ✨
