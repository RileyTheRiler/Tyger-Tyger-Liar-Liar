import React, { useEffect, useState } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active }) => {
    const [renderParams, setRenderParams] = useState({
        glitchOffset: 0,
        noiseOpacity: 0.1
    });

    useEffect(() => {
        let interval;
        if (active) {
            // Randomize glitches slightly when active
            interval = setInterval(() => {
                setRenderParams({
                    glitchOffset: Math.random() * 10 - 5,
                    noiseOpacity: 0.1 + Math.random() * 0.1
                });
            }, 100);
        }
        return () => clearInterval(interval);
    }, [active]);

    return (
        <div className={`vhs-container ${active ? 'active' : ''}`}>
            <div className="scanlines"></div>
            <div className="static-noise" style={{ opacity: renderParams.noiseOpacity }}></div>
            <div className="tracking-bar"></div>
            <div className="glitch-overlay" style={{ transform: `translateX(${renderParams.glitchOffset}px)` }}></div>

            {/* OSD (On Screen Display) - Play/Rec text */}
            {active && (
                <div className="vhs-osd">
                    <span className="play-text">PLAY</span>
                    <span className="tape-counter">SP 0:00:{Math.floor(Math.random() * 60).toString().padStart(2, '0')}</span>
                </div>
            )}
        </div>
    );
};

export default VHSEffect;
