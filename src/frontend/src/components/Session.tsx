import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import GameBoard, { GameBoardState, GameCellState } from './GameBoard';
import './Session.css';
import {api_server_url} from '../utils/links'

const Session: React.FC = () => {
    const { sessionId } = useParams<{ sessionId: string }>();
    const [gameKey, setGameKey] = useState(0);
    const [gameBoard, setGameBoard] = useState(Array(1).fill(null).map(() => Array(1).fill(1)));
    const [isGameStarted, setIsGameStarted] = useState(false);

    const startNewGame = async () => {
        const response = await fetch(`${api_server_url}/sessions/${sessionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "board_id": 0 }),
        });
        if (!response.ok) {
            alert("서버가 응답하지 않습니다.")
        }
        else {
            const jsonData = await response.json();
            const board: GameBoardState = jsonData.board;
            setGameKey(gameKey + 1); // 게임 보드를 리셋하기 위해 key 변경
            setGameBoard(board);
            setIsGameStarted(true);
        }
    };

    return (
        <div className="session-container">
        <button onClick={startNewGame} className="new-game-button">
            새 게임하기
        </button>
        {isGameStarted && sessionId && (
            <div className="gameboard-container">
            <GameBoard key={gameKey} sessionId={sessionId} gameBoard={gameBoard} />
            </div>
        )}
        </div>
    );
}

export default Session;
