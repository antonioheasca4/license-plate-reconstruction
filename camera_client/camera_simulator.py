"""
Camera Client Simulator - License Plate Reconstruction System

Simulates an embedded camera that monitors a folder and automatically sends
new images to the server for reconstruction and OCR.

Usage:
    python camera_simulator.py
    
Features:
    - Monitor a folder for new images (folder watching)
    - Automatic authentication to backend (JWT)
    - Sends images to /api/inference for reconstruction
    - Optional: Runs OCR on reconstructed images
    - Saves results in PostgreSQL (via /api/history)
    - Saves results locally
    - Detailed logging for debugging
"""

import os
import sys
import json
import time
import base64
import logging
import requests
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging with UTF-8 for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('camera_client.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class CameraClient:
    """Client that simulates a camera and communicates with the backend"""
    
    def __init__(self, config_path='config.json'):
        """Initializes the client with configuration from JSON"""
        self.config = self._load_config(config_path)
        self.token = None
        self.session = requests.Session()
        
        # Create folders if they don't exist
        os.makedirs(self.config['watch_folder'], exist_ok=True)
        os.makedirs(self.config['results_folder'], exist_ok=True)
        
        logger.info(" Camera Client initialized")
        logger.info(f" Watching folder: {self.config['watch_folder']}")
        logger.info(f" Results folder: {self.config['results_folder']}")
    
    def _load_config(self, config_path):
        """Loads configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f" Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f" Config file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f" Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def authenticate(self):
        """Authenticate to backend and obtain JWT token"""
        url = f"{self.config['server_url']}/api/auth/login"
        data = {
            'username': self.config['username'],
            'password': self.config['password']
        }
        
        try:
            logger.info(" Authenticating to server...")
            response = requests.post(url, data=data, timeout=5)
            response.raise_for_status()
            
            token_data = response.json()
            self.token = token_data['access_token']
            self.session.headers.update({
                'Authorization': f"Bearer {self.token}"
            })
            
            logger.info(" Authentication successful")
            return True
            
        except requests.exceptions.ConnectionError:
            logger.error(f" Cannot connect to server at {self.config['server_url']}")
            logger.error("   Make sure the backend is running!")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f" Authentication failed: {e}")
            logger.error("   Check your username/password in config.json")
            return False
        except Exception as e:
            logger.error(f" Unexpected error during authentication: {e}")
            return False
    
    def wait_for_backend(self, max_attempts=30, retry_delay=2):
        """
        Waits for the backend to become available
        
        Args:
            max_attempts: Maximum number of attempts
            retry_delay: Seconds between attempts
        
        Returns:
            bool: True if backend is available, False otherwise
        """
        url = f"{self.config['server_url']}/docs"  # Health check endpoint
        
        logger.info(f" Waiting for backend at {self.config['server_url']}...")
        
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    logger.info(f" Backend is ready! (attempt {attempt}/{max_attempts})")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            if attempt < max_attempts:
                logger.info(f"   Attempt {attempt}/{max_attempts} - waiting {retry_delay}s...")
                time.sleep(retry_delay)
        
        logger.error(f" Backend not available after {max_attempts} attempts")
        return False
    
    def process_image(self, image_path):
        """
        Processes an image: sends to server for reconstruction + OCR + saving in DB
        
        Args:
            image_path: Path to the image to be processed
        """
        logger.info(f" Processing image: {os.path.basename(image_path)}")
        
        # 1. Reconstruct image
        reconstructed_path = self._reconstruct_image(image_path)
        if not reconstructed_path:
            logger.error(" Reconstruction failed, skipping rest")
            return
        
        # 2. Save to database (with source="camera")
        history_id = self._save_to_history(image_path, reconstructed_path)
        
        # 3. Run OCR (optional)
        if self.config.get('auto_ocr', False):
            ocr_results = self._run_ocr(image_path, reconstructed_path)
            
            # 4. Update history with OCR results
            if history_id and ocr_results:
                self._update_history_with_ocr(history_id, ocr_results)
        
        logger.info(f" Processing complete for {os.path.basename(image_path)}\n")
    
    def _reconstruct_image(self, image_path):
        """Sends image to server for reconstruction"""
        url = f"{self.config['server_url']}/api/inference"
        
        try:
            # Reads the image
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                
                logger.info("    Sending to /api/inference...")
                start_time = time.time()
                
                response = self.session.post(url, files=files)
                response.raise_for_status()
                
                elapsed = time.time() - start_time
                logger.info(f"   Reconstruction completed in {elapsed:.2f}s")
            
            # Save reconstructed image
            if self.config.get('save_results', True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                original_name = Path(image_path).stem
                reconstructed_filename = f"{original_name}_reconstructed_{timestamp}.png"
                reconstructed_path = os.path.join(
                    self.config['results_folder'], 
                    reconstructed_filename
                )
                
                with open(reconstructed_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"    Saved: {reconstructed_filename}")
                return reconstructed_path
            
            return None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.warning("   Token expired, re-authenticating...")
                if self.authenticate():
                    return self._reconstruct_image(image_path)
            logger.error(f"   HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"   Reconstruction error: {e}")
            return None
    
    def _run_ocr(self, original_path, reconstructed_path):
        """Runs OCR on the original and reconstructed images"""
        url = f"{self.config['server_url']}/api/ocr"
        
        results = {}
        
        # OCR on the original image
        logger.info("   Running OCR on original image...")
        ocr_result_original = self._ocr_single_image(url, original_path)
        if ocr_result_original:
            results['original'] = ocr_result_original
            logger.info(f"   Original OCR: {ocr_result_original}")
        
        # OCR on the reconstructed image
        if reconstructed_path:
            logger.info("   Running OCR on reconstructed image...")
            ocr_result_reconstructed = self._ocr_single_image(url, reconstructed_path)
            if ocr_result_reconstructed:
                results['reconstructed'] = ocr_result_reconstructed
                logger.info(f"   Reconstructed OCR: {ocr_result_reconstructed}")
        
        # Save OCR results locally
        if results and self.config.get('save_results', True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = Path(original_path).stem
            ocr_filename = f"{original_name}_ocr_{timestamp}.json"
            ocr_path = os.path.join(self.config['results_folder'], ocr_filename)
            
            with open(ocr_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"   OCR results saved locally: {ocr_filename}")
        
        return results
    
    def _ocr_single_image(self, url, image_path):
        """Runs OCR on a single image"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/png')}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                
                data = response.json()
                return data.get('text', '')
                
        except Exception as e:
            logger.error(f"   OCR error: {e}")
            return None
    
    def _save_to_history(self, original_path, reconstructed_path):
        """Saves images to the database via /api/history"""
        url = f"{self.config['server_url']}/api/history"
        
        try:
            logger.info("   Saving to database...")
            
            # Convert images to base64
            with open(original_path, 'rb') as f:
                original_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            with open(reconstructed_path, 'rb') as f:
                reconstructed_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Send to server with source="camera"
            payload = {
                "original_image": f"data:image/jpeg;base64,{original_base64}",
                "reconstructed_image": f"data:image/png;base64,{reconstructed_base64}",
                "source": "camera"
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            history_id = data.get('id')
            
            logger.info(f"   Saved to database (ID: {history_id}) - marked as 'camera' source")
            return history_id
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.warning("   Token expired, re-authenticating...")
                if self.authenticate():
                    return self._save_to_history(original_path, reconstructed_path)
            logger.error(f"   Failed to save to database: {e}")
            return None
        except Exception as e:
            logger.error(f"   Database save error: {e}")
            return None
    
    def _update_history_with_ocr(self, history_id, ocr_results):
        """Updates the history record with OCR results"""
        url = f"{self.config['server_url']}/api/history/{history_id}"
        
        try:
            logger.info(f"   Updating database record {history_id} with OCR results...")
            
            payload = {
                "ocr_text_original": ocr_results.get('original', ''),
                "ocr_text_reconstructed": ocr_results.get('reconstructed', '')
            }
            
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"   Database updated with OCR results")
            
        except Exception as e:
            logger.error(f"   Failed to update database with OCR: {e}")


class ImageWatcher(FileSystemEventHandler):
    """Handler for file system events (folder watching)"""
    
    def __init__(self, camera_client):
        self.camera_client = camera_client
        self.processed_files = set()
    
    def on_created(self, event):
        """Called when a new file is created in the folder"""
        if event.is_directory:
            return
        
        # Check if it's an image (jpg, jpeg, png)
        file_path = event.src_path
        if not file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return
        
        # Avoid double processing
        if file_path in self.processed_files:
            return
        
        # Wait for the file to be fully written (sometimes necessary)
        time.sleep(0.5)
        
        # Check if the file exists and is accessible
        if not os.path.exists(file_path):
            return
        
        logger.info(f"\nNew image detected: {os.path.basename(file_path)}")
        
        # Process the image
        self.processed_files.add(file_path)
        self.camera_client.process_image(file_path)


def main():
    """Main function - starts the camera client"""
    print("=" * 60)
    print("License Plate Camera Client Simulator")
    print("=" * 60)
    print()
    
    # Initialize the client
    client = CameraClient()
    
    # Wait for the backend to be available
    if not client.wait_for_backend():
        logger.error("Cannot start without backend. Exiting...")
        sys.exit(1)
    
    # Authentication
    if not client.authenticate():
        logger.error("Cannot start without authentication. Exiting...")
        sys.exit(1)
    
    # Configure folder watcher
    event_handler = ImageWatcher(client)
    observer = Observer()
    observer.schedule(
        event_handler, 
        client.config['watch_folder'], 
        recursive=False
    )
    
    # Start watching
    observer.start()
    logger.info("Watching for new images...")
    logger.info(f"Drop images in: {os.path.abspath(client.config['watch_folder'])}")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nStopping camera client...")
        observer.stop()
    
    observer.join()
    logger.info("Camera client stopped")

if __name__ == "__main__":
    main()
