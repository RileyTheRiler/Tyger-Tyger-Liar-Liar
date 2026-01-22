import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    const noiseRef = useRef(null);
    const trackingRef = useRef(null);
    const glitchRef = useRef(null);
    const counterRef = useRef(null);

    // Store latest props for use in animation loop without restarting it
    const propsRef = useRef({ active, mentalLoad, attention, disorientation, instability });

    useEffect(() => {
        propsRef.current = { active, mentalLoad, attention, disorientation, instability };
    }, [active, mentalLoad, attention, disorientation, instability]);

    useEffect(() => {
        let animationFrameId;
        let lastTime = 0;

        const animate = (time) => {
            const { active, mentalLoad, attention, disorientation, instability } = propsRef.current;

            // Calculate interval based on current props
            const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

            if (time - lastTime > baseInterval) {
                lastTime = time;

                // --- Calculations ---
                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;
                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25;
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
                const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                const trackingPos = (Math.random() * attentionFactor * 10);

                // --- Apply Styles Directly ---

                if (noiseRef.current) {
                    noiseRef.current.style.opacity = noiseOpacity;
                }

                if (trackingRef.current) {
                    // CSS animation might override this if active, but we preserve original logic
                    trackingRef.current.style.top = `${10 + trackingPos}%`;
                }

                if (glitchRef.current) {
                    // Base opacity logic
                    const baseOpacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;
                    glitchRef.current.style.opacity = baseOpacity;

                    // Transform logic
                    let transform = `translateX(${glitchOffset}px)`;
                    let filter = '';

                    // Critical Style Logic
                    if (mentalLoad > 90) {
                        filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        const scale = 1 + Math.random() * 0.05;
                        transform += ` scale(${scale})`;
                    } else {
                        // Reset filter if not critical (important to clear it)
                        filter = 'none';
                    }

                    glitchRef.current.style.transform = transform;
                    glitchRef.current.style.filter = filter;
                }

                if (counterRef.current) {
                     // Random seconds 00-59 to match original chaotic effect
                     const sec = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                     counterRef.current.innerText = `SP 0:00:${sec}`;
                }
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(animationFrameId);
    }, []); // Loop runs forever and reads from propsRef

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
