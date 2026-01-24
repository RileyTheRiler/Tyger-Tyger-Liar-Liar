import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    // Refs for DOM elements to update directly
    const noiseRef = useRef(null);
    const trackingRef = useRef(null);
    const glitchRef = useRef(null);
    const timerRef = useRef(null);

    // Ref for props to access latest values in animation loop without dependencies
    const propsRef = useRef({ active, mentalLoad, attention, disorientation, instability });

    // Update propsRef when props change
    useEffect(() => {
        propsRef.current = { active, mentalLoad, attention, disorientation, instability };
    }, [active, mentalLoad, attention, disorientation, instability]);

    useEffect(() => {
        let animationFrameId;
        let lastTime = 0;

        const animate = (time) => {
            const { active, mentalLoad, attention, disorientation, instability } = propsRef.current;

            // Effect increases frequency with stress
            const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

            if (time - lastTime > baseInterval) {
                // Scale noise and glitch with Mental Load (0-100) and Attention (0-100)
                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;

                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25; // Large tracking jumps

                // Random major glitch chance increases with load
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                // Calculate values
                const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
                const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                const trackingPos = (Math.random() * attentionFactor * 10); // Vertical tracking jitter

                // Apply to refs
                if (noiseRef.current) {
                    noiseRef.current.style.opacity = noiseOpacity;
                }

                if (trackingRef.current) {
                    trackingRef.current.style.top = `${10 + trackingPos}%`;
                }

                if (glitchRef.current) {
                    let transform = `translateX(${glitchOffset}px)`;
                    let filter = '';
                    let opacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;

                    // Critical Failure State Style
                    if (mentalLoad > 90) {
                        filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        const scale = 1 + Math.random() * 0.05;
                        transform += ` scale(${scale})`;
                    } else {
                        filter = 'none';
                    }

                    glitchRef.current.style.transform = transform;
                    glitchRef.current.style.filter = filter;
                    glitchRef.current.style.opacity = opacity;
                }

                // Update timer text (simulating the random flicker)
                if (timerRef.current) {
                     // SP 0:00:XX
                     const randomSec = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                     // We only update the seconds part to avoid full text layout thrashing if possible,
                     // but textContent is fast enough for this small string.
                     // However, we want to preserve "SP 0:00:" prefix.
                     timerRef.current.textContent = `SP 0:00:${randomSec}`;
                }

                lastTime = time;
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(animationFrameId);
    }, []); // Empty dependency array -> runs once on mount

    return (
        <div className={`vhs-container active ${instability ? 'instability-panic' : ''}`}>
            <div className="scanlines"></div>
            <div
                ref={noiseRef}
                className="static-noise"
                style={{ opacity: 0.1 }} // Initial value
            ></div>
            <div
                ref={trackingRef}
                className="tracking-bar"
                style={{ top: '10%' }} // Initial value
            ></div>
            <div
                ref={glitchRef}
                className="glitch-overlay"
                style={{
                    transform: 'translateX(0px)',
                    opacity: active ? 0.5 : 0.2, // Initial value
                }}
            >
            </div>

            {/* OSD (On Screen Display) - Reactive text */}
            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span
                    ref={timerRef}
                    className="tape-counter"
                >
                    SP 0:00:00
                </span>
            </div>
        </div>
    );
};

export default VHSEffect;
