import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import VHSEffect from './VHSEffect';
import Datamosh from './Datamosh';
import './Layout.css';
import './CRTEffect.css';

const Layout = ({ children, uiState }) => {
    // Extract psych stats safely, defaulting if missing
    const sanity = uiState?.sanity ?? 100;
    const reality = uiState?.reality ?? 100;

    // Calculate intensity of effects based on Sanity (lower = higher intensity)
    // Sanity 100 -> 0 intensity
    // Sanity 0 -> 1 intensity
    // Calculate intensity of effects based on Sanity (lower = higher intensity)
    // Sanity 100 -> 0 intensity
    // Sanity 0 -> 1 intensity
    const panicLevel = Math.max(0, (100 - sanity) / 100);

    // Heartbeat for Pulse Effect (High Panic / Low Sanity)
    const [pulse, setPulse] = useState(1);
    useEffect(() => {
        if (panicLevel > 0.6) { // Active only when stressed
            const interval = setInterval(() => {
                setPulse(prev => (prev === 1 ? 1.02 : 1));
            }, 800 - (panicLevel * 400)); // Faster heartbeat with more panic
            return () => clearInterval(interval);
        } else {
            setPulse(1);
        }
    }, [panicLevel]);

    // Reality distortion (lower reality = more chromatic aberration/glitching)
    const glitchLevel = Math.max(0, (100 - reality) / 100);

    // VHS Transition Logic
    const [isTransitioning, setIsTransitioning] = useState(false);
    const prevLocation = useRef(uiState?.location);
    const prevSceneId = useRef(uiState?.scene_id);

    useEffect(() => {
        const currentLocation = uiState?.location;
        const currentSceneId = uiState?.scene_id; // Assuming backend might send this

        // Trigger if location changes or scene_id changes (if available)
        // We use a comprehensive check to avoid triggering on initial load if we don't want to,
        // but typically initial load might be nice to have a glitch too.
        // For now, let's trigger on change.
        const hasLocationChanged = prevLocation.current !== currentLocation;
        const hasSceneChanged = currentSceneId && prevSceneId.current !== currentSceneId;

        if (hasLocationChanged || hasSceneChanged) {
            setIsTransitioning(true);
            const timer = setTimeout(() => setIsTransitioning(false), 800); // 800ms duration
            return () => clearTimeout(timer);
        }

        prevLocation.current = currentLocation;
        prevSceneId.current = currentSceneId;
    }, [uiState?.location, uiState?.scene_id]);


    return (
        <div className="layout-container">
            {/* Dynamic Background */}
            <BackgroundDistortion panicLevel={panicLevel} glitchLevel={glitchLevel} />

            {/* Sanity Vignette Overlay */}
            <div
                className="vignette-overlay"
                style={{
                    boxShadow: `inset 0 0 ${100 + (panicLevel * 200)}px rgba(0,0,0,${0.6 + (panicLevel * 0.4)})`,
                    background: `radial-gradient(circle, transparent 60%, rgba(${20 * panicLevel},0,0,${0.2 * panicLevel}) 90%)`
                }}
            />

            {/* Main Content Area */}
            <main className="content-frame">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={uiState?.location || 'init'} // Key logic for transition
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -5 }}
                        transition={{ duration: 0.3 }}
                        className="content-inner"
                    >
                        {children}
                    </motion.div>
                </AnimatePresence>
            </main>

            {/* VHS Overlay Effect */}
            <VHSEffect active={isTransitioning} />

            {/* Datamosh Effect (Triggers on extreme low reality or specific flags) */}
            <Datamosh active={reality < 15} />

            {/* CRT Monitor Effects */}
            <div className="crt-container" style={{ transform: `scale(${pulse})` }}>
                <div className="crt-overlay" />
                <div className="crt-mesh" />
                <div className="crt-flicker" />
                <div className="crt-bezel" />
            </div>

            {/* Optional: Add scanline overlay here if not in body */}
            <div className="scanlines" />
        </div>
    );
};

// Internal Component for the background effects
const BackgroundDistortion = ({ panicLevel, glitchLevel }) => {
    return (
        <div className="background-distortion">
            {/* Base Gradient Layer - Shifts based on panic */}
            <motion.div
                className="bg-gradient-base"
                animate={{
                    background: `linear-gradient(${135 + (panicLevel * 45)}deg, #020202 0%, #08080a 50%, #0a0a0f 100%)`
                }}
                transition={{ duration: 2 }}
            />

            {/* Pulse Layer - Red glow fades in at high panic */}
            <motion.div
                className="bg-pulse-red"
                animate={{
                    opacity: panicLevel * 0.5,
                    scale: [1, 1.05, 1]
                }}
                transition={{
                    duration: 4 / (Math.max(0.1, panicLevel)), // Faster pulse when panic is high
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
            />

            {/* Glitch/Reality Layer - Purple tones */}
            <div
                className="bg-glitch-layer"
                style={{
                    opacity: glitchLevel * 0.4,
                    filter: `hue-rotate(${glitchLevel * 90}deg) blur(${glitchLevel * 4}px)`
                }}
            />
        </div>
    );
};

export default Layout;
