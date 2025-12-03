"""
OCR Service - Wrapper pentru fast-plate-ocr LicensePlateRecognizer
"""
import logging
from typing import Optional
from io import BytesIO
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class OCRManager:
    """Singleton pentru gestionarea modelului OCR"""
    
    _instance = None
    _recognizer = None
    _model_name = "cct-xs-v1-global-model"  # lightweight model
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRManager, cls).__new__(cls)
        return cls._instance
    
    def load_model(self) -> bool:
        """
        Încarcă modelul OCR la pornirea aplicației
        Returns:
            bool: True dacă modelul a fost încărcat cu succes
        """
        if self._recognizer is not None:
            logger.info("OCR model already loaded")
            return True
        
        try:
            from fast_plate_ocr import LicensePlateRecognizer
            
            logger.info(f"Loading OCR model: {self._model_name}...")
            self._recognizer = LicensePlateRecognizer(self._model_name)
            logger.info("OCR model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error loading OCR model: {str(e)}")
            return False
    
    def get_recognizer(self):
        """Returnează recognizer-ul încărcat"""
        return self._recognizer
    
    def is_loaded(self) -> bool:
        """Verifică dacă modelul este încărcat"""
        return self._recognizer is not None


def run_ocr(image_bytes: bytes) -> dict:
    """
    Rulează OCR pe imaginea uploadată
    
    Args:
        image_bytes: Imaginea ca bytes
    
    Returns:
        dict: Rezultatul OCR cu text și confidence
    """
    manager = OCRManager()
    
    if not manager.is_loaded():
        raise RuntimeError("OCR model not loaded. Please ensure the model is loaded at startup.")
    
    recognizer = manager.get_recognizer()
    
    try:
        # Convertește bytes la imagine PIL
        logger.info("Running OCR on image...")
        image = Image.open(BytesIO(image_bytes))
        
        # Convertește PIL Image la numpy array (așa cum așteaptă LicensePlateRecognizer)
        import numpy as np
        image_array = np.array(image)
        
        # Rulează OCR pe numpy array
        result = recognizer.run(image_array)
        
        # Curăță rezultatul: elimină underscore-uri
        if isinstance(result, list) and len(result) > 0:
            cleaned_result = [text.replace('_', '') for text in result]
        else:
            cleaned_result = result
        
        logger.info(f"OCR completed successfully! Text: {cleaned_result}")
        
        return {
            "text": cleaned_result,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error during OCR: {str(e)}")
        raise
