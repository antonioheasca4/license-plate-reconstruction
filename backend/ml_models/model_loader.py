"""
Model Loader - Load and manage the Pix2Pix model for license plate reconstruction
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
    """Singleton for managing the Pix2Pix model"""
    
    _instance = None
    _model: Optional[tf.keras.Model] = None
    _model_path: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def load_model(self) -> bool:
        """
        Load the Pix2Pix model at application startup
        Searches for any .keras file in the ml_models/ directory
        Returns:
            bool: True if the model was loaded successfully
        """
        if self._model is not None:
            logger.info("Model already loaded")
            return True
        
        try:
            # Search for any .keras file in the ml_models directory
            keras_files = glob.glob("ml_models/*.keras")
            
            if not keras_files:
                logger.error("No .keras model file found in ml_models/ directory")
                return False
            
            # Use the first .keras file found
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
        """Returns the loaded model"""
        return self._model
    
    def is_loaded(self) -> bool:
        """Checks if the model is loaded"""
        return self._model is not None
    
    def get_model_path(self) -> Optional[str]:
        """Returns the path of the loaded model"""
        return self._model_path


def preprocess_image(image_bytes: bytes, target_size=(128, 256)) -> np.ndarray:
    """
    Preprocess the image for input to the Pix2Pix model
    
    Args:
        image_bytes: The uploaded image bytes
        target_size: Target size (height, width) - 128x256 for the model
    
    Returns:
        numpy array with shape (1, 128, 256, 3) normalized to [-1, 1]
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to the target size expected by the model
        image = image.resize((target_size[1], target_size[0]), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Normalize from [0, 255] to [-1, 1] (as expected by Pix2Pix models)
        img_array = (img_array / 127.5) - 1.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        logger.info(f"Preprocessed image shape: {img_array.shape}, dtype: {img_array.dtype}")
        logger.info(f"Image value range: [{img_array.min():.2f}, {img_array.max():.2f}]")
        
        return img_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise


def postprocess_image(output_array: np.ndarray) -> bytes:
    """
    Converts the model output back to a PNG image
    
    Args:
        output_array: Model output with shape (1, 128, 256, 3) and values in [-1, 1]
    
    Returns:
        bytes: The PNG image as bytes
    """
    try:
        # Remove batch dimension
        img_array = output_array[0]
        
        # Denormalize from [-1, 1] to [0, 255]
        img_array = ((img_array + 1.0) * 127.5).astype(np.uint8)
        
        # Clip values for safety
        img_array = np.clip(img_array, 0, 255)
        
        # Convert to PIL image
        image = Image.fromarray(img_array, mode='RGB')
        
        # Save to bytes as PNG
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
    Runs inference on the uploaded image
    
    Args:
        image_bytes: The uploaded image as bytes
    
    Returns:
        bytes: The reconstructed image as PNG bytes
    """
    manager = ModelManager()
    
    if not manager.is_loaded():
        raise RuntimeError("Model not loaded. Please ensure the model is loaded at startup.")
    
    model = manager.get_model()
    
    try:
        # Preprocessing
        logger.info("Preprocessing image...")
        input_tensor = preprocess_image(image_bytes)
        
        # Inference
        logger.info("Running inference...")
        output_tensor = model.predict(input_tensor, verbose=0)
        
        # Postprocessing
        logger.info("Postprocessing output...")
        result_bytes = postprocess_image(output_tensor)
        
        logger.info("Inference completed successfully!")
        return result_bytes
        
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        raise
