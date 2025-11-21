import { useState, useRef } from 'react';
import axios from 'axios';
import './ImageUploader.css';

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [reconstructedUrl, setReconstructedUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    processFile(file);
  };

  const processFile = (file) => {
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file (JPEG, PNG, etc.)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Image file is too large. Maximum size is 10MB.');
      return;
    }

    setSelectedFile(file);
    setError('');
    setSuccess('');
    setReconstructedUrl(null);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const file = event.dataTransfer.files[0];
    processFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setReconstructedUrl(null);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post('/api/inference', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        responseType: 'blob' // Important: we're receiving an image
      });

      // Create URL for the reconstructed image
      const imageBlob = new Blob([response.data], { type: 'image/png' });
      const imageUrl = URL.createObjectURL(imageBlob);
      setReconstructedUrl(imageUrl);
      setSuccess('Image reconstructed successfully!');

    } catch (err) {
      console.error('Upload error:', err);
      if (err.response?.status === 401) {
        setError('Authentication failed. Please login again.');
      } else if (err.response?.status === 503) {
        setError('ML model is not loaded. Please contact administrator.');
      } else if (err.response?.data) {
        // Try to read error from blob
        const errorText = await err.response.data.text();
        try {
          const errorData = JSON.parse(errorText);
          setError(errorData.detail || 'Failed to process image');
        } catch {
          setError('Failed to process image. Please try again.');
        }
      } else {
        setError(err.message || 'Failed to upload image. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setReconstructedUrl(null);
    setError('');
    setSuccess('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="image-uploader-container">
      <h3>🚗 License Plate Reconstruction</h3>

      <div
        className={`upload-area ${dragOver ? 'drag-over' : ''}`}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📸</div>
        <p><strong>Click to upload</strong> or drag and drop</p>
        <p>PNG, JPG, JPEG (Max 10MB)</p>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
        />
      </div>

      {selectedFile && (
        <div className="file-info">
          <strong>Selected:</strong> {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
        </div>
      )}

      {error && <div className="error-box">{error}</div>}
      {success && <div className="success-box">{success}</div>}

      {previewUrl && !loading && !reconstructedUrl && (
        <div className="preview-section">
          <h4>Preview:</h4>
          <img src={previewUrl} alt="Preview" className="preview-image" />
          <div>
            <button onClick={handleUpload} className="btn-upload">
              🔄 Reconstruct Image
            </button>
            <button onClick={handleReset} className="btn-secondary">
              Clear
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Processing image with Pix2Pix model...</p>
          <p style={{ fontSize: '0.9rem', color: '#666' }}>This may take a few seconds</p>
        </div>
      )}

      {reconstructedUrl && (
        <div className="results-section">
          <h4>✨ Results:</h4>
          <div className="image-comparison">
            <div className="image-box">
              <h4>Original Image</h4>
              <img src={previewUrl} alt="Original" />
            </div>
            <div className="image-box">
              <h4>Reconstructed Image</h4>
              <img src={reconstructedUrl} alt="Reconstructed" />
            </div>
          </div>
          <div style={{ marginTop: '20px' }}>
            <button onClick={handleReset} className="btn-upload">
              📤 Upload Another Image
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
