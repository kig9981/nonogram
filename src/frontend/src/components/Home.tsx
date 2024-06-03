import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const createSession = async () => {
    // 임시로 세션 ID를 1로 설정하여 이동
    navigate('/1');
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
