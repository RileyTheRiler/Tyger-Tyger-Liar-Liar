import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    const noiseRef = useRef(null);
    const trackingRef = useRef(null);
    const glitchRef = useRef(null);
    const counterRef = useRef(null);

    // Store props in a ref to access them in the animation loop without restarting it
    const propsRef = useRef({ active, mentalLoad, attention, disorientation, instability });

    useEffect(() => {
        propsRef.current = { active, mentalLoad, attention, disorientation, instability };
    }, [active, mentalLoad, attention, disorientation, instability]);

    useEffect(() => {
        let animationFrameId;
        let lastUpdate = 0;
        let lastCounterUpdate = 0;

        const animate = (timestamp) => {
            const { active, mentalLoad, attention, disorientation, instability } = propsRef.current;

            // Base interval determination
            const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

            // Check if it's time to update visual jitter
            if (timestamp - lastUpdate > baseInterval) {
                lastUpdate = timestamp;

                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;

                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25;

                // Random major glitch chance increases with load
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
                const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                const trackingPos = (Math.random() * attentionFactor * 10);

                if (noiseRef.current) {
                    noiseRef.current.style.opacity = noiseOpacity;
                }

                if (trackingRef.current) {
                    trackingRef.current.style.top = `${10 + trackingPos}%`;
                }

                if (glitchRef.current) {
                    const baseOpacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;
                    let transform = `translateX(${glitchOffset}px)`;
                    let filter = 'none';

                    // Critical Failure State
                    if (mentalLoad > 90) {
                        filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        transform += ` scale(${1 + Math.random() * 0.05})`;
                    }

                    glitchRef.current.style.transform = transform;
                    glitchRef.current.style.opacity = baseOpacity;
                    glitchRef.current.style.filter = filter;
                }
            }

            // Update counter "glitch" effect
            if (timestamp - lastCounterUpdate > 100) {
                 lastCounterUpdate = timestamp;
                 if (counterRef.current) {
                     counterRef.current.textContent = `SP 0:00:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`;
                 }
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(animationFrameId);
    }, []); // Empty dependency array, relies on propsRef

    return (
        <div className={`vhs-container active ${instability ? 'instability-panic' : ''}`}>
            <div className="scanlines"></div>
            <div className="static-noise" ref={noiseRef}></div>
            <div className="tracking-bar" ref={trackingRef}></div>
            <div className="glitch-overlay" ref={glitchRef}></div>

            {/* OSD (On Screen Display) - Reactive text */}
            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span className="tape-counter" ref={counterRef}>SP 0:00:00</span>
            </div>
        </div>
    );
};

export default VHSEffect;
