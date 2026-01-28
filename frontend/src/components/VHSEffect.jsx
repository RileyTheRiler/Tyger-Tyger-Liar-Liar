import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    // Refs for DOM elements to bypass React render cycle
    const noiseRef = useRef(null);
    const trackingBarRef = useRef(null);
    const glitchRef = useRef(null);
    const counterRef = useRef(null);

    // Ref to hold latest props for the animation loop
    const propsRef = useRef({ mentalLoad, attention, disorientation, instability });

    // Update props ref when props change
    useEffect(() => {
        propsRef.current = { mentalLoad, attention, disorientation, instability };
    }, [mentalLoad, attention, disorientation, instability]);

    useEffect(() => {
        let animationFrameId;
        let lastUpdate = 0;
        let frames = 0;
        let seconds = Math.floor(Math.random() * 60); // Start at random second

        const animate = (timestamp) => {
            const { mentalLoad, attention, disorientation, instability } = propsRef.current;

            // Throttle updates based on instability/disorientation to match original feel
            // Original: 30ms (instability), 80ms (disorientation), 150ms (base)
            const interval = instability ? 30 : (disorientation ? 80 : 150);

            if (timestamp - lastUpdate > interval) {
                lastUpdate = timestamp;

                // Logic from original component
                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;

                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25;
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                // Update styles directly
                if (glitchRef.current) {
                    const offset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);

                    let transform = `translateX(${offset}px)`;
                    let filter = '';
                    let opacity = active ? (0.5 + (mentalLoad / 200)) : 0.2;

                    // Critical failure style
                    if (mentalLoad > 90) {
                        filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        transform += ` scale(${1 + Math.random() * 0.05})`;
                    }

                    glitchRef.current.style.transform = transform;
                    glitchRef.current.style.filter = filter;
                    glitchRef.current.style.opacity = opacity;
                }

                if (noiseRef.current) {
                    const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                    noiseRef.current.style.opacity = noiseOpacity;
                }

                if (trackingBarRef.current) {
                    const trackingPos = (Math.random() * attentionFactor * 10);
                    trackingBarRef.current.style.top = `${10 + trackingPos}%`;
                }
            }

            // Update counter every ~60 frames (approx 1 sec)
            frames++;
            if (frames % 60 === 0) {
                seconds = (seconds + 1) % 60;
                if (counterRef.current) {
                    counterRef.current.innerText = `SP 0:00:${seconds.toString().padStart(2, '0')}`;
                }
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        animate(0);

        return () => cancelAnimationFrame(animationFrameId);
    }, [active]); // Re-start if active changes (though logic handles it mostly)

    return (
        <div className={`vhs-container active ${instability ? 'instability-panic' : ''}`}>
            <div className="scanlines"></div>
            <div ref={noiseRef} className="static-noise" style={{ opacity: 0.1 }}></div>
            <div ref={trackingBarRef} className="tracking-bar" style={{ top: '10%' }}></div>
            <div ref={glitchRef} className="glitch-overlay"
                style={{
                    transform: 'translateX(0px)',
                    opacity: active ? 0.5 : 0.2
                }}>
            </div>

            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                {/* Initial render is stable "00" to prevent hydration mismatch */}
                <span ref={counterRef} className="tape-counter">SP 0:00:00</span>
            </div>
        </div>
    );
};

export default VHSEffect;
