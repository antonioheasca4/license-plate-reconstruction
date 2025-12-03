# License Plate Recognition System

A full-stack web application for Automatic License Plate Recognition (ALPR) with image reconstruction using Pix2Pix deep learning model. Built with FastAPI (Python) backend and React frontend, featuring JWT authentication and PostgreSQL database.

## 🏗️ Project Structure

```
license-plate-reconstruction/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application entry point
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models (User, ImageHistory with source field)
│   ├── schemas.py          # Pydantic schemas (ImageHistoryUpdate for OCR)
│   ├── auth.py             # Authentication logic
│   ├── ocr_service.py      # OCR service for license plate text recognition
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend Docker image
│   ├── .env               # Environment variables
│   ├── .env.example       # Example environment variables
│   └── ml_models/          # ML model directory
│       ├── model_loader.py # Pix2Pix model loading & inference
│       ├── *.keras         # Trained model (any .keras file)
│       └── README.md       # Model documentation
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── PrivateRoute.jsx
│   │   │   └── ImageUploader.jsx  # Upload & reconstruction UI
│   │   ├── contexts/       # Context providers (Auth)
│   │   ├── pages/          # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx  # Main app with upload
│   │   │   ├── Metrics.jsx     # Model metrics & PDF reports
│   │   │   ├── History.jsx     # Processing history with camera badge
│   │   │   └── History.css     # Styles for camera badge
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── Dockerfile          # Frontend Docker image
│   └── .env               # Environment variables
│
├── camera_client/          # Camera simulator (Edge device simulation)
│   ├── camera_simulator.py # Main client script with folder watching
│   ├── config.json         # Configuration (credentials, folders)
│   ├── requirements.txt    # Python dependencies (requests, watchdog)
│   ├── sample_images/      # Monitored folder for new images
│   ├── results/            # Local results (reconstructed images + OCR)
│   ├── camera_client.log   # Detailed logs
│   └── README.md           # Camera client documentation
│
├── docker-compose.yml      # Docker orchestration (3 services)
├── .env.docker             # Docker environment variables
├── .env.docker.example     # Docker env template
├── start.ps1               # Start script (Windows) - auto-starts camera client
├── start.sh                # Start script (Linux/macOS) - auto-starts camera client
├── stop.ps1                # Stop script (Windows)
├── stop.sh                 # Stop script (Linux/macOS)
├── AUTOMATION_GUIDE.md     # Automation & Docker documentation
├── ARCHITECTURE.md         # System architecture diagrams
└── ENV_BEST_PRACTICES.md   # Security best practices
```

## ✨ Features

### Core Functionality
- ✅ **User Authentication**: JWT-based authentication with secure password hashing (bcrypt)
- ✅ **User Registration & Login**: Complete user management system
- ✅ **Protected Routes**: Frontend and backend route protection
- ✅ **PostgreSQL Database**: Robust relational database with SQLAlchemy ORM (Dockerized)
- ✅ **License Plate Reconstruction**: Pix2Pix deep learning model for image enhancement
- ✅ **OCR Text Recognition**: Fast-plate-ocr integration for license plate text extraction

### Image Processing
- ✅ **Image Upload**: Drag & drop or click to upload license plate images
- ✅ **Real-time Inference**: Process images and view reconstructed results instantly
- ✅ **Side-by-Side Comparison**: Visual comparison of original vs reconstructed images
- ✅ **OCR on Both Images**: Run OCR on original and reconstructed plates to compare accuracy
- ✅ **Processing History**: View last 10 processed images with OCR results
- ✅ **Source Tracking**: Distinguish between web uploads and camera client uploads with visual badge
- ✅ **History Management**: Delete individual history items, update with new OCR results

### Client-Server Architecture
- ✅ **Camera Client Simulator**: Python script simulating embedded camera device
- ✅ **Folder Watching**: Automatic detection of new images (watchdog library)
- ✅ **Auto-processing**: Automatic reconstruction + OCR + database save for camera uploads
- ✅ **Camera Badge**: Visual indicator in UI for camera-originated images (📷 Camera)
- ✅ **Source Field**: Database tracks image source ("web" vs "camera")
- ✅ **Backend Wait**: Camera client waits for backend availability before starting

