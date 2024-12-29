import React from 'react';

const Node = ({ title, description, subnodes }) => (
  <div className="node">
    <h3>{title}</h3>
    <p>{description}</p>
    {subnodes && (
      <div className="subnodes">
        {subnodes.map((subnode, index) => (
          <Node
            key={index}
            title={subnode.title}
            description={subnode.description}
            subnodes={subnode.subnodes}
          />
        ))}
      </div>
    )}
  </div>
);

export default Node;
