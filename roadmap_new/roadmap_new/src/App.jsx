import React, { useState } from 'react';
import axios from 'axios';
import Tree from './components/Tree';

const App = () => {
  const [technology, setTechnology] = useState('');
  const [treeData, setTreeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setTreeData(null);

    try {
      const response = await axios.post(
        'https://meerkat-saving-seriously.ngrok-free.app/generate-roadmap',
        { technology }
      );
      setTreeData(response.data);
    } catch (err) {
      setError('Failed to fetch roadmap. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Roadmap Generator</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter technology (e.g., Python)"
          value={technology}
          onChange={(e) => setTechnology(e.target.value)}
        />
        <button type="submit">Generate Roadmap</button>
      </form>
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {treeData && <Tree data={treeData} />}
    </div>
  );
};

export default App;
