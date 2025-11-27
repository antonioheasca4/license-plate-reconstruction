# 🚀 Automation Scripts - Ghid de Utilizare

## 📋 Ce Scripturi Ai Disponibile

### 1. **start.ps1** / **start.bat** (Windows) / **start.sh** (Linux/macOS) - Start Aplicația ⭐ (RECOMANDAT)
Pornește TOTUL: Frontend + Backend + PostgreSQL

### 2. **stop.ps1** / **stop.bat** (Windows) / **stop.sh** (Linux/macOS) - Stop Aplicația
Oprește frontend, backend și opțional PostgreSQL

### 3. **docker-compose.yml** - Configurație Docker Completă
Contine 3 servicii: PostgreSQL, Backend, Frontend
- `start.ps1` pornește doar PostgreSQL din el
- `docker-compose up` pornește toate serviciile (Production-ready)

---

## 🎯 Metoda 1: Scripturi Automate (RECOMANDAT pentru Development)

### Pornire Aplicație ⭐

**Windows:**
```powershell
# Metodă 1: PowerShell direct
.\start.ps1

# Metodă 2: Double-click pe start.bat
# (Windows Explorer → dublu-click start.bat)
```

**Linux/macOS:**
```bash
# Fă scriptul executabil (prima dată)
chmod +x start.sh

# Pornește aplicația
./start.sh
```

**Ce face:**
1. ✅ Verifică Docker Desktop
2. ✅ Pornește PostgreSQL container (dacă nu rulează)
3. ✅ Așteaptă PostgreSQL să fie ready
4. ✅ Pornește React Frontend (background, port 3000)
5. ✅ Pornește FastAPI Backend (foreground, port 8000)
6. ✅ Afișează toate URL-urile

**URLs după pornire:**
- 🌐 Frontend: http://localhost:3000
- 🔥 Backend: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

### Oprire Aplicație

**Windows:**
```powershell
# Oprește Frontend + Backend, păstrează PostgreSQL și datele
.\stop.ps1

# Oprește doar backend + frontend, lasă PostgreSQL pornit
.\stop.ps1 -KeepDocker

# Oprește tot inclusiv PostgreSQL (păstrează datele)
.\stop.ps1

# Oprește tot și ȘTERGE datele (ATENȚIE!)
.\stop.ps1 -RemoveData
```

**Linux/macOS:**
```bash
# Oprește Frontend + Backend, păstrează PostgreSQL și datele
./stop.sh

# Oprește doar backend + frontend, lasă PostgreSQL pornit
./stop.sh --keep-docker

# Oprește tot și ȘTERGE datele (ATENȚIE!)
./stop.sh --remove-data
```

**SAU mai simplu:** Ctrl+C în terminal (oprește doar ce rulează în foreground)

### Avantaje
✅ Un singur command pentru TOTUL (Frontend + Backend + DB)  
✅ Verificări automate (Docker running, venv exists, node_modules)  
✅ Așteaptă PostgreSQL să fie ready  
✅ Mesaje colorate și clare  
✅ Frontend în background, Backend în foreground  
✅ Funcționează cu venv local (development rapid)  
✅ Auto-instalare dependențe dacă lipsesc

---

## 🐳 Metoda 2: Docker Compose (TOTUL în Docker)

### Setup
```powershell
# Prima dată: build images (Frontend + Backend + PostgreSQL)
docker-compose build

# Pornire TOTUL (3 containere)
docker-compose up -d

# Verificare logs
docker-compose logs -f

# Logs pentru un serviciu specific
docker-compose logs -f frontend
docker-compose logs -f backend

# Oprire
docker-compose down
```

**Containere create:**
- `lpr_postgres` - PostgreSQL database
- `lpr_backend` - FastAPI backend
- `lpr_frontend` - React + Vite frontend

### Avantaje
✅ Environment consistent (același Python, dependencies)  
✅ Izolare completă  
✅ Gata pentru producție  
✅ Ușor de distribuit (nu trebuie venv local)

### Dezavantaje
❌ **Rebuild OBLIGATORIU la fiecare schimbare de cod**  
❌ Mai lent pentru development (10-15 sec rebuild)  
❌ Hot-reload NU funcționează (codul e copiat în imagine la build)

**Exemplu după modificare cod:**
```powershell
# Modifici frontend/src/App.jsx
docker-compose restart frontend  # ❌ NU se vede schimbarea!
docker-compose up -d --build frontend  # ✅ Rebuild necesar
```

---

## 📊 Comparație Metode

| Aspect | start.ps1/start.sh | docker-compose up |
|--------|-----------|-------------------|
| **Ce pornește** | Frontend + Backend + PostgreSQL | Toate 3 în containere |
| **Unde rulează** | Frontend & Backend: PC / PostgreSQL: Docker | Totul în Docker |
| **Platforme** | ✅ Windows, Linux, macOS | ✅ Windows, Linux, macOS |
| **Viteză start** | ⚡ Rapid (3-5 sec) | 🐌 Mai lent (10-15 sec) |
| **Development** | ✅ Excelent | ⚠️ OK, dar rebuild frecvent |
| **Production** | ❌ Nu recomandat | ✅ Ideal |
| **Hot reload** | ✅ Instant (Frontend + Backend) | ⚠️ Backend necesită rebuild |
| **Izolare** | ⚠️ Parțială (doar DB) | ✅ Completă (tot) |
| **Setup** | ⚡ Simplu | 🔧 Build initial |
| **URL-uri** | localhost:3000, localhost:8000 | Aceleași |

