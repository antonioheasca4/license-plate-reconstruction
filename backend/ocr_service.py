"""
OCR Service - Wrapper for fast-plate-ocr LicensePlateRecognizer
"""
import logging
from typing import Optional
from io import BytesIO
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class OCRManager:
    """Singleton for managing the OCR model"""
    
    _instance = None
    _recognizer = None
    _model_name = "cct-xs-v1-global-model"  # lightweight model
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCRManager, cls).__new__(cls)
        return cls._instance
    
    def load_model(self) -> bool:
        """
        Load the OCR model at application startup
        Returns:
            bool: True if the model was loaded successfully
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
        """Return the loaded recognizer"""
        return self._recognizer
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded"""
        return self._recognizer is not None


def run_ocr(image_bytes: bytes) -> dict:
    """
    Run OCR on the uploaded image
    
    Args:
        image_bytes: The image as bytes
    
    Returns:
        dict: OCR result with text and confidence
    """
    manager = OCRManager()
    
    if not manager.is_loaded():
        raise RuntimeError("OCR model not loaded. Please ensure the model is loaded at startup.")
    
    recognizer = manager.get_recognizer()
    
    try:
        # Convert bytes to PIL image
        logger.info("Running OCR on image...")
        image = Image.open(BytesIO(image_bytes))
        
        # Convert PIL Image to numpy array (as expected by LicensePlateRecognizer)
        import numpy as np
        image_array = np.array(image)
        
        # Run OCR on numpy array
        result = recognizer.run(image_array)
        
        # Clean the result: remove underscores
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
