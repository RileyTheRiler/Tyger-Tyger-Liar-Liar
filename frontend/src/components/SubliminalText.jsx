import React, { useEffect, useState } from 'react';

// A component that occasionally swaps its text to a "corrupted" version
// based on the current Sanity level.
const SubliminalText = ({ text, sanity = 100, className = '' }) => {
    const [display, setDisplay] = useState(text);

    // Derived state for glitch probability
    const panic = Math.max(0, 100 - sanity);
    const isUnstable = panic > 40; // Starts glitching below 60 sanity

    useEffect(() => {
        if (!isUnstable) {
            setDisplay(text);
            return;
        }

        const CORRUPTIONS = [
            "WAKE UP", "LIAR", "THEY KNOW", "RUN", "FALSE",
            "LOOK BEHIND", "NULL", "ERROR", "VOID", "NO SIGNAL"
        ];

        const triggerGlitch = () => {
            // Probability check: higher panic = higher chance
            if (Math.random() < (panic / 200)) { // 0.2 to 0.5 chance roughly
                const word = CORRUPTIONS[Math.floor(Math.random() * CORRUPTIONS.length)];
                setDisplay(word);

                // Revert back quickly
                setTimeout(() => {
                    setDisplay(text);
                }, 100 + Math.random() * 200);
            }
        };

        const intervalId = setInterval(triggerGlitch, 2000); // Check every 2s

        return () => clearInterval(intervalId);
    }, [text, sanity, isUnstable, panic]);

    return (
        <span className={className} style={{ position: 'relative', display: 'inline-block' }}>
            {display}
        </span>
    );
};

export default SubliminalText;
