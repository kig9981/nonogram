import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';
import {api_server_url} from '../utils/links'

const Home: React.FC = () => {
    const navigate = useNavigate();
    const [sessionId, setSessionId] = useState<string | null>(null);

    const createSession = async () => {
        try {
            console.log(api_server_url);
            const response = await fetch(`${api_server_url}/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "session_id": sessionId }),
            });
            const jsonData = await response.json();
            // console.log(jsonData);
            const session_id = jsonData.session_id as string;
            setSessionId(session_id);
            // console.log(session_id);
            navigate('/session', { state: { sessionId: session_id } });
        }
        catch (error) {
            console.error('Fetch error:', error);
            alert('서버 응답이 없습니다. 잠시 후 다시 시도해주세요.');
        }
    };

    return (
        <div className="home-container">
        <button onClick={createSession} className="create-session-button">
            세션 생성하기
        </button>
        </div>
    );
}

export default Home;
