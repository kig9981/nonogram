import React, { useState, useEffect, MouseEvent } from 'react';
import './GameBoard.css';

const NOT_SELECTED = 0;
const REVEALED = 1;
const MARK_X = 2;
const MARK_QUESTION = 3;

type CellState = 0 | 1 | 2 | 3;
type BoardState = CellState[][];

interface GameBoardProps {
  numRow: number;
  numCol: number;
}

const GameBoard: React.FC<GameBoardProps> = ({ numRow, numCol }) => {
  const initialBoard: BoardState = Array(numRow).fill(null).map(() => Array(numCol).fill(NOT_SELECTED));
  const [board, setBoard] = useState<BoardState>(initialBoard);
  const [rowHints, setRowHints] = useState<number[][]>([]);
  const [colHints, setColHints] = useState<number[][]>([]);

  useEffect(() => {
    setRowHints(generateHints(initialBoard, 'row'));
    setColHints(generateHints(initialBoard, 'col'));
  }, []);

  const generateHints = (board: BoardState, type: 'row' | 'col'): number[][] => {
    const hints: number[][] = [];
    if (type === 'row') {
      for (let row of board) {
        const hint: number[] = [];
        let count = 0;
        for (let cell of row) {
          if (cell === REVEALED) {
            count++;
          } else if (count > 0) {
            hint.push(count);
            count = 0;
          }
        }
        if (count > 0) hint.push(count);
        hints.push(hint.reverse());
      }
    } else if (type === 'col') {
      for (let col = 0; col < board[0].length; col++) {
        const hint: number[] = [];
        let count = 0;
        for (let row = 0; row < board.length; row++) {
          if (board[row][col] === REVEALED) {
            count++;
          } else if (count > 0) {
            hint.push(count);
            count = 0;
          }
        }
        if (count > 0) hint.push(count);
        hints.push(hint.reverse());
      }
    }
    return hints;
  };

  const handleLeftClick = (row: number, col: number) => {
    const newBoard = board.map((r, rowIndex) =>
      r.map((c, colIndex) => {
        if (rowIndex === row && colIndex === col) {
          return c = REVEALED;
        }
        return c;
      })
    );
    setBoard(newBoard);
    setRowHints(generateHints(newBoard, 'row'));
    setColHints(generateHints(newBoard, 'col'));
  };

  const handleRightClick = (row: number, col: number, e: MouseEvent) => {
    e.preventDefault();
    const newBoard = board.map((r, rowIndex) =>
      r.map((c, colIndex) => {
        if (rowIndex === row && colIndex === col) {
          if (c === MARK_X) {
            return MARK_QUESTION;
          } else if (c === MARK_QUESTION) {
            return NOT_SELECTED;
          } else if (c === NOT_SELECTED) {
            return MARK_X;
          }
        }
        return c;
      })
    );
    setBoard(newBoard);
    setRowHints(generateHints(newBoard, 'row'));
    setColHints(generateHints(newBoard, 'col'));
  };

  return (
    <div className="game-board-container">
      <div className="unused"> </div>
      <div className="hints-row">
        {colHints.map((hint, index) => (
          <div key={index} className="hint-col">
            {hint.map((num, i) => (
              <div key={i} className="hint-num">{num}</div>
            ))}
          </div>
        ))}
      </div>
      <div className="hints-column">
        {rowHints.map((hint, index) => (
          <div key={index} className="hint-row">
            {hint.map((num, i) => (
              <span key={i} className="hint-num">{num}</span>
            ))}
          </div>
        ))}
      </div>
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
                {cell !== REVEALED && cell !== NOT_SELECTED && (
                  <span className={`cell-content ${cell}`}>
                    {cell === MARK_X ? 'X' : cell === MARK_QUESTION ? '?' : ''}
                  </span>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default GameBoard;
