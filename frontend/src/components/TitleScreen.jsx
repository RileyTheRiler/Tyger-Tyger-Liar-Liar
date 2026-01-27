import React from 'react';
import { motion } from 'framer-motion';
import GlitchText from './GlitchText';
import './TitleScreen.css';

// Alias motion to PascalCase to satisfy ESLint no-unused-vars rule
const Motion = motion;

const TitleScreen = ({ onStart, onExit }) => {
    return (
        <div className="title-screen">
            <div className="title-content">
                <Motion.div
                    initial={{ opacity: 0, y: -50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1, delay: 0.5 }}
                >
                    <GlitchText text="TYGER TYGER" className="title-main" />
                    <GlitchText text="LIAR LIAR" className="title-sub" />
                </Motion.div>

                <Motion.div
                    className="title-tagline"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.7 }}
                    transition={{ duration: 1, delay: 1.5 }}
                >
                    A PSYCHOLOGICAL HORROR MYSTERY
                </Motion.div>

                <Motion.div
                    className="title-menu"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5, delay: 2 }}
                >
                    <button className="title-btn start-btn" onClick={onStart} aria-label="Start Investigation">
                        [START_INVESTIGATION]
                    </button>
                    <button className="title-btn exit-btn" onClick={onExit} aria-label="Exit System">
                        [EXIT_SYSTEM]
                    </button>
                </Motion.div>

                <Motion.div
                    className="title-warning"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.5 }}
                    transition={{ duration: 1, delay: 2.5 }}
                >
                    WARNING: CONTAINS PSYCHOLOGICAL HORROR ELEMENTS
                </Motion.div>
            </div>

            <div className="scan-line-overlay"></div>
        </div>
    );
};

export default TitleScreen;
