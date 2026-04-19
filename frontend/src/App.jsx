import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Topics from './pages/Topics';
import PuzzleList from './pages/PuzzleList';
import Chat from './pages/Chat';
import Result from './pages/Result';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/topics" element={<Topics />} />
        <Route path="/puzzles/:topicId" element={<PuzzleList />} />
        <Route path="/chat/:topicId/:puzzleId" element={<Chat />} />
        <Route path="/result" element={<Result />} />
      </Routes>
    </Router>
  );
}

export default App;