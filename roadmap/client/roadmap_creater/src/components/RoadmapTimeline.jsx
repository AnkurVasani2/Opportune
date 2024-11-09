import React, { useState } from 'react';
import Modal from './Modal';  // Create a modal component

const RoadmapTimeline = ({ roadmapData }) => {
  const [modalContent, setModalContent] = useState(null); // State to track content for modal

  // Recursive function to render subnodes
  const renderSubnodes = (subnodes) => {
    return subnodes.map((subnode, index) => (
      <li key={index}>
        <strong>{subnode.title}:</strong> {subnode.description}
        {subnode.subnodes && subnode.subnodes.length > 0 && (
          <ul className="subnodes">
            {renderSubnodes(subnode.subnodes)}
          </ul>
        )}
      </li>
    ));
  };

  // Function to handle click and open modal with the .blue div content
  const handleOpenModal = (node) => {
    setModalContent(
      <div className="blue">
        <p>{node.description}</p>
        {node.subnodes && node.subnodes.length > 0 && (
          <ul>
            {renderSubnodes(node.subnodes)}
          </ul>
        )}
      </div>
    );
  };

  // Function to render nodes
  const renderNodes = () => {
    return Object.keys(roadmapData).map((nodeKey) => {
      const node = roadmapData[nodeKey];
      return (
        <div
          key={nodeKey}
          className="roadmap-node"
          onClick={() => handleOpenModal(node)}  // Open modal on click
          style={{ cursor: 'pointer' }}  // Add cursor pointer to indicate clickability
        >
          <h2>{node.title}</h2>
        </div>
      );
    });
  };

  return (
    <div className="roadmap-container">
      {roadmapData ? renderNodes() : <div>Loading...</div>}
      {modalContent && <Modal content={modalContent} onClose={() => setModalContent(null)} />}
    </div>
  );
};

export default RoadmapTimeline;
