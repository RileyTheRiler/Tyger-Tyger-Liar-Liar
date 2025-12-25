import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Layout.css';
import './CRTEffect.css'; // We might keep this for the sidebar specifically

const Layout = ({ children, sidebar, uiState }) => {
    const sanity = uiState?.sanity ?? 100;
    const panicLevel = Math.max(0, (100 - sanity) / 100);

    // Simple desk lamp flicker logic
    const [lampFlicker, setLampFlicker] = useState(1);
    useEffect(() => {
        if (Math.random() > 0.95) {
            // Occasional flicker
            const flicker = setInterval(() => {
                setLampFlicker(prev => (prev === 1 ? 0.95 : 1));
            }, 50);
            setTimeout(() => { clearInterval(flicker); setLampFlicker(1); }, 200);
        }
    }, [sanity]);

    return (
        <div className="layout-container">
            {/* The Main Narrative Paper Area */}
            <main className="main-content">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={uiState?.location || 'init'}
                        initial={{ opacity: 0, filter: 'blur(2px)' }}
                        animate={{ opacity: 1, filter: 'blur(0px)' }}
                        exit={{ opacity: 0, filter: 'blur(2px)' }}
                        transition={{ duration: 0.5 }}
                        className="content-inner"
                        style={{ opacity: lampFlicker }}
                    >
                        {children}
                    </motion.div>
                </AnimatePresence>
            </main>

            {/* The Device Sidebar Area */}
            <aside className="sidebar">
                {sidebar}
            </aside>

            {/* Atmospheric Overlays */}
            <div className="layout-overlay" />
            <div className="film-grain" />
        </div>
    );
};

export default Layout;

