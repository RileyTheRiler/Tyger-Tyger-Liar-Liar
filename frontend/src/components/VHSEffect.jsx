import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    const containerRef = useRef(null);
    const counterRef = useRef(null);

    // Refs for state that updates inside the loop without triggering re-renders
    const stateRef = useRef({
        lastUpdate: 0,
        baseInterval: 150
    });

    // Update base interval when props change, without restarting the loop if possible
    useEffect(() => {
        stateRef.current.baseInterval = instability ? 30 : (disorientation ? 80 : 150);
    }, [instability, disorientation]);

    useEffect(() => {
        let animationFrameId;

        const animate = (time) => {
            const state = stateRef.current;

            // Throttle updates based on baseInterval
            if (time - state.lastUpdate > state.baseInterval) {
                state.lastUpdate = time;

                // Logic derived from original component
                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;
                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25;
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
                const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                const trackingPos = (Math.random() * attentionFactor * 10);

                // Critical Failure logic
                const isCritical = mentalLoad > 90;
                const criticalScale = isCritical ? (1 + Math.random() * 0.05) : 1;

                // Apply to DOM via CSS Variables
                if (containerRef.current) {
                    containerRef.current.style.setProperty('--glitch-offset', `${glitchOffset}px`);
                    containerRef.current.style.setProperty('--noise-opacity', noiseOpacity);
                    containerRef.current.style.setProperty('--tracking-pos', `${trackingPos}%`);
                    containerRef.current.style.setProperty('--critical-scale', criticalScale);

                    if (isCritical) {
                        containerRef.current.style.setProperty('--critical-filter', 'grayscale(1) contrast(1.5) brightness(0.8)');
                    } else {
                        containerRef.current.style.removeProperty('--critical-filter');
                    }
                }

                // Update Tape Counter
                if (counterRef.current) {
                    const secs = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                    counterRef.current.textContent = `SP 0:00:${secs}`;
                }
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(animationFrameId);
    }, [mentalLoad, attention]);

    // Glitch Overlay Opacity calculation
    const overlayOpacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;

    return (
        <div
            ref={containerRef}
            className={`vhs-container active ${instability ? 'instability-panic' : ''}`}
            style={{
                '--overlay-opacity': overlayOpacity
            }}
        >
            <div className="scanlines"></div>
            <div className="static-noise"></div>
            <div className="tracking-bar"></div>
            <div className="glitch-overlay"></div>

            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span ref={counterRef} className="tape-counter">SP 0:00:00</span>
            </div>
        </div>
    );
};

export default VHSEffect;
