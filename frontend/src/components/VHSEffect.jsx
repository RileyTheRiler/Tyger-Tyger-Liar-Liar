import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    // Direct DOM references for high-frequency updates without React re-renders
    const noiseRef = useRef(null);
    const trackingRef = useRef(null);
    const glitchRef = useRef(null);
    const counterRef = useRef(null);

    // Animation state
    const requestRef = useRef();
    const lastUpdateRef = useRef(0);

    useEffect(() => {
        // Effect increases frequency with stress
        const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

        const animate = (time) => {
            // Throttle updates to match the intended visual framerate (baseInterval)
            if (time - lastUpdateRef.current >= baseInterval) {
                lastUpdateRef.current = time;

                // Scale noise and glitch with Mental Load (0-100) and Attention (0-100)
                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;

                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25; // Large tracking jumps

                // Random major glitch chance increases with load
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                // Calculate visual parameters
                const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
                const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                const trackingPos = (Math.random() * attentionFactor * 10);

                // --- Direct DOM Updates ---

                // 1. Static Noise Opacity
                if (noiseRef.current) {
                    noiseRef.current.style.opacity = noiseOpacity.toFixed(3);
                }

                // 2. Tracking Bar Position
                if (trackingRef.current) {
                    trackingRef.current.style.top = `${(10 + trackingPos).toFixed(1)}%`;
                }

                // 3. Glitch Overlay Transform & Critical State
                if (glitchRef.current) {
                    let transform = `translateX(${glitchOffset.toFixed(1)}px)`;
                    let filter = '';

                    // Critical Failure State Logic (previously inside render)
                    if (mentalLoad > 90) {
                        filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        const scale = 1 + Math.random() * 0.05;
                        transform += ` scale(${scale.toFixed(3)})`;
                    }

                    glitchRef.current.style.transform = transform;
                    glitchRef.current.style.filter = filter;
                    // Opacity logic from original component
                    glitchRef.current.style.opacity = active ? (0.5 + (mentalLoad / 200)).toFixed(2) : '0.2';
                }

                // 4. Tape Counter (simulating jitter/corruption)
                if (counterRef.current) {
                    const randomSec = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                    counterRef.current.textContent = `SP 0:00:${randomSec}`;
                }
            }

            requestRef.current = requestAnimationFrame(animate);
        };

        requestRef.current = requestAnimationFrame(animate);

        return () => {
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [active, mentalLoad, attention, disorientation, instability]);

    return (
        <div className={`vhs-container active ${instability ? 'instability-panic' : ''}`}>
            <div className="scanlines"></div>
            <div ref={noiseRef} className="static-noise"></div>
            <div ref={trackingRef} className="tracking-bar"></div>
            <div ref={glitchRef} className="glitch-overlay"></div>

            {/* OSD (On Screen Display) - Reactive text */}
            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span ref={counterRef} className="tape-counter">SP 0:00:00</span>
            </div>
        </div>
    );
};

export default VHSEffect;
