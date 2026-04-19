import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './PuzzleList.css';

const API_BASE = 'http://localhost:5001/api';

function PuzzleList() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [puzzles, setPuzzles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/puzzles/${topicId}`)
      .then(res => res.json())
      .then(data => {
        setPuzzles(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('加载谜题失败', err);
        setLoading(false);
      });
  }, [topicId]);

  const renderDifficulty = (level) => {
    return '★'.repeat(level) + '☆'.repeat(5 - level);
  };

  if (loading) {
    return <div className="puzzle-list-container loading">加载中...</div>;
  }

  return (
    <div className="puzzle-list-container">
      <div className="puzzle-list-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← 返回
        </button>
        <h1 className="puzzle-list-title">选择谜题</h1>
      </div>
      <div className="puzzle-list">
        {puzzles.map((puzzle) => (
          <div
            key={puzzle.id}
            className="puzzle-card"
            onClick={() => {
              // 从 puzzle.id 提取数字部分作为路由参数
              const puzzleNum = puzzle.id.split('_')[1];
              navigate(`/chat/${topicId}/${puzzleNum}`);
            }}
          >
            <div className="puzzle-header">
              <h3 className="puzzle-title">{puzzle.title}</h3>
              <span className="puzzle-difficulty">{renderDifficulty(puzzle.difficulty)}</span>
            </div>
            <p className="puzzle-soup">{puzzle.soup_face}</p>
            <div className="puzzle-footer">
              <span className="puzzle-label">汤面</span>
              <span className="puzzle-hint">点击开始游戏 →</span>
            </div>
          </div>
        ))}
        {puzzles.length === 0 && (
          <div className="no-puzzles">
            <p>该主题暂无谜题</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default PuzzleList;