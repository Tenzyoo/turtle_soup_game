import { useNavigate } from 'react-router-dom';
import './Home.css';

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <div className="home-content">
        <div className="logo-section">
          <div className="logo">
            <svg viewBox="0 0 100 100" className="turtle-logo">
              <ellipse cx="50" cy="55" rx="35" ry="25" fill="#4a7c59" />
              <ellipse cx="50" cy="55" rx="30" ry="20" fill="#6b9b7a" />
              <circle cx="50" cy="25" r="15" fill="#4a7c59" />
              <ellipse cx="25" cy="70" rx="10" ry="5" fill="#4a7c59" />
              <ellipse cx="75" cy="70" rx="10" ry="5" fill="#4a7c59" />
              <ellipse cx="30" cy="50" rx="8" ry="4" fill="#3d6b4a" />
              <ellipse cx="70" cy="50" rx="8" ry="4" fill="#3d6b4a" />
              <ellipse cx="50" cy="60" rx="8" ry="4" fill="#3d6b4a" />
              <circle cx="45" cy="22" r="2" fill="#1a1a1a" />
              <circle cx="55" cy="22" r="2" fill="#1a1a1a" />
            </svg>
          </div>
        </div>
        <h1 className="title">海龟汤谜题</h1>
        <p className="subtitle">通过提问，逐步揭开真相</p>
        <button className="start-button" onClick={() => navigate('/topics')}>
          开始游戏
        </button>
      </div>
    </div>
  );
}

export default Home;