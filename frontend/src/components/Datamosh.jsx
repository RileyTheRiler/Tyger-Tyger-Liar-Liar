import React from 'react';
import './Datamosh.css';

const Datamosh = ({ active }) => {
    if (!active) return null;

    return (
        <>
            <div className={`datamosh-container ${active ? 'active' : ''}`}>
                <div className="mosh-slice" />
                <div className="mosh-slice" />
                <div className="mosh-slice" />
                <div className="mosh-slice" />
                <div className="mosh-noise" />
            </div>

            {/* SVG Filter for liquid displacement/glitch */}
            <svg style={{ display: 'none' }}>
                <defs>
                    <filter id="datamosh-filter">
                        <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" result="noise" />
                        <feDisplacementMap in="SourceGraphic" in2="noise" scale="15" />
                    </filter>
                    <filter id="chromatic-aberration">
                        <feOffset in="SourceGraphic" dx="3" dy="0" result="red" />
                        <feOffset in="SourceGraphic" dx="-3" dy="0" result="blue" />
                        <feMerge>
                            <feMergeNode in="red" />
                            <feMergeNode in="blue" />
                        </feMerge>
                    </filter>
                </defs>
            </svg>
        </>
    );
};

export default Datamosh;
