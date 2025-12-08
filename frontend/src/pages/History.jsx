import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import './History.css';

function History() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/history?limit=10', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setHistory(response.data.items);
      setError(null);
    } catch (err) {
      console.error('Error fetching history:', err);
      setError('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const deleteHistoryItem = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`/api/history/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Remove from local state
      setHistory(history.filter(item => item.id !== id));
      
      // Close modal if the deleted item was selected
      if (selectedItem?.id === id) {
        setSelectedItem(null);
      }
    } catch (err) {
      console.error('Error deleting history item:', err);
      alert('Failed to delete history item');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="history-container">
        <div className="loading">Loading history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-container">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <button className="back-btn" onClick={() => navigate('/dashboard')}>← Back</button>
        <div>
          <h2>Image Processing History</h2>
          <p className="history-subtitle">Last 10 processed images</p>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          <p>No history yet. Upload and process some images to see them here!</p>
        </div>
      ) : (
        <div className="history-grid">
          {history.map((item, index) => (
            <div key={item.id} className="history-card">
              <div className="history-number">#{history.length - index}</div>
              {item.source === 'camera' && (
                <div className="camera-badge">📷 Camera</div>
              )}
              
              <div className="card-images">
                <div className="image-preview">
                  <img
                    src={item.original_image}
                    alt="Original"
                    onClick={() => setSelectedItem(item)}
                  />
                  <span className="image-label">Original</span>
                </div>

                {item.reconstructed_image && (
                  <div className="image-preview">
                    <img
                      src={item.reconstructed_image}
                      alt="Reconstructed"
                      onClick={() => setSelectedItem(item)}
                    />
                    <span className="image-label">Reconstructed</span>
                  </div>
                )}
              </div>

              {(item.ocr_text_original || item.ocr_text_reconstructed) && (
                <div className="card-ocr">
                  {item.ocr_text_original && (
                    <div className="ocr-result-small">
                      <span className="ocr-label">Original:</span>
                      <span className="ocr-text">{item.ocr_text_original}</span>
                    </div>
                  )}
                  {item.ocr_text_reconstructed && (
                    <div className="ocr-result-small">
                      <span className="ocr-label">Reconstructed:</span>
                      <span className="ocr-text">{item.ocr_text_reconstructed}</span>
                    </div>
                  )}
                </div>
              )}

              <div className="card-actions">
                <span className="card-date">{formatDate(item.created_at)}</span>
                <button
                  className="btn-view"
                  onClick={() => setSelectedItem(item)}
                >
                  View Details
                </button>
                <button
                  className="btn-delete"
                  onClick={() => deleteHistoryItem(item.id)}
                  title="Delete"
                >
                
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for viewing full details */}
      {selectedItem && (
        <div className="modal-overlay" onClick={() => setSelectedItem(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button
              className="modal-close"
              onClick={() => setSelectedItem(null)}
            >
              ✕
            </button>

            <h3>Image Details</h3>
            <p className="modal-date">{formatDate(selectedItem.created_at)}</p>

            <div className="modal-images">
              <div className="modal-image-container">
                <h4>Original Image</h4>
                <img src={selectedItem.original_image} alt="Original" />
                {selectedItem.ocr_text_original && (
                  <div className="modal-ocr">
                    <strong>OCR Result:</strong> {selectedItem.ocr_text_original}
                  </div>
                )}
              </div>

              {selectedItem.reconstructed_image && (
                <div className="modal-image-container">
                  <h4>Reconstructed Image</h4>
                  <img src={selectedItem.reconstructed_image} alt="Reconstructed" />
                  {selectedItem.ocr_text_reconstructed && (
                    <div className="modal-ocr">
                      <strong>OCR Result:</strong> {selectedItem.ocr_text_reconstructed}
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="modal-actions">
              <button
                className="btn-delete-modal"
                onClick={() => {
                  deleteHistoryItem(selectedItem.id);
                }}
              >
                Delete This Item
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default History;
