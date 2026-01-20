import React, { useEffect, useRef, memo } from 'react';
import './VHSEffect.css';

const VHSEffect = memo(({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    const containerRef = useRef(null);
    const counterRef = useRef(null);

    useEffect(() => {
        let interval;
        // Effect increases frequency with stress
        const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

        interval = setInterval(() => {
            if (!containerRef.current) return;

            // Scale noise and glitch with Mental Load (0-100) and Attention (0-100)
            const loadFactor = mentalLoad / 100.0;
            const attentionFactor = (attention || 0) / 100.0;

            const stressNoise = loadFactor * 0.6;
            const attentionGlitch = attentionFactor * 25; // Large tracking jumps

            // Random major glitch chance increases with load
            const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

            const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
            const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
            const trackingPos = (Math.random() * attentionFactor * 10); // Vertical tracking jitter

            // Critical scale jitter
            const criticalScale = mentalLoad > 90 ? (1 + Math.random() * 0.05) : 1;

            const container = containerRef.current;
            container.style.setProperty('--glitch-offset', `${glitchOffset.toFixed(2)}px`);
            container.style.setProperty('--noise-opacity', noiseOpacity.toFixed(3));
            container.style.setProperty('--tracking-pos', `${trackingPos.toFixed(2)}%`);
            container.style.setProperty('--critical-scale', criticalScale.toFixed(3));

            // Update counter text directly to avoid re-render
            if (counterRef.current) {
                const randomSec = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                counterRef.current.innerText = `SP 0:00:${randomSec}`;
            }

        }, baseInterval);

        return () => clearInterval(interval);
    }, [mentalLoad, attention, disorientation, instability]);

    const isCritical = mentalLoad > 90;
    const overlayOpacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;

    return (
        <div
            ref={containerRef}
            className={`vhs-container ${active ? 'active' : ''} ${instability ? 'instability-panic' : ''} ${isCritical ? 'critical-failure' : ''}`}
            style={{
                '--overlay-opacity': overlayOpacity
            }}
        >
            <div className="scanlines"></div>
            <div className="static-noise"></div>
            <div className="tracking-bar"></div>
            <div className="glitch-overlay"></div>

            {/* OSD (On Screen Display) - Reactive text */}
            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span ref={counterRef} className="tape-counter">SP 0:00:00</span>
            </div>
        </div>
    );
});

export default VHSEffect;
