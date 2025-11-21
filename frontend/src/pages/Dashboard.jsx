import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import ImageUploader from '../components/ImageUploader';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <h1>License Plate Recognition</h1>
        <div className="nav-right">
          <span className="user-info">Welcome, {user?.username}</span>
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome to the Dashboard!</h2>
          <div className="user-details">
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Account Status:</strong> {user?.is_active ? 'Active' : 'Inactive'}</p>
            <p><strong>Role:</strong> {user?.is_admin ? 'Admin' : 'User'}</p>
          </div>
        </div>

        {/* Image Upload and Reconstruction Component */}
        <ImageUploader />

        <div className="info-card">
          <h3>ℹ️ About License Plate Reconstruction</h3>
          <p>This system uses a Pix2Pix deep learning model to reconstruct and enhance license plate images.</p>
          <ul>
            <li>Upload a license plate image (degraded, blurry, or low quality)</li>
            <li>The Pix2Pix model will reconstruct it to improve clarity</li>
            <li>Compare the original and reconstructed images side-by-side</li>
            <li>Model size: 256x128 pixels (automatically resized)</li>
          </ul>
          <p className="note">Model: Auto-detected .keras file in ml_models/</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
