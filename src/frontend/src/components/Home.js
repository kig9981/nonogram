import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

function Home() {
  const navigate = useNavigate();

  const createSession = async () => {
    // const response = await fetch('/session', {
    //   method: 'POST',
    // });
    // const data = await response.json();
    // navigate(`/${data.sessionId}`);
    // 임시로 1로 이동
    navigate('/1')
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
