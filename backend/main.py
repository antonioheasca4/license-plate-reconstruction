from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated
import logging

from database import get_db, engine, Base
from models import User, ImageHistory
from schemas import UserCreate, UserResponse, Token, ImageHistoryCreate, ImageHistoryUpdate, ImageHistoryResponse, ImageHistoryList
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ml_models.model_loader import ModelManager, run_inference
from ocr_service import OCRManager, run_ocr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize model manager
model_manager = ModelManager()

# Initialize OCR manager
ocr_manager = OCRManager()

app = FastAPI(title="License Plate Recognition API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Load ML models at application startup"""
    logger.info("Starting application and loading ML models...")
    
    # Load Pix2Pix model
    success = model_manager.load_model()
    if success:
        logger.info("✓ Pix2Pix model loaded successfully!")
    else:
        logger.warning("⚠ Pix2Pix model failed to load. Inference endpoint will not work.")
        logger.warning("Please ensure a .keras model file is present in the 'ml_models' directory.")
    
    # Load OCR model
    ocr_success = ocr_manager.load_model()
    if ocr_success:
        logger.info("✓ OCR model loaded successfully!")
    else:
        logger.warning("⚠ OCR model failed to load. OCR endpoint will not work.")


@app.get("/")
def root():
    return {"message": "License Plate Recognition API", "version": "1.0.0"}


@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Validate that username doesn't look like an email
    if '@' in user_data.username or '.' in user_data.username and len(user_data.username.split('.')) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be an email address. Use only letters, numbers, underscores, and hyphens"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists (case-insensitive)
    existing_username = db.query(User).filter(User.username.ilike(user_data.username)).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    try:
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user. Please try again."
        )


@app.post("/api/auth/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    """Login and get access token"""
    # Find user by email or username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current logged-in user information"""
    return current_user


@app.get("/api/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    """Example of a protected route that requires authentication"""
    return {
        "message": f"Hello {current_user.username}! This is a protected route.",
        "user_id": current_user.id,
        "email": current_user.email
    }


@app.post("/api/inference")
async def predict_license_plate(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a license plate image and get the reconstructed version using Pix2Pix model
    
    - **file**: Image file (JPEG, PNG) containing a license plate
    - Returns: Reconstructed image as PNG
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    # Check file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large. Maximum size is 10MB."
        )
    
    # Check if model is loaded
    if not model_manager.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not loaded. Please contact administrator."
        )
    
    try:
        logger.info(f"Processing inference request from user {current_user.username}")
        logger.info(f"Uploaded file: {file.filename}, size: {len(contents)} bytes")
        
        # Run inference
        result_image = run_inference(contents)
        
        logger.info(f"Inference successful for user {current_user.username}")
        
        # Return the reconstructed image as PNG
        return Response(
            content=result_image,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=reconstructed_{file.filename}",
                "X-User-Id": str(current_user.id)
            }
        )
        
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/api/ocr")
async def ocr_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Run OCR on uploaded license plate image
    
    - **file**: Image file (PNG, JPG, JPEG)
    - Returns: OCR text result
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (PNG, JPG, JPEG)"
        )
    
    # Read file contents
    contents = await file.read()
    
    # Validate file size (max 10MB)
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit"
        )
    
    try:
        logger.info(f"Processing OCR request from user {current_user.username}")
        logger.info(f"Uploaded file: {file.filename}, size: {len(contents)} bytes")
        
        # Run OCR
        result = run_ocr(contents)
        
        # Convert array to string if needed
        text_result = result['text']
        if isinstance(text_result, list) and len(text_result) > 0:
            text_result = text_result[0]  # Take first result
        elif isinstance(text_result, list):
            text_result = ""
        
        logger.info(f"OCR successful for user {current_user.username}: {text_result}")
        
        return {"text": text_result, "success": True}
        
    except Exception as e:
        logger.error(f"Error during OCR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing OCR: {str(e)}"
        )


@app.get("/api/model/status")
def model_status(current_user: User = Depends(get_current_user)):
    """Check if the ML models are loaded and ready"""
    pix2pix_loaded = model_manager.is_loaded()
    ocr_loaded = ocr_manager.is_loaded()
    
    return {
        "pix2pix_loaded": pix2pix_loaded,
        "pix2pix_path": model_manager._model_path if pix2pix_loaded else None,
        "ocr_loaded": ocr_loaded,
        "ocr_model": "cct-xs-v1-global-model" if ocr_loaded else None,
        "status": "ready" if (pix2pix_loaded and ocr_loaded) else "partial" if (pix2pix_loaded or ocr_loaded) else "not_loaded"
    }


@app.post("/api/history", response_model=ImageHistoryResponse, status_code=status.HTTP_201_CREATED)
def save_history(
    history_data: ImageHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save image processing history for current user"""
    try:
        new_history = ImageHistory(
            user_id=current_user.id,
            original_image=history_data.original_image,
            reconstructed_image=history_data.reconstructed_image,
            ocr_text_original=history_data.ocr_text_original,
            ocr_text_reconstructed=history_data.ocr_text_reconstructed,
            source=history_data.source
        )
        
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        
        logger.info(f"History saved for user {current_user.username}, ID: {new_history.id}")
        return new_history
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving history: {str(e)}"
        )


@app.get("/api/history", response_model=ImageHistoryList)
def get_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get image processing history for current user (latest 10 by default)"""
    try:
        # Get total count
        total = db.query(ImageHistory).filter(ImageHistory.user_id == current_user.id).count()
        
        # Get history items, ordered by most recent first
        history_items = (
            db.query(ImageHistory)
            .filter(ImageHistory.user_id == current_user.id)
            .order_by(ImageHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        
        logger.info(f"Retrieved {len(history_items)} history items for user {current_user.username}")
        
        return ImageHistoryList(items=history_items, total=total)
        
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.delete("/api/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific history item (only if it belongs to current user)"""
    try:
        history_item = (
            db.query(ImageHistory)
            .filter(ImageHistory.id == history_id, ImageHistory.user_id == current_user.id)
            .first()
        )
        
        if not history_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="History item not found"
            )
        
        db.delete(history_item)
        db.commit()
        
        logger.info(f"History item {history_id} deleted by user {current_user.username}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting history: {str(e)}"
        )


@app.put("/api/history/{history_id}", response_model=ImageHistoryResponse)
def update_history(
    history_id: int,
    history_data: ImageHistoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific history item with new OCR results"""
    try:
        history_item = (
            db.query(ImageHistory)
            .filter(ImageHistory.id == history_id, ImageHistory.user_id == current_user.id)
            .first()
        )
        
        if not history_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="History item not found"
            )
        
        # Update only OCR fields
        if history_data.ocr_text_original is not None:
            history_item.ocr_text_original = history_data.ocr_text_original
        if history_data.ocr_text_reconstructed is not None:
            history_item.ocr_text_reconstructed = history_data.ocr_text_reconstructed
        
        db.commit()
        db.refresh(history_item)
        
        logger.info(f"History item {history_id} updated by user {current_user.username}")
        return history_item
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating history: {str(e)}"
        )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
