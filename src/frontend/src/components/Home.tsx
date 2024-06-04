import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';
import {api_server_url} from '../utils/links'

const Home: React.FC = () => {
    const navigate = useNavigate();

    const createSession = async () => {
        console.log(api_server_url);
        const response = await fetch(api_server_url + `/sessions`, {
            method: 'POST',
        });
        const jsonData = await response.json();
        console.log(jsonData);
        navigate('/' + jsonData.session_id);
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
