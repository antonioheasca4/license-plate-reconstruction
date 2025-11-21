# Docker Setup și Deployment

## 📦 Cerințe
- Docker Desktop instalat ([Download](https://www.docker.com/products/docker-desktop/))
- Docker Compose (inclus în Docker Desktop)

## 🚀 Pornire Rapidă

### Metoda 1: Mixed Development (RECOMANDAT) ⭐

Pornește Frontend + Backend local, PostgreSQL în Docker:

```powershell
.\start.ps1
# SAU dublu-click pe start.bat
```

**Avantaje:**
- ⚡ Start rapid
- ✅ Hot reload instant
- 🔧 Perfect pentru development

### Metoda 2: Full Docker (Production-ready)

Pornește Frontend + Backend + PostgreSQL toate în Docker:

```powershell
# Build și pornire toate serviciile
docker-compose up --build

# SAU în background (daemon)
docker-compose up -d --build
```

**Avantaje:**
- 🐳 Environment consistent
- 🔒 Izolare completă
- 🚀 Production-ready

---

## 📋 docker-compose.yml Explicat

Fișierul conține 3 servicii:

1. **postgres** - PostgreSQL 15 database
2. **backend** - FastAPI application  
3. **frontend** - React + Vite application

### Pornire Selectivă

```powershell
# Doar PostgreSQL (folosit de start.ps1)
docker-compose up -d postgres

# Toate serviciile (Frontend + Backend + PostgreSQL)
docker-compose up -d
```

---

## 🛠️ Setup Manual (Detaliat)

### 1. Configurare Environment Variables

```powershell
# Copiază template-ul și editează credențialele
copy .env.docker.example .env.docker

# Editează .env.docker cu parola ta securizată
# POSTGRES_PASSWORD=your_secure_password_here
```

### 2. Pornire Servicii Docker

```powershell
# Opțiunea 1: Doar PostgreSQL (pentru folosire cu start.ps1)
docker-compose up -d postgres

# Opțiunea 2: Toate serviciile (Frontend + Backend + PostgreSQL)
docker-compose up -d
```

**Ce se întâmplă:**
- `docker-compose up -d postgres` - pornește doar PostgreSQL (folosit de start.ps1)
- `docker-compose up -d` - pornește Frontend + Backend + PostgreSQL (toate în Docker)

**Containere create (opțiunea 2 - toate):**
- `lpr_postgres` - PostgreSQL 15 database
- `lpr_backend` - FastAPI backend (Python 3.12)
- `lpr_frontend` - React + Vite frontend (Node.js 18)

**Database settings:**
- Port: 5432
- User: `lpr_user`
- Password: `lpr_password_change_in_production` (configurabil în `.env.docker`)
- Database: `lpr_database`
- Volume persistent: `postgres_data`

### 3. Verificare Containere

```powershell
# Verifică ce containere rulează
docker ps

# Verifică logs pentru toate serviciile
docker-compose logs -f

# Logs pentru un serviciu specific
docker-compose logs -f postgres
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. Access URLs (când toate serviciile rulează)

- 🌐 Frontend: http://localhost:3000
- 🔥 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 🗄️ PostgreSQL: localhost:5432

---

## 🔄 Hot Reload și Modificări Cod

### ⭐ Cu start.ps1 (Development) - HOT RELOAD COMPLET

```powershell
.\start.ps1
```

**Frontend (React + Vite):**
- ✅ **Hot reload INSTANT**
- Modifici orice fișier `.jsx`, `.css`, `.tsx`, etc.
- Vite detectează automat schimbările
- Browser-ul se reîncarcă automat (< 1 secundă)
- **NU trebuie să repornești nimic!**

**Backend (FastAPI + Uvicorn):**
- ✅ **Auto-reload INSTANT**
- Modifici orice fișier `.py`
- Uvicorn rulează cu flag `--reload`
- Backend-ul se repornește automat (2-3 secunde)
- Vezi în terminal: `INFO: Application startup complete`
- **NU trebuie să repornești manual!**

**PostgreSQL:**
- ✅ Datele persistă în volume Docker `postgres_data`
- Schimbările în schema (models.py) se aplică automat via SQLAlchemy

### ⚠️ Cu docker-compose up (Production) - REBUILD NECESAR

```powershell
docker-compose up -d
```

**Problemă:** Codul este copiat în imagine la build. Modificările locale NU se reflectă automat.

**După modificări în Frontend:**
```powershell
# Restart simplu NU e suficient!
docker-compose restart frontend  # ❌ Nu funcționează

# Trebuie REBUILD:
docker-compose up -d --build frontend  # ✅ Corect
```

**După modificări în Backend:**
```powershell
# Trebuie REBUILD:
docker-compose up -d --build backend  # ✅ Corect

# SAU rebuild ambele:
docker-compose up -d --build
```

**De ce?** Dockerfile-urile copiază codul la build (`COPY . /app`). Modificările ulterioare din filesystem-ul local nu afectează containerele care rulează.

### 📊 Comparație Hot Reload

| Aspect | start.ps1 | docker-compose up |
|--------|-----------|-------------------|
| **Frontend changes** | ⚡ Instant (< 1s) | 🔄 Rebuild (~10-15s) |
| **Backend changes** | ⚡ Auto-reload (2-3s) | 🔄 Rebuild (~5-10s) |
| **CSS/Style changes** | ⚡ Instant | 🔄 Rebuild |
| **Dependencies (npm/pip)** | 🔄 Reinstall manual | 🔄 Rebuild image |
| **Workflow** | ✅ Edit → Save → See | ⚠️ Edit → Build → Wait |

### 🎯 Recomandare Finală

**Pentru development zilnic (modifici cod des):**
```powershell
.\start.ps1  # ⭐ HOT RELOAD - productivitate maximă!
```

**Pentru testing environment production:**
```powershell
docker-compose up -d --build  # Simulare production
```

---

## 🛠️ Comenzi Utile

### Oprire Aplicație
```powershell
# Folosește scriptul automat
.\stop.ps1

# Sau manual: Ctrl+C în terminalul backend-ului
```

### Stop Servicii
```powershell
# Stop toate serviciile (păstrează datele)
docker-compose down

# Stop și șterge datele (ATENȚIE: șterge baza de date!)
docker-compose down -v

# SAU folosește scripturile
.\stop.ps1              # Stop local services
.\stop.ps1 -RemoveDocker  # Stop + Docker down
.\stop.ps1 -RemoveDocker -RemoveData  # Stop + Docker down -v
```

### Restart Servicii
```powershell
# Restart toate serviciile Docker
docker-compose restart

# Restart un serviciu specific
docker-compose restart postgres
docker-compose restart backend

# SAU restart cu start.ps1
.\start.ps1
```

### Acces la PostgreSQL CLI
```powershell
docker exec -it lpr_postgres psql -U lpr_user -d lpr_database
```

Comenzi utile în psql:
```sql
-- Listare tabele
\dt

-- Descriere tabelă users
\d users

-- Listare utilizatori
SELECT * FROM users;

-- Ieșire
\q
```

### Vizualizare Logs Real-time
```powershell
# Logs pentru PostgreSQL
docker-compose logs -f postgres

# Logs pentru toate serviciile
docker-compose logs -f
```

## 📊 Configurare Bază de Date

### Variabile de Mediu (.env)

```env
DATABASE_URL=postgresql://lpr_user:lpr_password@localhost:5432/lpr_database
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Modificare Credentials

**Metoda Corectă (cu .env.docker):**

1. Editează `.env.docker`:
```env
POSTGRES_USER=new_user
POSTGRES_PASSWORD=new_secure_password
POSTGRES_DB=new_database
```

2. Editează `backend/.env`:
```env
DATABASE_URL=postgresql://new_user:new_secure_password@localhost:5432/new_database
```

3. Recreează containerul:
```powershell
docker-compose down -v
docker-compose up -d
```

**IMPORTANT:** Nu edita niciodată `docker-compose.yml` pentru credentials!

## 💾 Volume și Persistență

Datele sunt stocate în volume Docker numit `postgres_data`:

```powershell
# Listare volumes
docker volume ls

# Inspecție volume
docker volume inspect license-plate-reconstruction_postgres_data
```

**Important**: Atâta timp cât volume-ul există, datele vor persista chiar dacă oprești sau ștergi containerul.

---

## 🔧 Troubleshooting

### Serviciile nu pornesc
```powershell
# Verifică logs pentru erori
docker-compose logs

# Logs pentru un serviciu specific
docker-compose logs postgres
docker-compose logs backend
docker-compose logs frontend

# Verifică dacă porturile sunt libere
netstat -ano | findstr :5432   # PostgreSQL
netstat -ano | findstr :8000   # Backend
netstat -ano | findstr :3000   # Frontend

# SAU folosește scriptul automat
.\start.ps1
```

### Backend nu se conectează la PostgreSQL
```powershell
# Verifică dacă PostgreSQL este ready
docker exec lpr_postgres pg_isready -U lpr_user

# Testează conexiunea
docker exec -it lpr_postgres psql -U lpr_user -d lpr_database -c "SELECT 1;"

# SAU pornește cu scriptul (face toate verificările automat)
.\start.ps1
```

### Resetare completă
```powershell
# Oprește și șterge tot (container + volume)
.\stop.ps1 -RemoveDocker -RemoveData

# SAU manual
docker-compose down -v

# Pornește din nou
.\start.ps1

# Backend va recrea tabelele automat
```

## 📈 Monitoring

### Verificare Conexiuni Active
```powershell
docker exec -it lpr_postgres psql -U lpr_user -d lpr_database -c "SELECT count(*) FROM pg_stat_activity;"
```

### Dimensiune Bază de Date
```powershell
docker exec -it lpr_postgres psql -U lpr_user -d lpr_database -c "SELECT pg_size_pretty(pg_database_size('lpr_database'));"
```

### Backup Bază de Date
```powershell
# Backup
docker exec lpr_postgres pg_dump -U lpr_user lpr_database > backup.sql

# Restore
type backup.sql | docker exec -i lpr_postgres psql -U lpr_user lpr_database
```

## 🎯 Arhitectura Docker

### Metoda 1: Mixed (Development) - start.ps1 ⭐

```
┌─────────────────────────────────────────┐
│     Host Machine (Windows)              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Frontend (Port 3000)            │  │
│  │  - React + Vite                  │  │
│  │  - npm run dev                   │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Backend (Port 8000)             │  │
│  │  - FastAPI Application           │  │
│  │  - SQLAlchemy ORM                │  │
│  └──────────────┬───────────────────┘  │
│                 │ localhost:5432       │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │  Docker Container                │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │  PostgreSQL 15             │  │  │
│  │  │  - Port: 5432              │  │  │
│  │  │  - User: lpr_user          │  │  │
│  │  │  - DB: lpr_database        │  │  │
│  │  └────────────┬───────────────┘  │  │
│  │               │                   │  │
│  │               ▼                   │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │  Volume: postgres_data     │  │  │
│  │  │  (Persistent Storage)      │  │  │
│  │  └────────────────────────────┘  │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Caracteristici:**
- Frontend și Backend rulează LOCAL (pe host machine)
- Doar PostgreSQL în Docker container
- Hot reload instant pentru development
- Acces direct la cod pentru debugging

---

### Metoda 2: Fully Containerized (Production) - docker-compose up

```
┌─────────────────────────────────────────┐
│     Docker Network (lpr_network)        │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Frontend Container              │  │
│  │  - Node.js 18                    │  │
│  │  - Port 3000 → Host 3000        │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Backend Container               │  │
│  │  - Python 3.12                   │  │
│  │  - Port 8000 → Host 8000        │  │
│  └──────────────┬───────────────────┘  │
│                 │ Internal network     │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │  PostgreSQL Container            │  │
│  │  - Port 5432 → Host 5432        │  │
│  │  - Volume: postgres_data         │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Caracteristici:**
- Toate serviciile rulează în containere Docker
- Izolare completă între servicii
- Environment consistent (production-ready)
- Rebuild necesar pentru schimbări de cod

---

## ✅ Checklist Setup

### ⚡ Setup Rapid - start.ps1 (Development) ⭐
- [ ] Docker Desktop instalat și pornit
- [ ] Python 3.9+ și Node.js 18+ instalate
- [ ] Rulat `.\start.ps1` (sau dublu-click `start.bat`)
- [ ] Așteptat să pornească toate serviciile
- [ ] Verificat frontend la http://localhost:3000
- [ ] Verificat backend la http://localhost:8000/docs
- [ ] Testat înregistrare/login în aplicație

### 🐳 Setup Docker Complet (Production-ready)
- [ ] Docker Desktop instalat și pornit
- [ ] Creat `.env.docker` din `.env.docker.example`
- [ ] Creat `backend/.env` din `backend/.env.example`
- [ ] Rulat `docker-compose build` (prima dată)
- [ ] Rulat `docker-compose up -d`
- [ ] Verificat containere: `docker ps`
- [ ] Verificat frontend la http://localhost:3000
- [ ] Verificat backend la http://localhost:8000/docs
- [ ] Testat înregistrare/login în aplicație

---

## 📚 Resurse Adiționale

- 📖 **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** - Ghid complet pentru scripturile de automatizare
- 🔒 **[ENV_BEST_PRACTICES.md](ENV_BEST_PRACTICES.md)** - Best practices pentru securitate
- 🧪 **[TEST_SETUP.md](TEST_SETUP.md)** - Checklist pentru verificare setup
- 📋 **[README.md](README.md)** - Documentație generală proiect
