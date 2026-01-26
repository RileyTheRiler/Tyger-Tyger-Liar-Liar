import React, { useEffect, useState } from 'react';

// A component that occasionally swaps its text to a "corrupted" version
// based on the current Sanity level.
const SubliminalText = ({ text, sanity = 100, className = '' }) => {
    // State only tracks the active corruption word, if any.
    // If null, we display the original text.
    const [corruption, setCorruption] = useState(null);

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
                setCorruption(word);

                // Revert back quickly
                setTimeout(() => {
                    setCorruption(null);
                }, 100 + Math.random() * 200);
            }
        };

        const intervalId = setInterval(triggerGlitch, 2000); // Check every 2s

        return () => {
            clearInterval(intervalId);
            setCorruption(null); // Ensure clean state when stabilizing or unmounting
        };
    }, [isUnstable, panic]);

    // Choose what to display: the corruption word or the stable text
    const display = corruption || text;

    return (
        <span className={className} style={{ position: 'relative', display: 'inline-block' }}>
            <span className="sr-only">{text}</span>
            <span aria-hidden="true">{display}</span>
        </span>
    );
};

export default SubliminalText;