---

## 🎯 Recomandări

### Pentru Development (Zi cu Zi) ⭐

**Windows:**
```powershell
# Pornește totul instant!
.\start.ps1
# SAU dublu-click pe start.bat
```

**Linux/macOS:**
```bash
# Pornește totul instant!
./start.sh
```

### Pentru Testing (Simulare Production)
```powershell
# Totul în Docker, environment izolat
docker-compose up
```

### Pentru Production
```powershell
# Deploy cu Docker Compose
docker-compose up -d --build
```

---

## 🔧 Configurare PowerShell Execution Policy (Prima Dată)

Dacă `.\start.ps1` dă eroare de "execution policy":

```powershell
# Opțiunea 1: Permanent (recomandat pentru developer)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Opțiunea 2: O singură dată
powershell.exe -ExecutionPolicy Bypass -File .\start.ps1

# Opțiunea 3: Folosește start.bat (bypass automat)
.\start.bat
```

---

## 📝 Workflow Tipic Development

### Dimineața (Start lucru)

**Windows:**
```powershell
# Pornește aplicația cu un singur command!
.\start.ps1
# SAU dublu-click start.bat
```

**Linux/macOS:**
```bash
./start.sh
```

**Output:**
```
🚀 Starting License Plate Reconstruction System...
   (Frontend + Backend + PostgreSQL)

📦 Checking Docker...
✅ Docker is running

🐘 Starting PostgreSQL...
✅ PostgreSQL ready!

⚛️  Starting React Frontend...
✅ Frontend started in background

🔥 Starting FastAPI Backend...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 URLs:
   Frontend:  http://localhost:3000
   Backend:   http://localhost:8000
   API Docs:  http://localhost:8000/docs

Press Ctrl+C to stop everything...

INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Apoi deschizi browser:**
- http://localhost:3000 → aplicația ta completă!

### Seara (Stop lucru)

**Toate platformele:**
```bash
# Ctrl+C în terminal (oprește Frontend + Backend)
```

**Windows - Opțional oprește PostgreSQL:**
```powershell
.\stop.ps1              # Oprește tot, păstrează datele
# SAU
.\stop.ps1 -KeepDocker  # Lasă PostgreSQL pornit pentru mâine
```

**Linux/macOS - Opțional oprește PostgreSQL:**
```bash
./stop.sh              # Oprește tot, păstrează datele
# SAU
./stop.sh --keep-docker  # Lasă PostgreSQL pornit pentru mâine
```

---

## 🚨 Troubleshooting

### Eroare: "Docker Desktop is not running"
```powershell
# Soluție: pornește Docker Desktop
# Windows: Start Menu → Docker Desktop
```

### Eroare: "Virtual environment not found"
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
.\start.ps1
```

### Eroare: "PostgreSQL failed to start"
```powershell
# Verifică logs
docker logs lpr_postgres

# Restart container
docker-compose restart postgres

# SAU recreează
docker-compose down
docker-compose up -d
```

### Backend nu se conectează la PostgreSQL
```powershell
# Verifică DATABASE_URL în backend/.env
# Trebuie să match-uiască cu .env.docker
```

---

## 🎉 Exemple Rapide

### Start Aplicația (Frontend + Backend + PostgreSQL) ⭐

**Windows:**
```powershell
.\start.ps1
# SAU dublu-click: start.bat
```

**Linux/macOS:**
```bash
./start.sh
```

### Start complet izolat în Docker (toate 3 containere)
```powershell
docker-compose up --build
```

### Restart după schimbări cod (Docker)
```powershell
# Restart backend container
docker-compose restart backend

# Restart frontend container
docker-compose restart frontend
```

### Cleanup complet (șterge tot)
```powershell
# Opțiunea 1: Folosește scriptul
.\stop.ps1 -RemoveDocker -RemoveData

# Opțiunea 2: Docker direct
docker-compose down -v
```

---

## ✅ Best Practices

1. **Development Rapid**: Folosește `.\start.ps1` (Frontend + Backend + PostgreSQL) ⭐
2. **Testing**: Folosește `docker-compose up` (environment consistent, complet izolat)
3. **Production**: Folosește `docker-compose up -d --build` cu variabile securizate
4. **Cleanup**: Rulează `.\stop.ps1` la sfârșit de zi (economisește resurse)
5. **Git**: Nu uita să adaugi `.env*` în `.gitignore` (deja configurat)

---

**TL;DR:**
- **Start Aplicația (Windows)** → `.\start.ps1` sau dublu-click `start.bat` ⭐
- **Start Aplicația (Linux/macOS)** → `./start.sh` ⭐
- **Totul în Docker** → `docker-compose up`
- **Stop** → `Ctrl+C` sau `.\stop.ps1` (Windows) / `./stop.sh` (Linux/macOS)
