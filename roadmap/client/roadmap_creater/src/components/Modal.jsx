import React from 'react';
import './Modal.css';  // We'll add some basic styles for the modal

const Modal = ({ content, onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>Close</button>
        {content}
      </div>
    </div>
  );
};

export default Modal;
