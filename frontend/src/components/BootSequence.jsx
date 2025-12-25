import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GlitchText from './GlitchText';
import './BootSequence.css';

const maxLines = 15;

const randomHex = () => Math.floor(Math.random() * 16777215).toString(16);
const systemMessages = [
    "CONNECTING TO LIMBIC SYSTEM...",
    "BYPASSING AMYGDALA FIREWALL...",
    "SYNAPTIC HANDSHAKE: FAILED",
    "RETRYING...",
    "SYNAPTIC HANDSHAKE: ACCEPTED",
    "INJECTING MEMETIC PAYLOAD...",
    "WARNING: CORE INSTABILITY DETECTED",
    "REALITY ANCHOR: DRIFTING",
    "LOADING: TYGER_PROTOCOL_V0.9",
    "SUBJECT: [REDACTED]",
    "VITAL SIGNS: ELEVATED",
    "ESTABLISHING NEURAL LINK..."
];

const BootSequence = ({ onComplete }) => {
    const [lines, setLines] = useState([]);
    const [flash, setFlash] = useState(false);
    const [finished, setFinished] = useState(false);

    useEffect(() => {
        let lineInterval;
        let counter = 0;

        // Rapid stream of data
        lineInterval = setInterval(() => {
            counter++;
            const msg = Math.random() > 0.7
                ? systemMessages[Math.floor(Math.random() * systemMessages.length)]
                : `0x${randomHex()} :: ${Math.random().toFixed(4)}`;

            setLines(prev => {
                const nav = [...prev, msg];
                if (nav.length > maxLines) nav.shift();
                return nav;
            });

            if (counter === 15) setFlash(true);
            if (counter === 16) setFlash(false);

            if (counter > 30) {
                clearInterval(lineInterval);
                setFinished(true);
                setTimeout(onComplete, 2000); // Hold the WAKE UP screen
            }
        }, 80);

        return () => clearInterval(lineInterval);
    }, [onComplete]);

    return (
        <div className={`boot-container ${flash ? 'flash-red' : ''}`}>
            {!finished ? (
                <div className="boot-stream">
                    {lines.map((line, i) => (
                        <div key={i} className="boot-line">{line}</div>
                    ))}
                </div>
            ) : (
                <motion.div
                    className="wake-up-msg"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1.2, opacity: 1 }}
                    transition={{ duration: 0.1, yoyo: Infinity }}
                >
                    <GlitchText text="WAKE UP" />
                </motion.div>
            )}

            <div className="scan-line-overlay"></div>
        </div>
    );
};

export default BootSequence;
