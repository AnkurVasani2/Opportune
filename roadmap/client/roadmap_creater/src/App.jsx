  import React, { useState } from 'react';
import InputForm from './components/InputForm';
import RoadmapTimeline from './components/RoadmapTimeline';
import './css/roadmap.css';

const App = () => {
  const [roadmapData, setRoadmapData] = useState(null);

  const handleRoadmapGeneration = async (technology) => {
    try {
      const response = await fetch('https://meerkat-saving-seriously.ngrok-free.app/generate-roadmap', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ technology }),
      });
      const data = await response.json();
      setRoadmapData(data);  // Set roadmap data (JSON format)
    } catch (error) {
      console.error("Error fetching roadmap:", error);
    }
  };

  return (
    <div className="app-container">
      <InputForm onSubmit={handleRoadmapGeneration} />
      {roadmapData ? (
        <RoadmapTimeline roadmapData={roadmapData} />
      ) : (
        <div>Loading roadmap...</div>
      )}
    </div>
  );
};

export default App;
