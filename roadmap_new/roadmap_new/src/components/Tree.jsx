import React, { useState } from "react";
import "./Tree.css";

const TreeNode = ({ node, level = 0 }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleOpen = () => {
    setIsOpen((prev) => !prev);
  };

  return (
    <div className="tree-node" style={{ marginLeft: `${level * 20}px` }}>
      <div className="node-header" onClick={toggleOpen}>
        <span className={`toggle-icon ${isOpen ? "open" : ""}`}>
          {node.subnodes ? (isOpen ? "▼" : "▶") : ""}
        </span>
        <h3 className="node-title">{node.title}</h3>
      </div>
      {isOpen && (
        <div className="node-description">
          <p>{node.description}</p>
          {node.subnodes && (
            <div className="subnodes">
              {node.subnodes.map((subnode, index) => (
                <TreeNode key={index} node={subnode} level={level + 1} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const Tree = ({ data }) => {
  return (
    <div className="tree-container">
      {Object.values(data).map((node, index) => (
        <TreeNode key={index} node={node} />
      ))}
    </div>
  );
};

export default Tree;
