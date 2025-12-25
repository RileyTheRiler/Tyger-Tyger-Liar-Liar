import React, { useEffect, useState } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    const [renderParams, setRenderParams] = useState({
        glitchOffset: 0,
        noiseOpacity: 0.1
    });

    useEffect(() => {
        let interval;
        // Effect increases frequency with stress
        const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

        interval = setInterval(() => {
            // Scale noise and glitch with Mental Load (0-100) and Attention (0-100)
            // Attention adds a "magnetic" interference (tracking loss)
            // Mental Load adds "static" (noise)

            const loadFactor = mentalLoad / 100.0;
            const attentionFactor = (attention || 0) / 100.0;

            const stressNoise = loadFactor * 0.6;
            const attentionGlitch = attentionFactor * 25; // Large tracking jumps

            // Random major glitch chance increases with load
            const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

            setRenderParams({
                glitchOffset: (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2),
                noiseOpacity: 0.05 + stressNoise + (Math.random() * 0.1),
                trackingPos: (Math.random() * attentionFactor * 10) // Vertical tracking jitter
            });
        }, baseInterval);

        return () => clearInterval(interval);
    }, [mentalLoad, attention, disorientation, instability]);

    // Critical Failure State Style
    const criticalStyle = mentalLoad > 90 ? {
        filter: 'grayscale(1) contrast(1.5) brightness(0.8)',
        transform: `scale(${1 + Math.random() * 0.05})`
    } : {};

    return (
        <div className={`vhs-container active ${instability ? 'instability-panic' : ''}`}>
            <div className="scanlines"></div>
            <div className="static-noise" style={{ opacity: renderParams.noiseOpacity }}></div>
            <div className="tracking-bar" style={{ top: `${10 + renderParams.trackingPos}%` }}></div>
            <div className="glitch-overlay"
                style={{
                    transform: `translateX(${renderParams.glitchOffset}px)`,
                    opacity: active ? (0.5 + (mentalLoad / 200)) : 0.2,
                    ...criticalStyle
                }}>
            </div>

            {/* OSD (On Screen Display) - Reactive text */}
            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span className="tape-counter">SP 0:00:{Math.floor(Math.random() * 60).toString().padStart(2, '0')}</span>
            </div>
        </div>
    );
};

export default VHSEffect;
