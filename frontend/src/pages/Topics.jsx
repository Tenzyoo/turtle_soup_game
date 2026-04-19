import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './Topics.css';

const API_BASE = 'http://localhost:5001/api';

const defaultColors = {
  workplace: '#3498db',
  school: '#e74c3c',
  mystery: '#9b59b6',
  classic: '#f39c12'
};

function Topics() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/topics`)
      .then(res => res.json())
      .then(data => {
        setTopics(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('加载主题失败', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="topics-container loading">加载中...</div>;
  }

  return (
    <div className="topics-container">
      <div className="topics-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← 返回
        </button>
        <h1 className="topics-title">选择主题</h1>
      </div>
      <div className="topics-grid">
        {topics.map((topic) => (
          <div
            key={topic.id}
            className="topic-card"
            style={{ '--topic-color': defaultColors[topic.id] || '#666' }}
            onClick={() => navigate(`/puzzles/${topic.id}`)}
          >
            <div className="topic-icon">{topic.icon}</div>
            <h3 className="topic-name">{topic.name}</h3>
            <p className="topic-desc">{topic.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Topics;