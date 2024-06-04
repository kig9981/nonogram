import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import GameBoard from './GameBoard';
import './Session.css';

const Session: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [gameKey, setGameKey] = useState(0);
  const [numRow, setNumRow] = useState(10);
  const [numCol, setNumCol] = useState(10);

  const startNewGame = async () => {
    await fetch(`/session/${sessionId}/new-game`, {
      method: 'POST',
    });
    setGameKey(gameKey + 1); // 게임 보드를 리셋하기 위해 key 변경
    setNumRow(10);
    setNumCol(10);
  };

  return (
    <div className="session-container">
      <button onClick={startNewGame} className="new-game-button">
        새 게임하기
      </button>
      <div className="gameboard-container">
        <GameBoard key={gameKey} numRow={numRow} numCol={numCol} />
      </div>
    </div>
  );
}

export default Session;
