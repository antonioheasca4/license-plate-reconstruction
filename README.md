# License Plate Recognition System

A full-stack web application for Automatic License Plate Recognition (ALPR) with image reconstruction using Pix2Pix deep learning model. Built with FastAPI (Python) backend and React frontend, featuring JWT authentication and PostgreSQL database.

## 🏗️ Project Structure

```
license-plate-reconstruction/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application entry point
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # Authentication logic
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
│   │   │   └── Dashboard.jsx  # Main app with upload
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── Dockerfile          # Frontend Docker image
│   └── .env               # Environment variables
│
├── docker-compose.yml      # Docker orchestration (3 services)
├── .env.docker             # Docker environment variables
├── .env.docker.example     # Docker env template
├── start.ps1               # Start script (Development)
├── start.bat               # Windows batch wrapper
├── stop.ps1                # Stop script
├── stop.bat                # Windows batch wrapper
├── AUTOMATION_GUIDE.md     # Automation documentation
├── README_DOCKER.md        # Docker setup guide
└── ENV_BEST_PRACTICES.md   # Security best practices
```

## ✨ Features

- ✅ **User Authentication**: JWT-based authentication with secure password hashing (bcrypt)
- ✅ **User Registration & Login**: Complete user management system
- ✅ **Protected Routes**: Frontend and backend route protection
- ✅ **PostgreSQL Database**: Robust relational database with SQLAlchemy ORM (Dockerized)
- ✅ **License Plate Reconstruction**: Pix2Pix deep learning model for image enhancement
- ✅ **Image Upload**: Drag & drop or click to upload license plate images
- ✅ **Real-time Inference**: Process images and view reconstructed results instantly
- ✅ **Side-by-Side Comparison**: Visual comparison of original vs reconstructed images
- ✅ **Modern UI**: Responsive React interface with custom styling
- ✅ **CORS Configured**: Secure cross-origin resource sharing
- ✅ **Docker Support**: Full containerization with docker-compose
- ✅ **Automation Scripts**: One-command start/stop for development
- ✅ **Hot Reload**: Instant updates during development (frontend & backend)
- 🔄 **Coming Soon**: OCR text extraction, results history, model fine-tuning

## 🚀 Prerequisites

Before you begin, ensure you have the following installed:

### Required for Development (start.ps1)
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/)) - For PostgreSQL container
- **Python 3.9+** ([Download](https://www.python.org/downloads/)) - For backend (requires TensorFlow 2.20.0)
- **Node.js 18+** and npm ([Download](https://nodejs.org/)) - For frontend

### Required for Production (docker-compose up)
- **Docker Desktop** only - All services run in containers

## 📦 Installation & Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/antonioheasca4/license-plate-reconstruction.git
cd license-plate-reconstruction
```

### 2. Backend Setup

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

# The .env file is already configured for Docker PostgreSQL
# DATABASE_URL=postgresql://lpr_user:lpr_password_change_in_production@localhost:5432/lpr_database
```

**ML Dependencies Included**:
- TensorFlow 2.20.0 (Pix2Pix model)
- Pillow 10.2.0 (Image processing)
- NumPy 1.26.3 (Array operations)

**Important**: For production, generate a secure SECRET_KEY:

```powershell
# Generate a secure random key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and update `SECRET_KEY` in your `.env` file.

### 3. Docker Setup (PostgreSQL)

```powershell
# Create Docker environment file from example
copy .env.docker.example .env.docker

# Configure .env.docker with PostgreSQL credentials (already pre-configured)
# POSTGRES_USER=lpr_user
# POSTGRES_PASSWORD=lpr_password_change_in_production
# POSTGRES_DB=lpr_database
```

**Note**: The `start.ps1` script will automatically start PostgreSQL container when you run the application.

### 4. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file from example
copy .env.example .env
```

### 5. Add ML Model

Place your trained Pix2Pix model in the backend:

```powershell
# Copy any .keras model file to:
backend/ml_models/

# Examples:
backend/ml_models/generator_256x128noSkew.keras
backend/ml_models/model.keras
backend/ml_models/pix2pix_generator.keras
```

**Model Requirements**:
- Format: `.keras` (TensorFlow/Keras)
- Input shape: (batch, 128, 256, 3)
- Output shape: (batch, 128, 256, 3)
- Type: Pix2Pix Generator for license plate reconstruction

The first `.keras` file found will be automatically loaded at backend startup.

## 🎯 Running the Application

### Quick Start (Recommended) ⭐

**Option 1: Double-click to start**
```
Double-click: start.bat
```

**Option 2: PowerShell command**
```powershell
.\start.ps1
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
- Or run: `.\stop.ps1`

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

3. **Upload Another**:
   - Click "Upload Another Image" to process more plates

### 4. Test Features

- View your profile information on the Dashboard
- Upload multiple license plate images for reconstruction
- Try degraded/blurry images to see reconstruction quality
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
- `GET /api/model/status` - Check ML model status

### Using the API (cURL Examples)

**Register:**
```powershell
$body = @{
    email = "test@example.com"
    username = "testuser"
    password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" -Method Post -Body $body -ContentType "application/json"
```

**Login:**
```powershell
$formData = @{
    username = "testuser"
    password = "password123"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -Body $formData
```

**Access Protected Route:**
```powershell
$token = "your_access_token_here"
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Headers $headers
```

**Upload Image for Reconstruction:**
```powershell
$token = "your_access_token_here"
$headers = @{
    Authorization = "Bearer $token"
}

$filePath = "path/to/license_plate.jpg"
$boundary = [System.Guid]::NewGuid().ToString()

Invoke-RestMethod -Uri "http://localhost:8000/api/inference" -Method Post -Headers $headers -InFile $filePath -ContentType "multipart/form-data"
```

**Check Model Status:**
```powershell
$token = "your_access_token_here"
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/model/status" -Headers $headers
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
3. **OCR Integration**: Extract and display text from license plates
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
- Ensure at least one `.keras` file is in `backend/ml_models/`
- Check backend logs for "Found model file: ml_models/..." and "✓ ML model loaded successfully!"
- Verify model file is not corrupted

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

### CORS Issues

If you get CORS errors:
- Ensure backend is running on port 8000
- Ensure frontend is running on port 3000
- Check `ALLOWED_ORIGINS` in backend `.env`

## 📚 Additional Documentation

- 📖 **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** - Complete guide for automation scripts
- 🐳 **[README_DOCKER.md](README_DOCKER.md)** - Docker setup and management
- 🔒 **[ENV_BEST_PRACTICES.md](ENV_BEST_PRACTICES.md)** - Security best practices
- 🧪 **[TEST_SETUP.md](TEST_SETUP.md)** - Verification checklist
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