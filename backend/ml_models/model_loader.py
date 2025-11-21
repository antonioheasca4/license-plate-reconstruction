"""
Model Loader - Încarcă și gestionează modelul Pix2Pix pentru reconstrucția plăcuțelor
"""
import os
import logging
from typing import Optional
import glob
import tensorflow as tf
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

class ModelManager:
    """Singleton pentru gestionarea modelului Pix2Pix"""
    
    _instance = None
    _model: Optional[tf.keras.Model] = None
    _model_path: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def load_model(self) -> bool:
        """
        Încarcă modelul Pix2Pix la pornirea aplicației
        Caută orice fișier .keras în directorul ml_models/
        Returns:
            bool: True dacă modelul a fost încărcat cu succes
        """
        if self._model is not None:
            logger.info("Model already loaded")
            return True
        
        try:
            # Caută orice fișier .keras în directorul ml_models
            keras_files = glob.glob("ml_models/*.keras")
            
            if not keras_files:
                logger.error("No .keras model file found in ml_models/ directory")
                return False
            
            # Folosește primul fișier .keras găsit
            self._model_path = keras_files[0]
            logger.info(f"Found model file: {self._model_path}")
            
            logger.info(f"Loading model from {self._model_path}...")
            self._model = tf.keras.models.load_model(self._model_path, compile=False)
            logger.info("Model loaded successfully!")
            logger.info(f"Model input shape: {self._model.input_shape}")
            logger.info(f"Model output shape: {self._model.output_shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def get_model(self) -> Optional[tf.keras.Model]:
        """Returnează modelul încărcat"""
        return self._model
    
    def is_loaded(self) -> bool:
        """Verifică dacă modelul este încărcat"""
        return self._model is not None
    
    def get_model_path(self) -> Optional[str]:
        """Returnează calea modelului încărcat"""
        return self._model_path


def preprocess_image(image_bytes: bytes, target_size=(128, 256)) -> np.ndarray:
    """
    Preprocesează imaginea pentru input în modelul Pix2Pix
    
    Args:
        image_bytes: Bytes-urile imaginii uploadate
        target_size: Dimensiunea țintă (height, width) - 128x256 pentru model
    
    Returns:
        numpy array cu shape (1, 128, 256, 3) normalizat între [-1, 1]
    """
    try:
        # Deschide imaginea din bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convertește la RGB dacă e necesar
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Redimensionează la dimensiunea așteptată de model
        image = image.resize((target_size[1], target_size[0]), Image.Resampling.LANCZOS)
        
        # Convertește la numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Normalizare de la [0, 255] la [-1, 1] (așa cum așteaptă modelele Pix2Pix)
        img_array = (img_array / 127.5) - 1.0
        
        # Adaugă dimensiunea de batch
        img_array = np.expand_dims(img_array, axis=0)
        
        logger.info(f"Preprocessed image shape: {img_array.shape}, dtype: {img_array.dtype}")
        logger.info(f"Image value range: [{img_array.min():.2f}, {img_array.max():.2f}]")
        
        return img_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise


def postprocess_image(output_array: np.ndarray) -> bytes:
    """
    Convertește output-ul modelului înapoi în imagine PNG
    
    Args:
        output_array: Output-ul modelului cu shape (1, 128, 256, 3) și valori în [-1, 1]
    
    Returns:
        bytes: Imaginea PNG ca bytes
    """
    try:
        # Elimină dimensiunea de batch
        img_array = output_array[0]
        
        # Denormalizare de la [-1, 1] la [0, 255]
        img_array = ((img_array + 1.0) * 127.5).astype(np.uint8)
        
        # Clip valorile pentru siguranță
        img_array = np.clip(img_array, 0, 255)
        
        # Convertește la imagine PIL
        image = Image.fromarray(img_array, mode='RGB')
        
        # Salvează în bytes ca PNG
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        logger.info(f"Postprocessed image size: {len(img_bytes.getvalue())} bytes")
        
        return img_bytes.getvalue()
        
    except Exception as e:
        logger.error(f"Error postprocessing image: {str(e)}")
        raise


def run_inference(image_bytes: bytes) -> bytes:
    """
    Rulează inferența pe imaginea uploadată
    
    Args:
        image_bytes: Imaginea uploadată ca bytes
    
    Returns:
        bytes: Imaginea reconstruită ca PNG bytes
    """
    manager = ModelManager()
    
    if not manager.is_loaded():
        raise RuntimeError("Model not loaded. Please ensure the model is loaded at startup.")
    
    model = manager.get_model()
    
    try:
        # Preprocesare
        logger.info("Preprocessing image...")
        input_tensor = preprocess_image(image_bytes)
        
        # Inferență
        logger.info("Running inference...")
        output_tensor = model.predict(input_tensor, verbose=0)
        
        # Postprocesare
        logger.info("Postprocessing output...")
        result_bytes = postprocess_image(output_tensor)
        
        logger.info("Inference completed successfully!")
        return result_bytes
        
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        raise
