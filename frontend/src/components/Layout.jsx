import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Layout.css';

const Layout = ({ children, uiState }) => {
    // Extract psych stats safely, defaulting if missing
    const sanity = uiState?.sanity ?? 100;
    const reality = uiState?.reality ?? 100;

    // Calculate intensity of effects based on Sanity (lower = higher intensity)
    // Sanity 100 -> 0 intensity
    // Sanity 0 -> 1 intensity
    const panicLevel = Math.max(0, (100 - sanity) / 100);

    // Reality distortion (lower reality = more chromatic aberration/glitching)
    const glitchLevel = Math.max(0, (100 - reality) / 100);

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
                        key={history.length} // Subtle re-triggering or just standard transition
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
