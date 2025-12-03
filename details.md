# License Plate Reconstruction - Documentație Tehnică Detaliată

## 📋 Cuprins
1. [Prezentare Generală](#prezentare-generală)
2. [Arhitectura Aplicației](#arhitectura-aplicației)
3. [Backend - FastAPI](#backend---fastapi)
4. [Frontend - React](#frontend---react)
5. [Baza de Date](#baza-de-date)
6. [Sistem de Autentificare](#sistem-de-autentificare)
7. [Comunicarea Frontend-Backend](#comunicarea-frontend-backend)
8. [Tehnologii și Dependențe](#tehnologii-și-dependențe)
9. [Fluxul de Date](#fluxul-de-date)
10. [Structura Fișierelor](#structura-fișierelor)

---

## 🎯 Prezentare Generală

**Numele Proiectului:** License Plate Reconstruction System  
**Scop:** Aplicație web full-stack pentru recunoașterea și reconstrucția plăcuțelor de înmatriculare folosind deep learning (Pix2Pix model + fast-plate-ocr)  
**Stadiu Actual:** Sistem complet funcțional cu autentificare, reconstrucție imagini și OCR

### Caracteristici Principale
- ✅ Autentificare JWT completă (login/register/logout)
- ✅ Rutare protejată pe frontend și backend
- ✅ Validare complexă a datelor
- ✅ Management securizat al sesiunilor
- ✅ Interfață responsive modernă
- ✅ Upload și reconstrucție imagini cu Pix2Pix
- ✅ OCR pentru extragere text din plăcuțe (fast-plate-ocr)
- ✅ Vizualizare rapoarte PDF (OCR, PSNR/SSIM metrics)
- ✅ Scripturi cross-platform (Windows/Linux/macOS)
- ✅ Istoric procesări (ultimele 10 imagini cu rezultate OCR)
- ✅ Persistență stare între pagini (localStorage)
- 🔄 În dezvoltare: batch processing, fine-tuning model

---

## 🏗️ Arhitectura Aplicației

### Model Arhitectural: Client-Server (3-Tier Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  React Frontend (Vite)                                    │   │
│  │  - Port: 3000                                             │   │
│  │  - React Router pentru navigare                           │   │
│  │  - Context API pentru state management                    │   │
│  │  - Axios pentru HTTP requests                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/HTTPS
                         (Axios + Proxy Vite)
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend                                          │   │
│  │  - Port: 8000                                             │   │
│  │  - REST API endpoints                                     │   │
│  │  - JWT authentication                                     │   │
│  │  - Business logic layer                                   │   │
│  │  - CORS middleware                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SQLite Database (development)                            │   │
│  │  PostgreSQL (production-ready)                            │   │
│  │  - File: lpr_database.db                                  │   │
│  │  - Tabele: users, image_history                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend - FastAPI

### Structura Backend

```
backend/
├── main.py          # Entry point și endpoint-uri REST
├── database.py      # Configurare SQLAlchemy și conexiune DB
├── models.py        # Modele SQLAlchemy (ORM)
├── schemas.py       # Validare Pydantic (Request/Response)
├── auth.py          # Logică JWT și autentificare
├── ocr_service.py   # Serviciu OCR (fast-plate-ocr)
├── requirements.txt # Dependențe Python
├── ml_models/       # Modele ML (Pix2Pix .keras files)
└── __pycache__/     # Cache Python (generat automat)
```

### 1. **main.py** - Aplicația Principală

#### Configurare și Middleware
```python
app = FastAPI(title="License Plate Recognition API", version="1.0.0")

# CORS Middleware - permite comunicarea cu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Endpoint-uri Disponibile

| Method | Endpoint | Descriere | Autentificare |
|--------|----------|-----------|---------------|
| GET | `/` | Root - informații API | Nu |
| POST | `/api/auth/register` | Înregistrare utilizator nou | Nu |
| POST | `/api/auth/login` | Login și obținere token JWT | Nu |
| GET | `/api/auth/me` | Informații utilizator curent | Da (JWT) |
| GET | `/api/protected` | Rută protejată (exemplu) | Da (JWT) |
| POST | `/api/inference` | Upload și reconstrucție imagine Pix2Pix | Da (JWT) |
| POST | `/api/ocr` | Extrage text din plăcuță cu OCR | Da (JWT) |
| GET | `/api/model/status` | Status modele ML (Pix2Pix + OCR) | Da (JWT) |
| POST | `/api/history` | Salvează procesare în istoric | Da (JWT) |
| GET | `/api/history` | Obține istoric procesări (limit=10) | Da (JWT) |
| PUT | `/api/history/{id}` | Actualizează procesare cu OCR | Da (JWT) |
| DELETE | `/api/history/{id}` | Șterge procesare din istoric | Da (JWT) |

#### Logica Endpoint-urilor

**1. Register (`/api/auth/register`)**
- Validează username (fără @, doar litere/cifre/underscore/hyphen)
- Verifică unicitatea email-ului
- Verifică unicitatea username-ului (case-insensitive)
- Hash-uiește parola cu bcrypt
- Creează utilizator în DB
- Returnează obiect UserResponse

**2. Login (`/api/auth/login`)**
- Primește OAuth2PasswordRequestForm (username + password)
- Caută user după email SAU username
- Verifică parola hash-uită
- Generează JWT token (expirare 30 min)
- Returnează token + token_type

**3. Get Current User (`/api/auth/me`)**
- Extrage token din header Authorization
- Decodifică și validează JWT
- Returnează informații complete user

### 2. **database.py** - Configurare Bază de Date

```python
DATABASE_URL = "sqlite:///./lpr_database.db"  # Development
# DATABASE_URL = "postgresql://user:pass@host/db"  # Production

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency injection pentru sesiuni DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Caracteristici:**
- Suport SQLite (development) și PostgreSQL (production)
- Session factory pattern
- Dependency injection cu FastAPI
- Gestionare automată închidere conexiuni

### 3. **models.py** - Modele Bază de Date (SQLAlchemy ORM)

**User Model**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relații
    image_history = relationship("ImageHistory", back_populates="user", cascade="all, delete-orphan")
```

**ImageHistory Model**
```python
class ImageHistory(Base):
    __tablename__ = "image_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_image = Column(Text, nullable=False)  # Base64
    reconstructed_image = Column(Text, nullable=True)  # Base64
    ocr_text_original = Column(String, nullable=True)
    ocr_text_reconstructed = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relații
    user = relationship("User", back_populates="image_history")
```

**Câmpuri User:**
- `id`: Primary key, auto-increment
- `email`: Unic, indexat pentru căutări rapide
- `username`: Unic, indexat, case-insensitive
- `hashed_password`: Bcrypt hash (nu se stochează plaintext!)
- `is_active`: Flag pentru activare/dezactivare cont
- `is_admin`: Role-based access control
- `created_at`: Timestamp automat la creare
- `updated_at`: Timestamp automat la modificare

**Câmpuri ImageHistory:**
- `id`: Primary key, auto-increment
- `user_id`: Foreign key către users (cascade delete)
- `original_image`: Imagine originală (base64 în Text field)
- `reconstructed_image`: Imagine reconstruită (base64, nullable)
- `ocr_text_original`: Text OCR din imagine originală (nullable)
- `ocr_text_reconstructed`: Text OCR din imagine reconstruită (nullable)
- `created_at`: Timestamp automat la creare

### 4. **schemas.py** - Validare și Serializare (Pydantic)

**UserCreate** - Input pentru înregistrare
```python
class UserCreate(BaseModel):
    email: EmailStr  # Validare automată format email
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    
    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        # Regex: doar a-z, A-Z, 0-9, _, -
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username invalid')
        return v
```

**UserResponse** - Output pentru client
```python
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    # NU include hashed_password (securitate!)
```

**Token** - Răspuns login
```python
class Token(BaseModel):
    access_token: str  # JWT token
    token_type: str    # "bearer"
```

**ImageHistoryCreate** - Input pentru salvare istoric
```python
class ImageHistoryCreate(BaseModel):
    original_image: str  # Base64 encoded
    reconstructed_image: Optional[str] = None  # Base64, nullable
    ocr_text_original: Optional[str] = None
    ocr_text_reconstructed: Optional[str] = None
```

**ImageHistoryResponse** - Output istoric individual
```python
class ImageHistoryResponse(BaseModel):
    id: int
    user_id: int
    original_image: str
    reconstructed_image: Optional[str]
    ocr_text_original: Optional[str]
    ocr_text_reconstructed: Optional[str]
    created_at: datetime
```

**ImageHistoryList** - Listă istoric
```python
class ImageHistoryList(BaseModel):
    items: List[ImageHistoryResponse]
    total: int
```

### 5. **auth.py** - Sistem de Autentificare

#### Configurare JWT
```python
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
```

#### Funcții Principale

**1. Hashing Parole (bcrypt)**
```python
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), 
                         hashed_password.encode('utf-8'))
```

**2. Generare JWT Token**
```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**3. Extragere User din Token**
```python
def get_current_user(token: str = Depends(oauth2_scheme), 
                     db: Session = Depends(get_db)) -> User:
    # Decodifică JWT
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    # Caută user în DB
    user = db.query(User).filter(User.email == email).first()
    return user
```

---

## ⚛️ Frontend - React

### Structura Frontend

```
frontend/
├── src/
│   ├── components/
│   │   ├── PrivateRoute.jsx    # HOC pentru rute protejate
│   │   └── ImageUploader.jsx   # Component upload/reconstrucție
│   ├── contexts/
│   │   └── AuthContext.jsx     # State management autentificare
│   ├── pages/
│   │   ├── Login.jsx           # Pagină login
│   │   ├── Register.jsx        # Pagină înregistrare
│   │   ├── Dashboard.jsx       # Pagină dashboard (protejată)
│   │   ├── Metrics.jsx         # Pagină metrici cu PDF viewer
│   │   ├── History.jsx         # Pagină istoric procesări
│   │   ├── Auth.css            # Stiluri autentificare
│   │   ├── Dashboard.css       # Stiluri dashboard
│   │   └── History.css         # Stiluri istoric
│   ├── App.jsx                 # Componenta principală
│   ├── App.css                 # Stiluri globale
│   ├── main.jsx                # Entry point
│   └── index.css               # Stiluri bază
├── index.html
├── package.json
└── vite.config.js
```

### 1. **App.jsx** - Componenta Root

```jsx
function App() {
  return (
    <AuthProvider>           {/* Context global pentru autentificare */}
      <Router>               {/* React Router pentru navigare */}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={
            <PrivateRoute>   {/* Protecție rută */}
              <Dashboard />
            </PrivateRoute>
          }/>
          <Route path="/metrics" element={
            <PrivateRoute>
              <Metrics />
            </PrivateRoute>
          }/>
          <Route path="/history" element={
            <PrivateRoute>
              <History />
            </PrivateRoute>
          }/>
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
```

**Caracteristici:**
- AuthProvider înfășoară întreaga aplicație (state global)
- React Router v6 pentru navigare
- Redirecționare automată root → dashboard
- PrivateRoute pentru protecție

### 2. **AuthContext.jsx** - State Management

#### Structura Context
```javascript
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

#### State și Funcționalitate
```javascript
const [user, setUser] = useState(null);        // Utilizator curent
const [loading, setLoading] = useState(true);  // Loading state

useEffect(() => {
  // La mount, verifică dacă există token în localStorage
  const token = localStorage.getItem('token');
  if (token) fetchUser(token);
}, []);
```

#### Funcții Expuse

**1. Login**
```javascript
const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await axios.post('/api/auth/login', formData);
  const { access_token } = response.data;
  
  localStorage.setItem('token', access_token);  // Persistență
  await fetchUser(access_token);                // Populează user state
  
  return { success: true };
};
```

**2. Register**
```javascript
const register = async (email, username, password) => {
  await axios.post('/api/auth/register', { email, username, password });
  return { success: true };
};
```

**3. Logout**
```javascript
const logout = () => {
  localStorage.removeItem('token');  // Șterge token
  setUser(null);                     // Resetează state
};
```

**4. Fetch User**
```javascript
const fetchUser = async (token) => {
  const response = await axios.get('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` }
  });
  setUser(response.data);
};
```

### 3. **Login.jsx** - Pagină Login

**Funcționalitate:**
- Form cu username/email + password
- Validare input (required)
- Afișare erori din backend
- Mesaj success de la register (state passthrough)
- Loading state pentru button
- Redirecționare la dashboard după login

**Flow:**
1. User introduce credențiale
2. Submit → apel `login()` din context
3. Succes → navigate('/dashboard')
4. Eroare → afișare mesaj

### 4. **Register.jsx** - Pagină Înregistrare

**Validări Frontend:**
- Email valid (type="email")
- Username: min 3, max 50 caractere
- Username: doar `[a-zA-Z0-9_-]`
- Username: fără @ (validare explicită)
- Password: min 6 caractere
- Confirm password: matching

**Flow:**
1. User completează form
2. Validare frontend
3. Submit → apel `register()` din context
4. Succes → navigate('/login') cu mesaj success
5. Eroare → afișare mesaj

### 5. **Dashboard.jsx** - Pagină Protejată

**Conținut:**
- Navbar cu username și buton logout
- Welcome card cu detalii user:
  - Email
  - Username
  - Account status (Active/Inactive)
  - Role (Admin/User)
- Info card cu feature-uri viitoare

**Protecție:**
- Accesibilă doar prin `<PrivateRoute>`
- Verifică existența `user` din context
- Redirectează la login dacă nu autentificat

### 6. **PrivateRoute.jsx** - Protecție Rute

```jsx
const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  return user ? children : <Navigate to="/login" />;
};
```

**Logică:**
- Dacă loading → afișează loading screen
- Dacă user → renderează children (componenta protejată)
- Altfel → redirectează la /login

### 7. **vite.config.js** - Configurare Build Tool

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Backend URL
        changeOrigin: true,
      }
    }
  }
})
```

**Proxy Explicat:**
- Request-uri către `/api/*` sunt redirectate automat la `http://localhost:8000/api/*`
- Evită probleme CORS în development
- Permite apeluri relative: `axios.get('/api/auth/me')`

---

## 🗄️ Baza de Date

### Schema Actuală

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### Tipuri de Baze de Date Suportate

**1. SQLite (Development)**
- Fișier local: `lpr_database.db`
- Zero configurare
- Ideal pentru development și testing
- Limitări: concurență scăzută

**2. PostgreSQL (Production)**
- Connection string: `postgresql://user:pass@host:port/dbname`
- Performanță înaltă
- Suport pentru concurență
- Backup și replicare

### Configurare Dinamică

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./lpr_database.db"  # Default fallback
)
```

**Variabilă de Mediu (.env):**
```bash
# Development
DATABASE_URL=sqlite:///./lpr_database.db

# Production
DATABASE_URL=postgresql://user:password@localhost:5432/lpr_db
```

### Migrare Date (Viitor)

Pentru modificări schema, se recomandă **Alembic** (tool de migrare SQLAlchemy):
```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

---

## 🔐 Sistem de Autentificare

### Arhitectura Autentificării

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend   │         │   Backend    │         │   Database   │
│   (React)    │         │  (FastAPI)   │         │  (SQLite)    │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                        │
       │  1. POST /register     │                        │
       │  {email, user, pass}   │                        │
       │───────────────────────>│                        │
       │                        │  2. Hash password      │
       │                        │     (bcrypt)           │
       │                        │  3. INSERT user        │
       │                        │───────────────────────>│
       │                        │<───────────────────────│
       │  4. UserResponse       │                        │
       │<───────────────────────│                        │
       │                        │                        │
       │  5. POST /login        │                        │
       │  {username, password}  │                        │
       │───────────────────────>│                        │
       │                        │  6. SELECT user        │
       │                        │───────────────────────>│
       │                        │<───────────────────────│
       │                        │  7. Verify password    │
       │                        │     (bcrypt.checkpw)   │
       │                        │  8. Generate JWT       │
       │                        │     (jose)             │
       │  9. {access_token}     │                        │
       │<───────────────────────│                        │
       │  10. Store in          │                        │
       │      localStorage      │                        │
       │                        │                        │
       │  11. GET /api/auth/me  │                        │
       │      Authorization:    │                        │
       │      Bearer <token>    │                        │
       │───────────────────────>│                        │
       │                        │  12. Decode JWT        │
       │                        │      (jose.jwt.decode) │
       │                        │  13. SELECT user       │
       │                        │───────────────────────>│
       │                        │<───────────────────────│
       │  14. UserResponse      │                        │
       │<───────────────────────│                        │
```

### Flow Detaliat

#### 1. Înregistrare (Register)

**Frontend:**
```javascript
// 1. Validare frontend
if (!usernameRegex.test(username)) throw error;
if (password !== confirmPassword) throw error;

// 2. Trimitere request
const result = await register(email, username, password);

// 3. Redirect la login cu mesaj success
navigate('/login', { state: { message: 'Registration successful!' } });
```

**Backend:**
```python
# 1. Validare Pydantic (schemas.py)
UserCreate.model_validate(user_data)

# 2. Verificare duplicate (main.py)
if db.query(User).filter(User.email == email).first():
    raise HTTPException(400, "Email already registered")

# 3. Hash password (auth.py)
hashed_password = get_password_hash(password)

# 4. Creare user (main.py)
new_user = User(email=email, username=username, hashed_password=hashed_password)
db.add(new_user)
db.commit()

# 5. Returnare UserResponse
return new_user
```

#### 2. Login

**Frontend:**
```javascript
// 1. Creare FormData (OAuth2 standard)
const formData = new FormData();
formData.append('username', username);  // Poate fi email SAU username
formData.append('password', password);

// 2. POST request
const response = await axios.post('/api/auth/login', formData);
const { access_token } = response.data;

// 3. Stocare token
localStorage.setItem('token', access_token);

// 4. Fetch user data
await fetchUser(access_token);
```

**Backend:**
```python
# 1. Căutare user (email SAU username)
user = db.query(User).filter(
    (User.email == form_data.username) | (User.username == form_data.username)
).first()

# 2. Verificare password
if not verify_password(form_data.password, user.hashed_password):
    raise HTTPException(401, "Incorrect credentials")

# 3. Generare JWT token
access_token_expires = timedelta(minutes=30)
access_token = create_access_token(
    data={"sub": user.email},  # Subject = email
    expires_delta=access_token_expires
)

# 4. Returnare token
return {"access_token": access_token, "token_type": "bearer"}
```

#### 3. Request Autentificat

**Frontend:**
```javascript
const token = localStorage.getItem('token');
const response = await axios.get('/api/auth/me', {
  headers: {
    Authorization: `Bearer ${token}`
  }
});
```

**Backend:**
```python
# 1. Extragere token (OAuth2PasswordBearer)
token = oauth2_scheme(request)  # Din header Authorization

# 2. Decodare JWT
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
email = payload.get("sub")

# 3. Verificare expirare (automată în jwt.decode)
# 4. Căutare user
user = db.query(User).filter(User.email == email).first()

# 5. Dependency injection
return user  # Disponibil în endpoint ca Depends(get_current_user)
```

### Securitate

#### 1. **Password Hashing (bcrypt)**
```python
# NICIODATĂ nu stoca parole plaintext!
plain = "password123"
hashed = "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.FaZ7O0/0rYZw7aRIpg8K5YJ.vC"

# Bcrypt caracteristici:
# - Salt generat automat
# - Cost factor 12 (2^12 iterații)
# - Rezistent la rainbow tables
# - Slow by design (prevent brute force)
```

#### 2. **JWT Tokens**
```
Header:    {"alg": "HS256", "typ": "JWT"}
Payload:   {"sub": "user@example.com", "exp": 1234567890}
Signature: HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)

Token: header.payload.signature
```

**Avantaje JWT:**
- Stateless (nu necesită sesiuni server)
- Auto-conținut (payload include date user)
- Verificabil (signature cu SECRET_KEY)
- Expirare automată (exp claim)

#### 3. **CORS Configuration**
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
allow_credentials=True  # Permite cookies și Authorization headers
allow_methods=["*"]     # GET, POST, PUT, DELETE, etc.
allow_headers=["*"]     # Authorization, Content-Type, etc.
```

#### 4. **Validare Input**

**Backend (Pydantic):**
- Email format valid (EmailStr)
- Length constraints (Field)
- Regex patterns (field_validator)
- Type checking automat

**Frontend (React):**
- HTML5 validation (type, required, minLength)
- Custom regex validation
- Password matching
- Real-time error display

---

## 🔄 Comunicarea Frontend-Backend

### Request/Response Flow

#### 1. **Axios Configuration**

```javascript
// Frontend implicit folosește proxy Vite
axios.get('/api/auth/me')  
// → http://localhost:3000/api/auth/me (frontend)
// → http://localhost:8000/api/auth/me (proxied to backend)
```

#### 2. **API Endpoints Mapping**

| Frontend Call | Proxy → Backend | Method | Auth |
|---------------|-----------------|--------|------|
| `/api/auth/register` | `POST :8000/api/auth/register` | POST | Nu |
| `/api/auth/login` | `POST :8000/api/auth/login` | POST | Nu |
| `/api/auth/me` | `GET :8000/api/auth/me` | GET | Da |

#### 3. **Request Headers**

**Autentificat:**
```javascript
{
  "Content-Type": "application/json",
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**FormData (Login):**
```javascript
{
  "Content-Type": "multipart/form-data",
  // No Authorization (login endpoint)
}
```

#### 4. **Response Format**

**Success (200/201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Error (400/401/500):**
```json
{
  "detail": "Email already registered"
}
// SAU
{
  "detail": [
    {"loc": ["body", "email"], "msg": "Invalid email format", "type": "value_error"}
  ]
}
```

#### 5. **Error Handling**

**Frontend (AuthContext.jsx):**
```javascript
try {
  const response = await axios.post('/api/auth/login', formData);
  return { success: true };
} catch (error) {
  let errorMessage = 'Login failed';
  
  if (error.response?.data?.detail) {
    if (typeof error.response.data.detail === 'string') {
      errorMessage = error.response.data.detail;
    } else if (Array.isArray(error.response.data.detail)) {
      errorMessage = error.response.data.detail
        .map(err => err.msg || err.message)
        .join(', ');
    }
  }
  
  return { success: false, error: errorMessage };
}
```

---

## 🛠️ Tehnologii și Dependențe

### Backend (Python)

| Package | Versiune | Scop |
|---------|----------|------|
| **fastapi** | 0.109.0 | Framework web modern, async, rapid |
| **uvicorn** | 0.27.0 | ASGI server pentru FastAPI |
| **sqlalchemy** | 2.0.25 | ORM pentru baze de date |
| **psycopg2-binary** | 2.9.9 | Driver PostgreSQL |
| **python-jose** | 3.3.0 | JWT encoding/decoding |
| **bcrypt** | 4.1.2 | Password hashing |
| **python-multipart** | 0.0.6 | FormData parsing (OAuth2) |
| **python-dotenv** | 1.0.0 | Environment variables |
| **pydantic** | 2.5.3 | Validare date și serializare |

**Instalare:**
```bash
cd backend
pip install -r requirements.txt
```

### Frontend (JavaScript)

| Package | Versiune | Scop |
|---------|----------|------|
| **react** | 18.2.0 | UI library |
| **react-dom** | 18.2.0 | React rendering |
| **react-router-dom** | 6.21.1 | Routing și navigare |
| **axios** | 1.6.5 | HTTP client |
| **vite** | 5.0.11 | Build tool rapid |
| **@vitejs/plugin-react** | 4.2.1 | Plugin Vite pentru React |

**Instalare:**
```bash
cd frontend
npm install
```

### Development Tools

**Backend:**
- Python 3.9+
- Virtual environment (venv)
- SQLite3 (built-in)

**Frontend:**
- Node.js 18+
- npm 9+

**Optional:**
- PostgreSQL 14+ (production)
- Docker (containerizare)

---

## 📊 Fluxul de Date

### 1. User Registration Flow

```
User Input (Frontend)
    ↓
Email: "user@example.com"
Username: "johndoe"
Password: "securepass123"
    ↓
Frontend Validation (Register.jsx)
    ├─ Email valid? ✓
    ├─ Username format? ✓ [a-zA-Z0-9_-]
    ├─ Password >= 6? ✓
    └─ Passwords match? ✓
    ↓
POST /api/auth/register
    {
      "email": "user@example.com",
      "username": "johndoe",
      "password": "securepass123"
    }
    ↓
Backend Validation (schemas.py - UserCreate)
    ├─ Pydantic validation
    ├─ Email format (EmailStr)
    ├─ Username regex
    └─ Field constraints
    ↓
Business Logic (main.py)
    ├─ Check email exists?
    ├─ Check username exists?
    └─ Hash password (bcrypt)
    ↓
Database Insert (models.py)
    INSERT INTO users (email, username, hashed_password, is_active, is_admin)
    VALUES ('user@example.com', 'johndoe', '$2b$12$...', TRUE, FALSE)
    ↓
Response (schemas.py - UserResponse)
    {
      "id": 1,
      "email": "user@example.com",
      "username": "johndoe",
      "is_active": true,
      "is_admin": false,
      "created_at": "2024-11-21T10:30:00Z"
    }
    ↓
Frontend Redirect
    navigate('/login', { state: { message: 'Registration successful!' } })
```

### 2. User Login Flow

```
User Input (Frontend)
    ↓
Username: "johndoe"  (poate fi email SAU username)
Password: "securepass123"
    ↓
FormData Creation (AuthContext.jsx)
    username: johndoe
    password: securepass123
    ↓
POST /api/auth/login (OAuth2PasswordRequestForm)
    ↓
Database Query (main.py)
    SELECT * FROM users
    WHERE email = 'johndoe' OR username = 'johndoe'
    ↓
Password Verification (auth.py)
    bcrypt.checkpw(
      plain='securepass123',
      hashed='$2b$12$...'
    ) → TRUE
    ↓
JWT Generation (auth.py)
    Payload: {"sub": "user@example.com", "exp": 1700575800}
    Signature: HMACSHA256(payload, SECRET_KEY)
    Token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzAwNTc1ODAwfQ.signature"
    ↓
Response
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ↓
Frontend Token Storage (AuthContext.jsx)
    localStorage.setItem('token', access_token)
    ↓
Fetch User Data
    GET /api/auth/me
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ↓
Update Context State
    setUser({
      id: 1,
      email: "user@example.com",
      username: "johndoe",
      ...
    })
    ↓
Redirect to Dashboard
    navigate('/dashboard')
```

### 3. Protected Route Access Flow

```
User navigates to /dashboard
    ↓
PrivateRoute Component (PrivateRoute.jsx)
    ├─ loading = true? → Show "Loading..."
    ├─ user exists? → Render <Dashboard />
    └─ no user? → <Navigate to="/login" />
    ↓
Dashboard Mount (Dashboard.jsx)
    ├─ Access user from useAuth()
    ├─ Display user.username, user.email, etc.
    └─ Render UI
    ↓
API Call (optional, e.g., fetch data)
    GET /api/protected
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ↓
Backend Token Verification (auth.py)
    ├─ Extract token from Authorization header
    ├─ Decode JWT: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    ├─ Verify expiration (automatic)
    ├─ Extract email from payload["sub"]
    └─ Query user from database
    ↓
Dependency Injection (FastAPI)
    current_user: User = Depends(get_current_user)
    ↓
Endpoint Logic (main.py)
    @app.get("/api/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"message": f"Hello {current_user.username}!"}
    ↓
Response
    {
      "message": "Hello johndoe!",
      "user_id": 1,
      "email": "user@example.com"
    }
```

---

## 📁 Structura Fișierelor Detaliată

```
license-plate-reconstruction/
│
├── backend/                          # Aplicația backend FastAPI
│   ├── main.py                       # Entry point, endpoint-uri REST API
│   ├── database.py                   # Configurare SQLAlchemy, engine, session
│   ├── models.py                     # Modele ORM (User)
│   ├── schemas.py                    # Scheme Pydantic (validare I/O)
│   ├── auth.py                       # Logică JWT, hashing, autentificare
│   ├── ocr_service.py                # Serviciu OCR (fast-plate-ocr wrapper)
│   ├── requirements.txt              # Dependențe Python
│   ├── .env                          # Variabile mediu (SECRET_KEY, DATABASE_URL)
│   ├── .env.example                  # Template pentru .env
│   ├── lpr_database.db               # Bază de date SQLite (generat automat)
│   ├── ml_models/                    # Modele ML (.keras files)
│   │   └── generator_256x128noSkew.keras  # Model Pix2Pix
│   └── __pycache__/                  # Cache bytecode Python
│
├── frontend/                         # Aplicația frontend React
│   ├── index.html                    # HTML template
│   ├── package.json                  # Dependențe Node.js, scripts npm
│   ├── vite.config.js                # Configurare Vite (port, proxy)
│   │
│   ├── public/                       # Fișiere statice
│   │   └── reports/                  # Rapoarte PDF
│   │       ├── ocr_results.pdf       # Rezultate OCR
│   │       └── psnr_ssim_results.pdf # Metrici calitate
│   │
│   ├── src/                          # Cod sursă React
│   │   ├── main.jsx                  # Entry point React
│   │   ├── App.jsx                   # Componenta root, routing
│   │   ├── App.css                   # Stiluri globale aplicație
│   │   ├── index.css                 # Stiluri bază, reset CSS
│   │   │
│   │   ├── components/               # Componente reutilizabile
│   │   │   ├── PrivateRoute.jsx      # HOC pentru protecție rute
│   │   │   ├── ImageUploader.jsx     # Upload + Reconstrucție + OCR
│   │   │   └── ImageUploader.css     # Stiluri componenta upload
│   │   │
│   │   ├── contexts/                 # Context providers (state global)
│   │   │   └── AuthContext.jsx       # Context autentificare (user, login, logout)
│   │   │
│   │   └── pages/                    # Componente pagini
│   │       ├── Login.jsx             # Pagină login
│   │       ├── Register.jsx          # Pagină înregistrare
│   │       ├── Dashboard.jsx         # Pagină dashboard (protejată)
│   │       ├── Metrics.jsx           # Pagină rapoarte PDF
│   │       ├── Auth.css              # Stiluri login + register
│   │       ├── Dashboard.css         # Stiluri dashboard
│   │       └── Metrics.css           # Stiluri pagină metrics
│   │
│   └── node_modules/                 # Dependențe instalate (generat de npm)
│
├── start.ps1                         # Script pornire Windows (PowerShell)
├── start.bat                         # Script pornire Windows (batch)
├── start.sh                          # Script pornire Linux/macOS (bash)
├── stop.ps1                          # Script oprire Windows
├── stop.sh                           # Script oprire Linux/macOS
├── docker-compose.yml                # Configurare Docker (PostgreSQL)
├── .env.docker                       # Environment pentru Docker
├── .env.docker.example               # Template Docker env
├── README.md                         # Documentație proiect (setup, features)
├── LICENSE                           # Licență proiect
└── details.md                        # ACEST FIȘIER - Documentație tehnică completă
│   │   │
│   │   ├── contexts/                 # Context providers (state global)
│   │   │   └── AuthContext.jsx       # Context autentificare (user, login, logout)
│   │   │
│   │   └── pages/                    # Componente pagini
│   │       ├── Login.jsx             # Pagină login
│   │       ├── Register.jsx          # Pagină înregistrare
│   │       ├── Dashboard.jsx         # Pagină dashboard (protejată)
│   │       ├── Auth.css              # Stiluri login + register
│   │       └── Dashboard.css         # Stiluri dashboard
│   │
│   └── node_modules/                 # Dependențe instalate (generat de npm)
│
├── README.md                         # Documentație proiect (setup, features)
├── LICENSE                           # Licență proiect
└── details.md                        # ACEST FIȘIER - Documentație tehnică completă
```

### Descriere Fișiere Cheie

#### Backend

- **main.py**: Punct de intrare, definește toate endpoint-urile API, configurează CORS, inițializează FastAPI app, încarcă modelele ML (Pix2Pix + OCR)
- **database.py**: Creează engine-ul SQLAlchemy, SessionLocal factory, Base pentru modele
- **models.py**: Definește schema tabelei `users` folosind SQLAlchemy ORM
- **schemas.py**: Pydantic models pentru validare request/response (UserCreate, UserResponse, Token)
- **auth.py**: Funcții pentru hashing bcrypt, generare/verificare JWT, dependency injection `get_current_user`
- **ocr_service.py**: Wrapper pentru fast-plate-ocr, OCRManager singleton, funcție run_ocr()
- **requirements.txt**: Lista tuturor dependențelor Python (FastAPI, TensorFlow, fast-plate-ocr, etc.)
- **.env**: Variabile de mediu sensibile (SECRET_KEY, DATABASE_URL) - NU se commit în Git
- **lpr_database.db**: Fișier SQLite generat automat la primul run, conține tabela users
- **ml_models/**: Folder cu modele Pix2Pix (.keras format)

#### Frontend

- **main.jsx**: Montează aplicația React în DOM (`root.render(<App />)`)
- **App.jsx**: Componenta principală, definește rutele cu React Router, înfășoară cu AuthProvider
- **vite.config.js**: Configurare dev server (port 3000, proxy către backend :8000)
- **AuthContext.jsx**: State management global pentru autentificare, expune `login`, `register`, `logout`, `user`
- **PrivateRoute.jsx**: HOC care verifică autentificarea înainte de a randa componenta protejată
- **ImageUploader.jsx**: Componentă pentru upload, reconstrucție Pix2Pix și OCR pe imagini
- **Login.jsx**: Form login, apelează `login()` din context, redirectează la dashboard
- **Register.jsx**: Form register, validează input, apelează `register()`, redirectează la login
- **Dashboard.jsx**: Pagină protejată, afișează date user, buton logout, link către Metrics
- **Metrics.jsx**: Pagină pentru vizualizare rapoarte PDF (OCR results, PSNR/SSIM)
- **Auth.css**: Stiluri pentru paginile de autentificare (form, input, button, card)
- **Dashboard.css**: Stiluri pentru dashboard (navbar, cards, layout)
- **Metrics.css**: Stiluri pentru pagina de metrics (tabs, iframe viewer)
- **ImageUploader.css**: Stiluri pentru componenta de upload (preview, butoane OCR, rezultate)

#### Scripts

- **start.ps1 / start.bat**: Pornește automat PostgreSQL + Backend + Frontend pe Windows
- **start.sh**: Pornește automat PostgreSQL + Backend + Frontend pe Linux/macOS
- **stop.ps1**: Oprește toate serviciile pe Windows (opțional păstrează PostgreSQL)
- **stop.sh**: Oprește toate serviciile pe Linux/macOS (opțional păstrează PostgreSQL)

---

## 🚀 Cum Funcționează Împreună

### 1. Startup Sequence

**Quick Start (Recomandat):**

Windows:
```bash
# Pornește tot automat (Frontend + Backend + PostgreSQL)
.\start.ps1
# sau dublu-click pe start.bat
```

Linux/macOS:
```bash
# Fă scriptul executabil (prima dată)
chmod +x start.sh

# Pornește tot automat (Frontend + Backend + PostgreSQL)
./start.sh
```

**Manual Setup:**

Backend (Windows):
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
# → Uvicorn running on http://0.0.0.0:8000
# → Database tables created (if not exists)
```

Backend (Linux/macOS):
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# → Uvicorn running on http://0.0.0.0:8000
```

Frontend (toate platformele):
```bash
cd frontend
npm install
npm run dev
# → Vite dev server running on http://localhost:3000
# → Proxy configured: /api/* → http://localhost:8000/api/*
```

### 2. Communication Flow

```
Browser (localhost:3000)
    ↕ HTTP Requests (Axios)
Vite Dev Server (localhost:3000)
    ↕ Proxy: /api/* → :8000/api/*
FastAPI Backend (localhost:8000)
    ↕ SQLAlchemy ORM + TensorFlow + fast-plate-ocr
Database + ML Models (PostgreSQL + .keras + ONNX)
```

### 3. Technology Stack Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  React Components + React Router + CSS                      │
│  - Login, Register, Dashboard, Metrics, ImageUploader       │
│  - PrivateRoute protection                                  │
└─────────────────────────────────────────────────────────────┘
                          ↕ Axios HTTP
┌─────────────────────────────────────────────────────────────┐
│                   STATE MANAGEMENT LAYER                     │
│  React Context API (AuthContext)                            │
│  - Global user state                                        │
│  - login/register/logout functions                          │
│  - localStorage persistence                                 │
└─────────────────────────────────────────────────────────────┘
                    ↕ REST API (JSON + multipart/form-data)
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER                               │
│  FastAPI + Pydantic                                         │
│  - Endpoint definitions (main.py)                           │
│  - Request/Response validation (schemas.py)                 │
│  - Dependency injection, file uploads                       │
└─────────────────────────────────────────────────────────────┘
                    ↕ Function Calls
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                       │
│  Python Functions (auth.py, ocr_service.py)                 │
│  - Password hashing (bcrypt)                                │
│  - JWT generation/verification (python-jose)                │
│  - User authentication                                      │
│  - OCR text extraction (fast-plate-ocr)                     │
└─────────────────────────────────────────────────────────────┘
                    ↕ SQLAlchemy ORM + ML Inference
┌─────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                         │
│  SQLAlchemy ORM (models.py, database.py)                    │
│  TensorFlow (Pix2Pix model inference)                       │
│  ONNX Runtime (fast-plate-ocr inference)                    │
│  - User model, session management                           │
│  - ML model loading and prediction                          │
└─────────────────────────────────────────────────────────────┘
                    ↕ SQL Queries + File I/O
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                             │
│  PostgreSQL / SQLite (users table)                          │
│  File System (ml_models/*.keras, ONNX models)               │
│  - Persistent data storage                                  │
│  - ML model files                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Concluzie

### Stare Actuală
Proiectul **License Plate Reconstruction** este o aplicație web full-stack complet funcțională din punct de vedere al autentificării. Sistemul include:

✅ **Backend complet**:
- REST API cu FastAPI
- Autentificare JWT robustă
- Bază de date relațională cu ORM (PostgreSQL/SQLite)
- Validare complexă a datelor
- Securitate (bcrypt, JWT, CORS)
- ML Inference (Pix2Pix model TensorFlow)
- OCR service (fast-plate-ocr cu ONNX Runtime)

✅ **Frontend modern**:
- React 18 cu Vite
- React Router pentru navigare
- Context API pentru state management
- Interfață responsive
- Protecție rute
- Upload și preview imagini
- Integrare OCR și reconstrucție Pix2Pix
- Vizualizare rapoarte PDF

✅ **Integrare completă**:
- Comunicare frontend-backend prin Axios
- Proxy development (Vite)
- Error handling consistent
- Token persistence (localStorage)
- Docker PostgreSQL pentru producție
- Cross-platform scripts (Windows/Linux/macOS)

### Next Steps (Viitor)
🔄 **Funcționalități planificate**:
1. **Istoric utilizator** - salvare și vizualizare rezultate procesări anterioare
2. **Batch processing** - procesare multiplă de imagini simultan
3. **Admin panel** - fine-tuning model, gestiune useri, statistici
4. **Export rezultate** - CSV, PDF, JSON download
5. **Metrics tracking** - PSNR/SSIM calculation în real-time
6. **Model versioning** - suport pentru multiple versiuni de modele

### Tehnologii Cheie Folosite
- **Backend**: FastAPI, SQLAlchemy, JWT (python-jose), bcrypt, TensorFlow 2.20.0, fast-plate-ocr 1.0.2, onnxruntime
- **Frontend**: React 18, React Router 6, Axios, Vite
- **Database**: PostgreSQL (prod), SQLite (dev)
- **ML/AI**: TensorFlow (Pix2Pix), ONNX Runtime (OCR), OpenCV, NumPy
- **Security**: bcrypt password hashing, JWT tokens, CORS
- **DevOps**: Docker, Docker Compose, cross-platform bash/PowerShell scripts
- **Tools**: npm, pip, venv, Git, Git LFS

---

**Autor**: António Heasca  
**Proiect**: License Plate Reconstruction System  
**Versiune**: 2.0.0  
**Data**: Noiembrie 2025  
**Repository**: license-plate-reconstruction
