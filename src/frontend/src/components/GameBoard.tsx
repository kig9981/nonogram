import React, { useState, useEffect, MouseEvent } from 'react';
import './GameBoard.css';

const NOT_SELECTED = 0;
const REVEALED = 1;
const MARK_X = 2;
const MARK_QUESTION = 3;
const MARK_WRONG = 4;

const WHITE = 0;
const BLACK = 1;

type PlayCellState = 0 | 1 | 2 | 3 | 4;
type GameCellState = 0 | 1;
type PlayBoardState = PlayCellState[][];
type GameBoardState = GameCellState[][];

const CellStateToStr = [
    "",
    "marked",
    "x",
    "question",
    "red-marked"
]


export type { GameCellState };
export type { GameBoardState };

interface GameBoardProps {
    gameBoard: GameBoardState;
}

const GameBoard: React.FC<GameBoardProps> = ({ gameBoard }) => {
    const numRow = gameBoard.length;
    const numCol = gameBoard[0].length;
    const initialBoard: PlayBoardState = Array(numRow).fill(null).map(() => Array(numCol).fill(NOT_SELECTED));
    const [board, setBoard] = useState<PlayBoardState>(initialBoard);
    const [rowHints, setRowHints] = useState<number[][]>([]);
    const [colHints, setColHints] = useState<number[][]>([]);

    useEffect(() => {
        setRowHints(generateHints(gameBoard, 'row'));
        setColHints(generateHints(gameBoard, 'col'));
    }, []);

    const generateHints = (board: GameBoardState, type: 'row' | 'col'): number[][] => {
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
                    if (gameBoard[rowIndex][colIndex] === BLACK) {
                        return c = REVEALED;
                    }
                    else if (c !== MARK_WRONG) {
                        alert("Incorrect!");
                        return c = MARK_WRONG;
                    }
                }
                return c;
            })
        );
        setBoard(newBoard);
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
                                className={`game-cell ${CellStateToStr[cell]}`}
                            >
                                {cell !== REVEALED && cell !== NOT_SELECTED && (
                                    <span className={`cell-content ${CellStateToStr[cell]}`}>
                                        {cell === MARK_X || cell == MARK_WRONG ? 'X' : cell === MARK_QUESTION ? '?' : ''}
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
