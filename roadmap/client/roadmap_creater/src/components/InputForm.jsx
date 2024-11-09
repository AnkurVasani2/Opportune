import React, { useState } from 'react';

const InputForm = ({ onSubmit }) => {
  const [technology, setTechnology] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(technology);
  };

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter a technology (e.g. Python, Machine Learning)"
        value={technology}
        onChange={(e) => setTechnology(e.target.value)}
      />
      <button type="submit">Generate Roadmap</button>
    </form>
  );
};


export default InputForm;
