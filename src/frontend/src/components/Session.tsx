import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import GameBoard, { GameBoardState, GameCellState } from './GameBoard';
import './Session.css';
import {api_server_url} from '../utils/links'


const Session: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const state = location.state as { sessionId?: string }
    const [gameKey, setGameKey] = useState(0);
    const [gameBoard, setGameBoard] = useState(() => {
        const savedGameBoard = sessionStorage.getItem('gameBoard');
        if (savedGameBoard) {
            return JSON.parse(savedGameBoard);
        }
        return Array(1).fill(null).map(() => Array(1).fill(1));
    });
    const [isGameStarted, setIsGameStarted] = useState(() => {
        const savedIsGameStarted = sessionStorage.getItem('isGameStarted');
        if (savedIsGameStarted) {
            return JSON.parse(savedIsGameStarted);
        }
        return false;
    });
    const [sessionId, setSessionId] = useState<string | null>(() => sessionStorage.getItem('sessionId'));
    const [isInitialized, setIsInitialized] = useState<Boolean>(false);
    const [isSessionValid, setSessionValid] = useState<Boolean>(false);

    useEffect(() => setIsInitialized(true), []);

    useEffect(() => {
        if (!isInitialized) {
            return;
        }
        console.log("Session entered");
        console.log(`sessionId: ${sessionId}`);
        console.log(`given sessionId: ${state.sessionId}`);
        const initializeSession = async () => {
            try {
                let currentSessionId = sessionId;
                if (!state.sessionId && sessionId === "") {
                    navigate("/");
                }
                if(state.sessionId && sessionId === "") {
                    setSessionId(state.sessionId);
                    currentSessionId = state.sessionId;
                }
                const response = await fetch(`${api_server_url}/sessions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ "session_id": currentSessionId }),
                });
                if (!response.ok) {
                    alert("서버가 응답하지 않습니다.");
                    navigate("/");
                }
                const jsonData = await response.json();
                setSessionId(jsonData.session_id);
                setSessionValid(true);
            }
            catch (error) {
                alert("unknown error");
                navigate("/");
            }
        };

        initializeSession();
    }, [isInitialized]);

    useEffect(() => {
        if (sessionId) {
            sessionStorage.setItem('sessionId', sessionId);
        }
    }, [sessionId]);
    useEffect(() => sessionStorage.setItem('isGameStarted', JSON.stringify(isGameStarted)), [isGameStarted]);
    useEffect(() => sessionStorage.setItem('gameBoard', JSON.stringify(gameBoard)), [gameBoard]);

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
        {isGameStarted && isSessionValid && sessionId && (
            <div className="gameboard-container">
            <GameBoard key={gameKey} sessionId={sessionId} gameBoard={gameBoard} />
            </div>
        )}
        </div>
    );
}

export default Session;
