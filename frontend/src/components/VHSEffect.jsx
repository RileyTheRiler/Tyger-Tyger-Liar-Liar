import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    // Refs for direct DOM manipulation to avoid React render cycle overhead
    const glitchRef = useRef(null);
    const noiseRef = useRef(null);
    const trackingRef = useRef(null);
    const counterRef = useRef(null);

    // Store props in ref to access latest values in animation loop without re-triggering effect
    const propsRef = useRef({ active, mentalLoad, attention, disorientation, instability });

    useEffect(() => {
        propsRef.current = { active, mentalLoad, attention, disorientation, instability };
    }, [active, mentalLoad, attention, disorientation, instability]);

    useEffect(() => {
        let animationFrameId;
        let lastUpdate = 0;

        const loop = (timestamp) => {
            const { mentalLoad, attention, disorientation, instability, active } = propsRef.current;

            // Effect increases frequency with stress (logic from original component)
            const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

            if (timestamp - lastUpdate >= baseInterval) {
                lastUpdate = timestamp;

                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;
                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25; // Large tracking jumps

                // Random major glitch chance increases with load
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
                const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                const trackingPos = (Math.random() * attentionFactor * 10); // Vertical tracking jitter

                // Direct DOM updates
                if (glitchRef.current) {
                    // Critical Failure State Style Logic
                    // Original: mentalLoad > 90 ? { filter: ..., transform: scale(...) } : {}
                    const isCritical = mentalLoad > 90;
                    const baseOpacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;

                    if (isCritical) {
                        glitchRef.current.style.filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        const scale = 1 + Math.random() * 0.05;
                        glitchRef.current.style.transform = `translateX(${glitchOffset}px) scale(${scale})`;
                    } else {
                        glitchRef.current.style.filter = '';
                        glitchRef.current.style.transform = `translateX(${glitchOffset}px)`;
                    }
                    glitchRef.current.style.opacity = baseOpacity;
                }

                if (noiseRef.current) {
                    noiseRef.current.style.opacity = noiseOpacity;
                }

                if (trackingRef.current) {
                    trackingRef.current.style.top = `${10 + trackingPos}%`;
                }

                if (counterRef.current) {
                    // Jittery counter effect
                    const sec = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                    counterRef.current.textContent = `SP 0:00:${sec}`;
                }
            }

            animationFrameId = requestAnimationFrame(loop);
        };

        animationFrameId = requestAnimationFrame(loop);

        return () => cancelAnimationFrame(animationFrameId);
    }, []); // Run once, depend on propsRef for updates

    return (
        <div className={`vhs-container active ${instability ? 'instability-panic' : ''}`}>
            <div className="scanlines"></div>
            <div className="static-noise" ref={noiseRef} style={{ opacity: 0.1 }}></div>
            <div className="tracking-bar" ref={trackingRef} style={{ top: '10%' }}></div>
            <div className="glitch-overlay"
                ref={glitchRef}
                style={{
                    // Initial styles
                    opacity: active ? (0.5 + (mentalLoad / 200)) : 0.2
                }}>
            </div>

            {/* OSD (On Screen Display) - Reactive text */}
            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span className="tape-counter" ref={counterRef}>SP 0:00:00</span>
            </div>
        </div>
    );
};

export default VHSEffect;
