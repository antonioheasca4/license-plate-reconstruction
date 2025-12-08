# Camera Client Simulator

Embedded camera simulator for License Plate Reconstruction System.

## Functionality

Monitors a folder and automatically sends any new image to the server for:
- Reconstruction (Pix2Pix)
- OCR (fast-plate-ocr)
- Save local results

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests` - HTTP client for API calls
- `watchdog` - Folder monitoring (detect new files)

## Configuration

Edit `config.json`:

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

**Parameters:**
- `server_url`: Backend URL (default: http://localhost:8000)
- `username/password`: JWT authentication credentials
- `watch_folder`: Folder monitored for new images
- `results_folder`: Where are reconstructed images + OCR results saved
- `auto_ocr`: Automatically run OCR after reconstruction (true/false)
- `save_results`: Save results locally (true/false)

## Use

### 1. Start Backend

```bash
# From the main project folder
.\start.ps1  # Windows
./start.sh   # Linux/macOS
```

### 2. Create an account (if you don't already have one)

Open http://localhost:3000 and register.

### 3. Update config.json

Put your username and password in `config.json`.

### 4. Start Camera Client

```bash
cd camera_client
pip install -r requirements.txt
python camera_simulator.py
```

### 5. Test

Copy a plate image to the folder `sample_images/`:

```bash
# Windows
copy path\to\license_plate.jpg sample_images\

# Linux/macOS
cp path/to/license_plate.jpg sample_images/
```

**What happens automatically:**
1. Wait for the backend to become available (max 60 seconds)
2. Authenticate to the backend (JWT)
3. Start monitoring the `sample_images/` folder
4. Detect new images in the folder
5. Send image to `/api/inference` for reconstruction
6. Save to database with `source="camera"` (POST `/api/history`)
7. Run OCR on original + reconstructed (if `auto_ocr: true`)
8. Update database with OCR results (PUT `/api/history/{id}`)
9. Save results locally in `results/`
10. Log everything in `camera_client.log`

## Output Exemple

```
License Plate Camera Client Simulator
Configuration loaded from config.json
Authenticating to server...
Authentication successful
Watching for new images...
Drop images in: camera_client\sample_images
Press Ctrl+C to stop

New image detected: plate_001.jpg
Processing image: plate_001.jpg
   Sending to /api/inference...
   Reconstruction completed in 1.23s
   Saved: plate_001_reconstructed_20251203_143025.png
   Running OCR on original image...
   Original OCR: ABC123
   Running OCR on reconstructed image...
   Reconstructed OCR: ABC123
   OCR results saved: plate_001_ocr_20251203_143025.json
  Processing complete for plate_001.jpg
```