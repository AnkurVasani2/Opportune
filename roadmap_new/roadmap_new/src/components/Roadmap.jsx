import React from 'react';
import Node from './Node';

const Roadmap = ({ data }) => {
  const renderNodes = (node) => (
    <Node
      key={node.title}
      title={node.title}
      description={node.description}
      subnodes={node.subnodes}
    />
  );

  return (
    <div className="roadmap">
      <h2>Roadmap</h2>
      <div className="nodes">
        {Object.values(data).map((node) => renderNodes(node))}
      </div>
    </div>
  );
};

export default Roadmap;