### Development & Deployment
- ✅ **Modern UI**: Responsive React interface with custom styling
- ✅ **Persistent State**: Images and OCR results persist when navigating between pages
- ✅ **CORS Configured**: Secure cross-origin resource sharing
- ✅ **Docker Support**: Full containerization with docker-compose
- ✅ **Automation Scripts**: One-command start (frontend + backend + camera client)
- ✅ **Hot Reload**: Instant updates during development (frontend & backend)
- 🔄 **Coming Soon**: Model fine-tuning, batch processing, export results

## 🚀 Prerequisites

Before you begin, ensure you have the following installed:

### Required for Development (Quick Start Scripts)
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/)) - For PostgreSQL container
- **Python 3.9+** ([Download](https://www.python.org/downloads/)) - For backend (requires TensorFlow 2.20.0)
- **Node.js 18+** and npm ([Download](https://nodejs.org/)) - For frontend
- **Git LFS** ([Download](https://git-lfs.github.com/)) - For ML model files (185 MB)

**Note**: Quick start scripts are available for both Windows (`start.ps1`) and Linux/macOS (`start.sh`).

### Required for Production (docker-compose up)
- **Docker Desktop** only - All services run in containers

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/antonioheasca4/license-plate-reconstruction.git
cd license-plate-reconstruction
```

**Note**: The ML model (185 MB) will be automatically downloaded via Git LFS during clone.

### 2. Backend Setup

**Windows (PowerShell):**
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env
```

**Linux/macOS (Bash):**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
```

**Note**: The `.env` file is already configured for Docker PostgreSQL:  
`DATABASE_URL=postgresql://lpr_user:lpr_password_change_in_production@localhost:5432/lpr_database`

**ML Dependencies Included**:
- TensorFlow 2.20.0 (Pix2Pix model)
- Pillow 10.2.0 (Image processing)
- NumPy 1.26.3 (Array operations)
- fast-plate-ocr 1.0.2 (License plate OCR)
- onnxruntime (Fast OCR inference)

**Important**: For production, generate a secure SECRET_KEY:

```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_hex(32))"
# Or on Python 3:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and update `SECRET_KEY` in your `.env` file.

### 3. Docker Setup (PostgreSQL)

**Windows (PowerShell):**
```powershell
# Create Docker environment file from example
copy .env.docker.example .env.docker
```

**Linux/macOS (Bash):**
```bash
# Create Docker environment file from example
cp .env.docker.example .env.docker
```

**Configure** `.env.docker` with PostgreSQL credentials (already pre-configured):
```
POSTGRES_USER=lpr_user
POSTGRES_PASSWORD=lpr_password_change_in_production
POSTGRES_DB=lpr_database
```

**Note**: The startup script will automatically start PostgreSQL container when you run the application.

### 4. Frontend Setup

**Windows (PowerShell):**
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file from example
copy .env.example .env
```

**Linux/macOS (Bash):**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file from example
cp .env.example .env
```

### 5. Add ML Model

Place your trained Pix2Pix model in the backend:

**Windows:**
```powershell
# Copy any .keras model file to:
backend/ml_models/

# Examples:
backend/ml_models/generator_256x128noSkew.keras
backend/ml_models/model.keras
backend/ml_models/pix2pix_generator.keras
```

**Linux/macOS:**
```bash
# Copy any .keras model file to:
backend/ml_models/

# Example:
cp /path/to/your/model.keras backend/ml_models/
```

**Model Requirements**:
- Format: `.keras` (TensorFlow/Keras)
- Input shape: (batch, 128, 256, 3)
- Output shape: (batch, 128, 256, 3)
- Type: Pix2Pix Generator for license plate reconstruction

The first `.keras` file found will be automatically loaded at backend startup.

## 🎯 Running the Application

### Quick Start (Recommended) ⭐

**Windows:**
```
# Option 1: Double-click to start
start.bat

# Option 2: PowerShell command
.\start.ps1
```

**Linux/macOS:**
```bash
# Make the script executable (first time only)
chmod +x start.sh

# Run the start script
./start.sh
```

This will automatically:
- ✅ Start PostgreSQL container (Docker)
- ✅ Start React Frontend (port 3000)
- ✅ Start FastAPI Backend (port 8000)

**Access the application:**
- 🌐 Frontend: **http://localhost:3000**
- 🔥 Backend API: **http://localhost:8000**
- 📚 API Documentation (Swagger): **http://localhost:8000/docs**
- 📖 Alternative API Docs (ReDoc): **http://localhost:8000/redoc**

**Stop the application:**
- Press `Ctrl+C` in terminal
- **Windows**: Or run `.\stop.ps1`
- **Linux/macOS**: Or run `./stop.sh`

### Alternative: Docker Compose (Production-like)

```powershell
# Start everything in Docker containers
docker-compose up --build

# Stop
docker-compose down
```

## 🧪 Testing the Application

### 1. Register a New User

- Open **http://localhost:3000** in your browser
- Click on "Register"
- Fill in the form:
  - Email: `test@example.com`
  - Username: `testuser` (no @ symbol allowed)
  - Password: `password123`
- Click "Register"

### 2. Login

- You'll be redirected to the login page
- Enter your credentials
- Click "Login"
- You'll be redirected to the Dashboard

### 3. Upload and Reconstruct License Plate Images

Once logged in:
1. **Upload an Image**:
   - Drag & drop or click to select a license plate image
   - Supported formats: PNG, JPG, JPEG (max 10MB)
   
2. **View Reconstruction**:
   - Click "Reconstruct Image" button
   - Wait for Pix2Pix model to process (few seconds)
   - View side-by-side comparison of original vs reconstructed image

3. **Run OCR**:
   - Click "🔍 Run OCR" button on original image to extract text
   - Click "🔍 Run OCR" button on reconstructed image to extract text
   - Compare OCR accuracy between original and reconstructed plates

### 4. Test Features

- View your profile information on the Dashboard
- Upload multiple license plate images for reconstruction
- Try degraded/blurry images to see reconstruction quality
- Compare OCR results between original and enhanced images
- Try logging out and accessing `/dashboard` directly (you'll be redirected to login)

## 📡 API Endpoints

### Public Endpoints

- `GET /` - API root information
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token

### Protected Endpoints (Require JWT Token)

- `GET /api/auth/me` - Get current user information
- `GET /api/protected` - Example protected route
- `POST /api/inference` - Upload and reconstruct license plate image
- `POST /api/ocr` - Extract text from license plate image using OCR
- `GET /api/model/status` - Check ML models status (Pix2Pix + OCR)
- `POST /api/history` - Save image processing history (auto-saved after reconstruction, accepts source field)
- `GET /api/history?limit=10` - Get user's processing history (default: last 10 items, includes source field)
- `PUT /api/history/{history_id}` - Update history item with OCR results (uses ImageHistoryUpdate schema)
- `DELETE /api/history/{history_id}` - Delete specific history item

### Using the API (cURL Examples)

**Register:**

Windows (PowerShell):
```powershell
$body = @{
    email = "test@example.com"
    username = "testuser"
    password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" -Method Post -Body $body -ContentType "application/json"
```

Linux/macOS (Bash):
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

**Login:**

Windows (PowerShell):
```powershell
$formData = @{
    username = "testuser"
    password = "password123"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -Body $formData
```

Linux/macOS (Bash):
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -F "username=testuser" \
  -F "password=password123"
```

**Access Protected Route:**

Windows (PowerShell):
```powershell
$token = "your_access_token_here"
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Headers $headers
```

Linux/macOS (Bash):
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer your_access_token_here"
```

**Upload Image for Reconstruction:**

Windows (PowerShell):
```powershell
$token = "your_access_token_here"
$headers = @{
    Authorization = "Bearer $token"
}

$filePath = "path/to/license_plate.jpg"
$boundary = [System.Guid]::NewGuid().ToString()

Invoke-RestMethod -Uri "http://localhost:8000/api/inference" -Method Post -Headers $headers -InFile $filePath -ContentType "multipart/form-data"
```

Linux/macOS (Bash):
```bash
curl -X POST "http://localhost:8000/api/inference" \
  -H "Authorization: Bearer your_access_token_here" \
  -F "file=@path/to/license_plate.jpg"
```

**Run OCR on Image:**

Windows (PowerShell):
```powershell
$token = "your_access_token_here"
$headers = @{
    Authorization = "Bearer $token"
}

$filePath = "path/to/license_plate.jpg"

Invoke-RestMethod -Uri "http://localhost:8000/api/ocr" -Method Post -Headers $headers -InFile $filePath -ContentType "multipart/form-data"
```

Linux/macOS (Bash):
```bash
curl -X POST "http://localhost:8000/api/ocr" \
  -H "Authorization: Bearer your_access_token_here" \
  -F "file=@path/to/license_plate.jpg"
```

**Check Models Status:**

Windows (PowerShell):
```powershell
$token = "your_access_token_here"
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/model/status" -Headers $headers
```

Linux/macOS (Bash):
```bash
curl -X GET "http://localhost:8000/api/model/status" \
  -H "Authorization: Bearer your_access_token_here"
```

## 🔒 Security Features

- **Password Hashing**: Bcrypt algorithm for secure password storage
- **JWT Tokens**: Secure token-based authentication with 30-minute expiration
- **HTTPS Ready**: Configure TLS/SSL for production deployment
- **CORS Protection**: Configured to allow only specific origins
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **GDPR Compliant**: User data handling follows best practices

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Robust relational database
- **Pydantic** - Data validation using Python type annotations
- **python-jose** - JWT token creation and validation
- **passlib** - Password hashing library
- **uvicorn** - ASGI server
- **TensorFlow 2.20.0** - Deep learning framework for Pix2Pix model
- **fast-plate-ocr 1.0.2** - License plate OCR with ONNX runtime
- **Pillow** - Image processing library
- **NumPy** - Numerical computing

### Frontend
- **React 18** - UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Vite** - Fast build tool and dev server

## 📝 Database Schema

### Users Table

| Column          | Type      | Description                    |
|-----------------|-----------|--------------------------------|
| id              | Integer   | Primary key                    |
| email           | String    | Unique email address           |
| username        | String    | Unique username                |
| hashed_password | String    | Bcrypt hashed password         |
| is_active       | Boolean   | Account status                 |
| is_admin        | Boolean   | Admin privileges flag          |
| created_at      | DateTime  | Account creation timestamp     |
| updated_at      | DateTime  | Last update timestamp          |

## 🔄 Next Steps

The core features are complete! Here's what's coming next:

1. ✅ ~~**Image Upload Feature**~~ - Complete! Upload license plate images via dashboard
2. ✅ ~~**Pix2Pix Model Integration**~~ - Complete! Model loaded and running inference
3. ✅ ~~**OCR Integration**~~ - Complete! Fast-plate-ocr extracts text from plates
4. **Results History**: Store and display recognition history in database
5. **Fine-tuning Interface**: Admin panel for model retraining with new data
6. **Batch Processing**: Upload and process multiple images simultaneously
7. **WebSocket Support**: Real-time streaming for camera simulation
8. **Performance Metrics**: Display model confidence and processing time

## 🐛 Troubleshooting

### Backend Issues

**Database connection error:**
- Ensure Docker Desktop is running
- Check if PostgreSQL container is running: `docker ps`
- Verify credentials in `backend/.env` match `.env.docker`
- Run `.\start.ps1` to automatically start everything

**Import errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- TensorFlow installation may take time (331.9 MB)

**Model not loading:**
- Ensure at least one `.keras` file is in `backend/ml_models/` for Pix2Pix
- OCR model (cct-xs-v1-global-model) downloads automatically on first run
- Check backend logs for "Found model file: ml_models/..." and "✓ ML model loaded successfully!"
- Check OCR logs for "✓ OCR model loaded successfully!"
- Verify model files are not corrupted

**OCR errors:**
- Ensure `fast-plate-ocr[onnx]` is installed: `pip install fast-plate-ocr[onnx]`
- First OCR run downloads the model (may take time)
- Check image quality - OCR works best on clear, properly cropped plates

### Frontend Issues

**Dependencies not found:**
```powershell
Remove-Item -Recurse -Force node_modules
npm install
```

**Port already in use:**
- Use `.\stop.ps1` to stop all processes
- Or change port in `vite.config.js`

### Docker Issues

**Docker Desktop not running:**
- Start Docker Desktop application
- Wait for it to fully start (whale icon in taskbar)

**PostgreSQL container won't start:**
```powershell
# Check logs
docker logs lpr_postgres

# Restart container
docker-compose restart

# Or use automation script
.\start.ps1
```


## 📚 Additional Documentation

- 📖 **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** - Complete guide for automation scripts
- 🐳 **[README_DOCKER.md](README_DOCKER.md)** - Docker setup and management
- 📋 **[details.md](details.md)** - Comprehensive technical documentation (Romanian)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Antonio Heasca**
- GitHub: [@antonioheasca4](https://github.com/antonioheasca4)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

**Note**: This is a development setup. For production deployment:
1. Use strong passwords in `.env.docker` (change `lpr_password_change_in_production`)
2. Generate secure SECRET_KEY in `backend/.env`
3. Use `docker-compose up -d --build` for complete containerization
4. Enable HTTPS/TLS
5. Set up proper database backups
6. Implement rate limiting
7. Use production-grade secrets management
8. Set DEBUG=False and use production builds