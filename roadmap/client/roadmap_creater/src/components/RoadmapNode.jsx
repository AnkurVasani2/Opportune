import React from 'react';

const RoadmapNode = ({ nodeData }) => {
  return (
    <div className="roadmap-node">
      <h3>{nodeData.title}</h3>
      {nodeData.subnodes && (
        <div className="subnodes">
          {nodeData.subnodes.map((subnode, index) => (
            <div key={index} className="subnode">
              <h4>{subnode.title}</h4>
              <p>{subnode.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RoadmapNode;
