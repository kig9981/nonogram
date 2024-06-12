import React, { useState, useEffect, MouseEvent } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './GameBoard.css';
import {api_server_url} from '../utils/links'

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
    sessionId: string,
    gameBoard: GameBoardState;
}

const GameBoard: React.FC<GameBoardProps> = ({ sessionId, gameBoard }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const numRow = gameBoard.length;
    const numCol = gameBoard[0].length;
    const initialBoard: PlayBoardState = Array(numRow).fill(null).map(() => Array(numCol).fill(NOT_SELECTED));
    const [board, setBoard] = useState<PlayBoardState>(initialBoard);
    const [rowHints, setRowHints] = useState<number[][]>([]);
    const [colHints, setColHints] = useState<number[][]>([]);
    const [isGameFinished, setIsGameFinished] = useState<Boolean>(false);
    const [unrevealedCounter, setUnrevealedCounter] = useState<number>(gameBoard.flat().filter(cell => cell === BLACK).length);

    useEffect(() => {
        const initializeBoard = async () => {
            setRowHints(generateHints(gameBoard, 'row'));
            setColHints(generateHints(gameBoard, 'col'));
            const response = await fetch(`${api_server_url}/sessions/${sessionId}/play`);
            console.log(response);
            if (response.ok) {
                const jsonData = await response.json();
                setBoard(jsonData.board);
            }
            else {
                console.log(await response.text());
            }
        };

        initializeBoard();
        
    }, [sessionId]);

    const sendClickMessage = async (x: number, y: number, state: PlayCellState) => {
        const response = await fetch(`${api_server_url}/sessions/${sessionId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "x": x, "y": y, "state": state }),
        });
        if (!response.ok) {
            alert("서버가 응답하지 않습니다.")
            console.log(await response.text());
        }
        else {
            const jsonData = await response.json();
            const responseCode: number = jsonData.response;
            console.log(JSON.stringify({"x": x, "y": y, "state": state, "response": responseCode}));
            return responseCode;
        }
        return 3;
    }

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

    const finishGame = () => {
        const newBoard = board.map((r, rowIndex) =>
            r.map((c, colIndex) => {
                if (gameBoard[rowIndex][colIndex] === WHITE && c !== MARK_WRONG) {
                    sendClickMessage(rowIndex, colIndex, MARK_X);
                    return MARK_X;
                }
                else if (gameBoard[rowIndex][colIndex] === BLACK) {
                    sendClickMessage(rowIndex, colIndex, REVEALED);
                    return REVEALED;
                }
                return c;
            })
        );
        setBoard(newBoard);
    }

    const handleLeftClick = (row: number, col: number) => {
        if (isGameFinished) return;
        const newBoard = board.map((r, rowIndex) =>
            r.map((c, colIndex) => {
                if (rowIndex === row && colIndex === col) {
                    if (gameBoard[rowIndex][colIndex] === BLACK) {
                        sendClickMessage(rowIndex, colIndex, REVEALED);
                        setUnrevealedCounter(unrevealedCounter - 1);
                        return c = REVEALED;
                    }
                    else if (c !== MARK_WRONG) {
                        sendClickMessage(rowIndex, colIndex, MARK_WRONG);
                        return c = MARK_WRONG;
                    }
                }
                return c;
            })
        );
        setBoard(newBoard);
        if (unrevealedCounter === 0) {
            setIsGameFinished(true);
            finishGame();
        }
    };

    const handleRightClick = (row: number, col: number, e: MouseEvent) => {
        e.preventDefault();
        if (isGameFinished) return;
        const newBoard = board.map((r, rowIndex) =>
            r.map((c, colIndex) => {
                if (rowIndex === row && colIndex === col) {
                    if (c === MARK_X) {
                        sendClickMessage(rowIndex, colIndex, MARK_QUESTION);
                        return MARK_QUESTION;
                    } else if (c === MARK_QUESTION) {
                        sendClickMessage(rowIndex, colIndex, NOT_SELECTED);
                        return NOT_SELECTED;
                    } else if (c === NOT_SELECTED) {
                        sendClickMessage(rowIndex, colIndex, MARK_X);
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
                                        {cell === MARK_X || cell === MARK_WRONG ? 'X' : cell === MARK_QUESTION ? '?' : ''}
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
