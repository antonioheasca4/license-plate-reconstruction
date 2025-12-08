import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ImageUploader.css';

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(() => localStorage.getItem('lpr_previewUrl') || null);
  const [reconstructedUrl, setReconstructedUrl] = useState(() => localStorage.getItem('lpr_reconstructedUrl') || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrOriginal, setOcrOriginal] = useState(() => localStorage.getItem('lpr_ocrOriginal') || '');
  const [ocrReconstructed, setOcrReconstructed] = useState(() => localStorage.getItem('lpr_ocrReconstructed') || '');
  const [currentHistoryId, setCurrentHistoryId] = useState(() => {
    const saved = localStorage.getItem('lpr_currentHistoryId');
    return saved ? parseInt(saved) : null;
  });
  const fileInputRef = useRef(null);

  // Reload from localStorage when component becomes visible (e.g., navigating back)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        // Reload all data from localStorage when page becomes visible
        const savedPreview = localStorage.getItem('lpr_previewUrl');
        const savedReconstructed = localStorage.getItem('lpr_reconstructedUrl');
        const savedOcrOriginal = localStorage.getItem('lpr_ocrOriginal');
        const savedOcrReconstructed = localStorage.getItem('lpr_ocrReconstructed');
        const savedHistoryId = localStorage.getItem('lpr_currentHistoryId');
        
        if (savedPreview) setPreviewUrl(savedPreview);
        if (savedReconstructed) setReconstructedUrl(savedReconstructed);
        if (savedOcrOriginal) setOcrOriginal(savedOcrOriginal);
        if (savedOcrReconstructed) setOcrReconstructed(savedOcrReconstructed);
        if (savedHistoryId) setCurrentHistoryId(parseInt(savedHistoryId));
      }
    };

    // Also reload when component mounts
    handleVisibilityChange();

    window.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleVisibilityChange);
    
    return () => {
      window.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleVisibilityChange);
    };
  }, []);

  // Save to localStorage whenever state changes
  useEffect(() => {
    if (previewUrl) localStorage.setItem('lpr_previewUrl', previewUrl);
    else localStorage.removeItem('lpr_previewUrl');
  }, [previewUrl]);

  useEffect(() => {
    if (reconstructedUrl) localStorage.setItem('lpr_reconstructedUrl', reconstructedUrl);
    else localStorage.removeItem('lpr_reconstructedUrl');
  }, [reconstructedUrl]);

  useEffect(() => {
    if (ocrOriginal) localStorage.setItem('lpr_ocrOriginal', ocrOriginal);
    else localStorage.removeItem('lpr_ocrOriginal');
  }, [ocrOriginal]);

  useEffect(() => {
    if (ocrReconstructed) localStorage.setItem('lpr_ocrReconstructed', ocrReconstructed);
    else localStorage.removeItem('lpr_ocrReconstructed');
  }, [ocrReconstructed]);

  useEffect(() => {
    if (currentHistoryId) localStorage.setItem('lpr_currentHistoryId', currentHistoryId.toString());
    else localStorage.removeItem('lpr_currentHistoryId');
  }, [currentHistoryId]);

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
      
      // Convert to base64 for both display and storage
      const reader = new FileReader();
      reader.onloadend = async () => {
        const reconstructedBase64 = reader.result;
        setReconstructedUrl(reconstructedBase64); // Save base64 instead of blob URL
        setSuccess('Image reconstructed successfully!');
        
        // Save to history immediately after reconstruction
        try {
          const token = localStorage.getItem('token');
          const historyData = {
            original_image: previewUrl,
            reconstructed_image: reconstructedBase64,
            ocr_text_original: null,
            ocr_text_reconstructed: null
          };
          
          const historyResponse = await axios.post('/api/history', historyData, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          // Save the ID for future OCR updates
          setCurrentHistoryId(historyResponse.data.id);
          console.log('Saved to history after reconstruction, ID:', historyResponse.data.id);
        } catch (err) {
          console.error('Failed to save to history:', err);
        }
      };
      reader.readAsDataURL(imageBlob);

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
    setOcrOriginal('');
    setOcrReconstructed('');
    setCurrentHistoryId(null);
    
    // Clear localStorage
    localStorage.removeItem('lpr_previewUrl');
    localStorage.removeItem('lpr_reconstructedUrl');
    localStorage.removeItem('lpr_ocrOriginal');
    localStorage.removeItem('lpr_ocrReconstructed');
    localStorage.removeItem('lpr_currentHistoryId');
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleOCR = async (imageSource) => {
    setOcrLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      let blob;

      if (imageSource === 'original') {
        // Convert data URL to blob
        const response = await fetch(previewUrl);
        blob = await response.blob();
      } else {
        // Reconstructed image is already a blob URL
        const response = await fetch(reconstructedUrl);
        blob = await response.blob();
      }

      const formData = new FormData();
      formData.append('file', blob, 'plate.png');

      const ocrResponse = await axios.post('/api/ocr', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      const ocrText = ocrResponse.data.text || 'No text detected';
      
      if (imageSource === 'original') {
        setOcrOriginal(ocrText);
      } else {
        setOcrReconstructed(ocrText);
      }

      // Save to history with current OCR results
      await saveToHistoryWithOCR(imageSource, ocrText);

    } catch (err) {
      console.error('OCR error:', err);
      if (err.response?.status === 401) {
        setError('Authentication failed. Please login again.');
      } else {
        setError(`OCR failed: ${err.response?.data?.detail || err.message}`);
      }
    } finally {
      setOcrLoading(false);
    }
  };

  const saveToHistory = async () => {
    if (!previewUrl) return;

    try {
      const token = localStorage.getItem('token');
      
      // Convert blob URL to base64 if reconstructed image exists
      let reconstructedBase64 = null;
      if (reconstructedUrl) {
        const response = await fetch(reconstructedUrl);
        const blob = await response.blob();
        reconstructedBase64 = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        });
      }
      
      const historyData = {
        original_image: previewUrl,
        reconstructed_image: reconstructedBase64,
        ocr_text_original: ocrOriginal || null,
        ocr_text_reconstructed: ocrReconstructed || null
      };

      await axios.post('/api/history', historyData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Saved to history successfully');
    } catch (err) {
      console.error('Failed to save to history:', err);
      // Don't show error to user, this is a background operation
    }
  };

  const saveToHistoryWithOCR = async (imageSource, ocrText) => {
    if (!previewUrl) return;

    try {
      const token = localStorage.getItem('token');
      
      // Convert blob URL to base64 if reconstructed image exists
      let reconstructedBase64 = null;
      if (reconstructedUrl) {
        const response = await fetch(reconstructedUrl);
        const blob = await response.blob();
        reconstructedBase64 = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        });
      }
      
      const historyData = {
        original_image: previewUrl,
        reconstructed_image: reconstructedBase64,
        ocr_text_original: imageSource === 'original' ? ocrText : (ocrOriginal || null),
        ocr_text_reconstructed: imageSource === 'reconstructed' ? ocrText : (ocrReconstructed || null)
      };

      // If we already have a history ID, update it instead of creating new
      if (currentHistoryId) {
        await axios.put(`/api/history/${currentHistoryId}`, historyData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        console.log('Updated history with OCR successfully');
      } else {
        const response = await axios.post('/api/history', historyData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        // Save the ID for future updates
        setCurrentHistoryId(response.data.id);
        console.log('Saved to history with OCR successfully, ID:', response.data.id);
      }

    } catch (err) {
      console.error('Failed to save to history:', err);
      // Don't show error to user, this is a background operation
    }
  };

  return (
    <div className="image-uploader-container">
      <h3> License Plate Reconstruction</h3>

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
              Reconstruct Image
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
          <h4> Results:</h4>
          <div className="image-comparison">
            <div className="image-box">
              <h4>Original Image</h4>
              <img src={previewUrl} alt="Original" />
              <button 
                onClick={() => handleOCR('original')} 
                className="btn-ocr"
                disabled={ocrLoading}
              >
                Run OCR
              </button>
              {ocrOriginal && (
                <div className="ocr-result">
                  <strong>Text:</strong> <span className="ocr-text">{ocrOriginal}</span>
                </div>
              )}
            </div>
            <div className="image-box">
              <h4>Reconstructed Image</h4>
              <img src={reconstructedUrl} alt="Reconstructed" />
              <button 
                onClick={() => handleOCR('reconstructed')} 
                className="btn-ocr"
                disabled={ocrLoading}
              >
                Run OCR
              </button>
              {ocrReconstructed && (
                <div className="ocr-result">
                  <strong>Text:</strong> <span className="ocr-text">{ocrReconstructed}</span>
                </div>
              )}
            </div>
          </div>
          {ocrLoading && <div className="ocr-loading">Running OCR...</div>}
          <div style={{ marginTop: '20px' }}>
            <button onClick={handleReset} className="btn-upload">
             Upload Another Image
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
