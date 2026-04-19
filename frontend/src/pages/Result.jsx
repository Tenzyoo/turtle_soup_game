import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './Result.css';

const API_BASE = 'http://localhost:5001/api';

function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const [personality, setPersonality] = useState(null);
  const [loading, setLoading] = useState(true);

  const { puzzleId, soupBottom, history, title } = location.state || {};

  useEffect(() => {
    if (!puzzleId || !history) {
      navigate('/');
      return;
    }

    // 请求性格分析
    fetch(`${API_BASE}/personality`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        puzzle_id: puzzleId,
        history: history
      })
    })
      .then(res => res.json())
      .then(data => {
        setPersonality(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('性格分析失败', err);
        setLoading(false);
      });
  }, [puzzleId, history, navigate]);

  if (loading) {
    return <div className="result-container loading">分析推理人格中...</div>;
  }

  if (!personality) {
    return <div className="result-container error">分析失败</div>;
  }

  return (
    <div className="result-container">
      <div className="result-header">
        <h1>🎉 游戏结束</h1>
        <p className="soup-title">{title}</p>
      </div>

      <div className="truth-card">
        <h2>真相揭晓</h2>
        <p>{soupBottom}</p>
      </div>

      <div className="personality-card">
        <div className="personality-header">
          <h2>你的推理人格</h2>
          <div className="personality-name">{personality.name}</div>
          <div className="personality-tags">
            {personality.tags.map((tag, i) => (
              <span key={i} className="tag">{tag}</span>
            ))}
          </div>
        </div>

        <div className="dimension-bars">
          <div className="dimension">
            <span className="dimension-label">推理风格</span>
            <div className="bar">
              <div className={`bar-fill inference-${personality.inference_style}`}
                   style={{ width: `${personality.inference_score * 33}%` }}>
              </div>
            </div>
            <span className="dimension-value">
              {personality.inference_style === 'lawful' ? '逻辑' :
               personality.inference_style === 'chaotic' ? '混乱' : '中立'}
            </span>
          </div>
          <div className="dimension">
            <span className="dimension-label">探索风格</span>
            <div className="bar">
              <div className={`bar-fill exploration-${personality.exploration_style}`}
                   style={{ width: `${personality.exploration_score * 33}%` }}>
              </div>
            </div>
            <span className="dimension-value">
              {personality.exploration_style === 'cautious' ? '谨慎' :
               personality.exploration_style === 'aggressive' ? '突击' : '中立'}
            </span>
          </div>
        </div>

        <div className="personality-desc">
          <h3>人格描述</h3>
          <p>{personality.description}</p>
        </div>

        <div className="personality-eval">
          <h3>评价</h3>
          <p>{personality.evaluation}</p>
        </div>

        {personality.reason && (
          <div className="analysis-reason">
            <h3>分析依据</h3>
            <p>{personality.reason}</p>
          </div>
        )}
      </div>

      <div className="result-actions">
        <button className="retry-btn" onClick={() => navigate('/')}>
          再来一局
        </button>
        <button className="share-btn">
          分享结果
        </button>
      </div>
    </div>
  );
}

export default Result;