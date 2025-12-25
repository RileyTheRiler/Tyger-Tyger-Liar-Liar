import React from 'react';
import './Datamosh.css';

const Datamosh = ({ active }) => {
    if (!active) return null;

    return (
        <div className={`datamosh-container ${active ? 'active' : ''}`}>
            {/* We create multiple glitch layers that will simulate frame tearing */}
            <div className="mosh-slice" />
            <div className="mosh-slice" />
            <div className="mosh-slice" />
            <div className="mosh-slice" />
        </div>
    );
};

export default Datamosh;
