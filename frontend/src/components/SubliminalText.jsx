import React, { useEffect, useState } from 'react';

// A component that occasionally swaps its text to a "corrupted" version
// based on the current Sanity level.
const SubliminalText = ({ text, sanity = 100, className = '' }) => {
    const [glitchWord, setGlitchWord] = useState(null);

    // Derived state for glitch probability
    const panic = Math.max(0, 100 - sanity);
    const isUnstable = panic > 40; // Starts glitching below 60 sanity

    useEffect(() => {
        if (!isUnstable) return;

        const CORRUPTIONS = [
            "WAKE UP", "LIAR", "THEY KNOW", "RUN", "FALSE",
            "LOOK BEHIND", "NULL", "ERROR", "VOID", "NO SIGNAL"
        ];

        const triggerGlitch = () => {
            // Probability check: higher panic = higher chance
            if (Math.random() < (panic / 200)) { // 0.2 to 0.5 chance roughly
                const word = CORRUPTIONS[Math.floor(Math.random() * CORRUPTIONS.length)];
                setGlitchWord(word);

                // Revert back quickly
                setTimeout(() => {
                    setGlitchWord(null);
                }, 100 + Math.random() * 200);
            }
        };

        const intervalId = setInterval(triggerGlitch, 2000); // Check every 2s

        return () => {
            clearInterval(intervalId);
            // Ensure we reset when stopping instability (e.g. sanity restored)
            setGlitchWord(null);
        };
    }, [isUnstable, panic]);

    // Use glitchWord if active, otherwise fallback to prop text
    const display = glitchWord || text;

    return (
        <span className={className} style={{ position: 'relative', display: 'inline-block' }}>
            {/* Stable text for screen readers so they don't hear glitch noise */}
            <span className="sr-only">{text}</span>
            {/* Visual text that may glitch, hidden from screen readers */}
            <span aria-hidden="true">{display}</span>
        </span>
    );
};

export default SubliminalText;
