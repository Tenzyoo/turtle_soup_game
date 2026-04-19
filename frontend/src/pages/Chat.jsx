import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Chat.css';

const API_BASE = 'http://localhost:5001/api';

function Chat() {
  const { topicId, puzzleId } = useParams();
  const navigate = useNavigate();

  const [puzzle, setPuzzle] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [hintsUsed, setHintsUsed] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [gameEnded, setGameEnded] = useState(false);
  const [loading, setLoading] = useState(true);

  // 加载谜题数据
  useEffect(() => {
    // 组合正确的 puzzleId 格式：topicId + '_' + puzzleId
    const fullPuzzleId = `${topicId}_${puzzleId}`;
    fetch(`${API_BASE}/puzzle/${fullPuzzleId}`)
      .then(res => res.json())
      .then(data => {
        setPuzzle(data);
        setMessages([
          { type: 'system', text: `欢迎来到「${data.title}」` },
          { type: 'soup', text: data.soup_face },
          { type: 'tip', text: '提示：请提出只能用"是"、"否"或"无关"回答的问题' }
        ]);
        setLoading(false);
      })
      .catch(err => {
        console.error('加载谜题失败', err);
        setLoading(false);
      });
  }, [puzzleId]);

  const handleSend = async () => {
    if (!inputValue.trim() || gameEnded) return;

    const question = inputValue.trim();
    setMessages(prev => [...prev, { type: 'user', text: question }]);
    setInputValue('');

    // 调用后端API
    try {
      const history = messages
        .filter(m => m.type === 'user' || m.type === 'ai')
        .map(m => ({
          question: m.type === 'user' ? m.text : '',
          response: m.type === 'ai' ? { judgement: m.judgement || '', reply: m.text } : {}
        }));

      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          puzzle_id: `${topicId}_${puzzleId}`,
          question,
          history
        })
      });

      const data = await res.json();
      // 显示判断 + 回复
      setMessages(prev => [...prev, {
        type: 'ai',
        judgement: data.judgement,
        text: data.reply
      }]);

      // 如果揭晓了答案，跳转到结果页面
      if (data.is_revealed && data.soup_bottom) {
        setShowAnswer(true);
        setGameEnded(true);
        // 收集完整历史（包含当前问题）
        const fullHistory = [...history, {
          question,
          response: { judgement: data.judgement, reply: data.reply }
        }];
        // 跳转到结果页
        navigate('/result', {
          state: {
            puzzleId: `${topicId}_${puzzleId}`,
            soupBottom: data.soup_bottom,
            history: fullHistory,
            title: puzzle.title
          }
        });
      }
    } catch (err) {
      console.error('API调用失败', err);
      setMessages(prev => [...prev, { type: 'ai', text: '请求失败，请重试' }]);
    }
  };

  const handleHint = async () => {
    if (hintsUsed >= 3 || gameEnded) return;

    try {
      const res = await fetch(`${API_BASE}/hint/${topicId}_${puzzleId}?index=${hintsUsed}`);
      const data = await res.json();
      setMessages(prev => [...prev, { type: 'hint', text: `提示：${data.hint}` }]);
      setHintsUsed(prev => prev + 1);
    } catch (err) {
      console.error('获取提示失败', err);
    }
  };

  const handleRevealAnswer = async () => {
    if (showAnswer) return;

    try {
      const res = await fetch(`${API_BASE}/reveal/${topicId}_${puzzleId}`);
      const data = await res.json();
      setShowAnswer(true);
      setGameEnded(true);
      setMessages(prev => [...prev, { type: 'answer', text: `答案：${data.soup_bottom}` }]);
    } catch (err) {
      console.error('揭示答案失败', err);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) {
    return <div className="chat-container loading">加载中...</div>;
  }

  if (!puzzle) {
    return <div className="chat-container error">谜题加载失败</div>;
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← 返回
        </button>
        <span className="chat-title">{puzzle.title}</span>
        <div className="header-actions">
          <button className="hint-btn" onClick={handleHint} disabled={hintsUsed >= 3 || gameEnded}>
            提示({hintsUsed}/3)
          </button>
          <button className="reveal-btn" onClick={handleRevealAnswer} disabled={showAnswer}>
            揭示答案
          </button>
        </div>
      </div>

      <div className="chat-messages">
        <div className="soup-card">
          <span className="soup-label">汤面</span>
          <p className="soup-text">{puzzle.soup_face}</p>
        </div>

        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="message-content">
              {msg.judgement && <strong>{msg.judgement}</strong>}
              {msg.judgement ? ' - ' : ''}{msg.text}
            </div>
          </div>
        ))}

        <div className="tips-banner">
          <span className="tips-icon">💡</span>
          <span className="tips-text">提问技巧：尝试询问时间、地点、人物关系等关键信息</span>
        </div>
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          placeholder={gameEnded ? '游戏已结束' : '输入你的问题...'}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={gameEnded}
        />
        <button className="send-btn" onClick={handleSend} disabled={gameEnded}>
          提问
        </button>
      </div>
    </div>
  );
}

export default Chat;