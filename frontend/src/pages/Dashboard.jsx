import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
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

        <div className="info-card">
          <h3>🚀 Next Steps</h3>
          <p>The authentication system is fully functional! You can now:</p>
          <ul>
            <li>Upload license plate images</li>
            <li>Run image reconstruction using Pix2Pix model</li>
            <li>View recognition history</li>
            <li>Fine-tune the model (admin only)</li>
          </ul>
          <p className="note">These features will be implemented in the next phase.</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
