import React, { useState, useEffect } from 'react';
import './GameBoard.css'; // CSS 파일을 임포트합니다.

function GameBoard() {
  const [board, setBoard] = useState([]);

  useEffect(() => {
    setBoard(Array(10).fill().map(() => Array(10).fill(null)));
  }, []);

  const handleLeftClick = (row, col) => {
    const newBoard = board.map((r, rowIndex) =>
      r.map((c, colIndex) => {
        if (rowIndex === row && colIndex === col) {
          return c === 'marked' ? null : 'marked'; // 토글 동작 추가
        }
        return c;
      })
    );
    setBoard(newBoard);
  };

  const handleRightClick = (row, col, e) => {
    e.preventDefault();
    const newBoard = board.map((r, rowIndex) =>
      r.map((c, colIndex) => {
        if (rowIndex === row && colIndex === col) {
          if (c === 'x') {
            return '?';
          } else if (c === '?') {
            return null;
          } else {
            return 'x';
          }
        }
        return c;
      })
    );
    setBoard(newBoard);
  };

  return (
    <div className="game-board">
      {board.map((row, rowIndex) => (
        <div key={rowIndex} className="game-row">
          {row.map((cell, colIndex) => (
            <div
              key={colIndex}
              onClick={() => handleLeftClick(rowIndex, colIndex)}
              onContextMenu={(e) => handleRightClick(rowIndex, colIndex, e)}
              className={`game-cell ${cell}`}
            >
              {cell !== 'marked' && cell !== null && (
                <span className={`cell-content ${cell}`}>
                  {cell === 'x' ? 'X' : cell === '?' ? '?' : ''}
                </span>
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export default GameBoard;
