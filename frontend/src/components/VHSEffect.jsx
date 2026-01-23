import React, { useEffect, useRef } from 'react';
import './VHSEffect.css';

const VHSEffect = ({ active, mentalLoad = 0, attention = 0, disorientation = false, instability = false }) => {
    const noiseRef = useRef(null);
    const trackingRef = useRef(null);
    const glitchRef = useRef(null);
    const counterRef = useRef(null);
    const containerRef = useRef(null);

    // Store props in ref to access inside requestAnimationFrame loop
    const propsRef = useRef({ active, mentalLoad, attention, disorientation, instability });

    useEffect(() => {
        propsRef.current = { active, mentalLoad, attention, disorientation, instability };

        // Update container class when instability changes to avoid full re-render if possible,
        // but class updates usually trigger re-render anyway unless done via ref.
        // For simplicity, we can leave className logic in render if it changes rarely,
        // or manipulate classList manually.
        if (containerRef.current) {
            if (instability) {
                containerRef.current.classList.add('instability-panic');
            } else {
                containerRef.current.classList.remove('instability-panic');
            }
        }
    }, [active, mentalLoad, attention, disorientation, instability]);

    useEffect(() => {
        let animationFrameId;
        let lastTime = 0;

        const animate = (time) => {
            const { active, mentalLoad, attention, disorientation, instability } = propsRef.current;

            // Effect increases frequency with stress
            const baseInterval = instability ? 30 : (disorientation ? 80 : 150);

            if (time - lastTime > baseInterval) {
                lastTime = time;

                const loadFactor = mentalLoad / 100.0;
                const attentionFactor = (attention || 0) / 100.0;

                const stressNoise = loadFactor * 0.6;
                const attentionGlitch = attentionFactor * 25;
                const majorGlitch = Math.random() < (loadFactor * 0.1) ? 50 : 0;

                const glitchOffset = (Math.random() * (5 + attentionGlitch + majorGlitch)) - (2.5 + attentionGlitch / 2);
                const noiseOpacity = 0.05 + stressNoise + (Math.random() * 0.1);
                const trackingPos = (Math.random() * attentionFactor * 10);

                // Update DOM directly
                if (noiseRef.current) {
                    noiseRef.current.style.opacity = noiseOpacity.toFixed(3);
                }

                if (trackingRef.current) {
                    trackingRef.current.style.top = `${10 + trackingPos}%`;
                }

                if (glitchRef.current) {
                    const el = glitchRef.current;
                    el.style.transform = `translateX(${glitchOffset.toFixed(1)}px)`;
                    el.style.opacity = active ? (0.5 + (mentalLoad / 200)).toFixed(3) : '0.2';

                    if (mentalLoad > 90) {
                        el.style.filter = 'grayscale(1) contrast(1.5) brightness(0.8)';
                        // Add scale jitter
                        const scale = 1 + Math.random() * 0.05;
                        el.style.transform += ` scale(${scale.toFixed(3)})`;
                    } else {
                         el.style.filter = '';
                    }
                }

                if (counterRef.current) {
                     // Update random counter occasionally or every frame
                     // Previous behavior: every render.
                     const randomSec = Math.floor(Math.random() * 60).toString().padStart(2, '0');
                     counterRef.current.textContent = `SP 0:00:${randomSec}`;
                }
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrameId);
    }, []); // Run loop once

    return (
        <div
            ref={containerRef}
            className={`vhs-container active`}
        >
            <div className="scanlines"></div>
            <div ref={noiseRef} className="static-noise"></div>
            <div ref={trackingRef} className="tracking-bar"></div>
            <div ref={glitchRef} className="glitch-overlay"></div>

            <div className="vhs-osd">
                <span className="play-text">{disorientation ? "ERR: LOSS" : "PLAY"}</span>
                <span ref={counterRef} className="tape-counter">SP 0:00:00</span>
            </div>
        </div>
    );
};

export default VHSEffect;
