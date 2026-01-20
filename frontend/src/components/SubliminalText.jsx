import React, { useEffect, useState } from 'react';

// A component that occasionally swaps its text to a "corrupted" version
// based on the current Sanity level.
const SubliminalText = ({ text, sanity = 100, className = '' }) => {
    const [glitchedText, setGlitchedText] = useState(null);

    // Derived state for glitch probability
    const panic = Math.max(0, 100 - sanity);
    const isUnstable = panic > 40; // Starts glitching below 60 sanity

    useEffect(() => {
        if (!isUnstable) {
            // Reset state if we become stable.
            // Using setTimeout to avoid synchronous setState warning.
            const t = setTimeout(() => setGlitchedText(null), 0);
            return () => clearTimeout(t);
        }

        const CORRUPTIONS = [
            "WAKE UP", "LIAR", "THEY KNOW", "RUN", "FALSE",
            "LOOK BEHIND", "NULL", "ERROR", "VOID", "NO SIGNAL"
        ];

        const triggerGlitch = () => {
            // Probability check: higher panic = higher chance
            if (Math.random() < (panic / 200)) { // 0.2 to 0.5 chance roughly
                const word = CORRUPTIONS[Math.floor(Math.random() * CORRUPTIONS.length)];
                setGlitchedText(word);

                // Revert back quickly
                setTimeout(() => {
                    setGlitchedText(null);
                }, 100 + Math.random() * 200);
            }
        };

        const intervalId = setInterval(triggerGlitch, 2000); // Check every 2s

        return () => clearInterval(intervalId);
    }, [sanity, isUnstable, panic]);

    // If unstable, show glitch text if present, else show normal text.
    // If stable, always show normal text (even if glitch text is lingering before reset)
    const display = (isUnstable && glitchedText) || text;

    return (
        <span
            className={className}
            style={{ position: 'relative', display: 'inline-block' }}
            aria-label={text}
        >
            <span aria-hidden="true">{display}</span>
        </span>
    );
};

export default SubliminalText;
