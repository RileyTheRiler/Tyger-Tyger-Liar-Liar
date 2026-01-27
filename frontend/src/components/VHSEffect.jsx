import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    const staticNoiseRef = useRef(null);
    const trackingBarRef = useRef(null);
    const glitchOverlayRef = useRef(null);
    const tapeCounterRef = useRef(null);

    // Keep track of latest props for the animation loop
    const propsRef = useRef({ mentalLoad, attention, disorientation, instability, active });

    useEffect(() => {
        propsRef.current = { mentalLoad, attention, disorientation, instability, active };
    }, [mentalLoad, attention, disorientation, instability, active]);

    useEffect(() => {
        let animationFrameId;
        let lastTime = 0;

        const animate = (time) => {
            const { mentalLoad, attention, disorientation, instability, active } = propsRef.current;

            // Effect increases frequency with stress
            const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

            if (time - lastTime >= baseInterval) {
                lastTime = time;

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

                // Apply styles directly to DOM elements
                if (staticNoiseRef.current) {
                    staticNoiseRef.current.style.opacity = noiseOpacity;
                }

                if (trackingBarRef.current) {
                    // Base 10% + jitter
                    trackingBarRef.current.style.top = `${10 + trackingPos}%`;
                }

                if (glitchOverlayRef.current) {
                    let transform = `translateX(${glitchOffset}px)`;
                    let filter = 'none';

                    // Critical Failure State Style
                    if (mentalLoad > 90) {
                        filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        transform += ` scale(${1 + Math.random() * 0.05})`;
                    }

                    glitchOverlayRef.current.style.transform = transform;
                    glitchOverlayRef.current.style.filter = filter;

                    const baseOpacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;
                    glitchOverlayRef.current.style.opacity = baseOpacity;
                }

                if (tapeCounterRef.current) {
                    const randomSec = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                    tapeCounterRef.current.innerText = `SP 0:00:${randomSec}`;
                }
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(animationFrameId);
    }, []); // Run loop once, read from refs

    return (
        <div className={`vhs-container active ${instability ? 'instability-panic' : ''}`}>
            <div className="scanlines"></div>
            <div className="static-noise" ref={staticNoiseRef}></div>
            <div className="tracking-bar" ref={trackingBarRef} style={{ top: '10%' }}></div>
            <div className="glitch-overlay" ref={glitchOverlayRef}></div>

            {/* OSD (On Screen Display) - Reactive text */}
            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span className="tape-counter" ref={tapeCounterRef}>SP 0:00:00</span>
            </div>
        </div>
    );
};

export default VHSEffect;
