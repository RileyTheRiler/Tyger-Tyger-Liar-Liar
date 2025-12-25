import React, { useState, useEffect, useMemo } from 'react';
import { parseRichText } from '../utils/textParser';
import './Typewriter.css';

const Typewriter = ({ text, speed = 10, onComplete }) => {
    // 1. Parse text into tokens ONCE
    const tokens = useMemo(() => parseRichText(text), [text]);

    // 2. We need to track how many characters of the *plain text content* have been revealed.
    const fullPlainText = tokens.map(t => t.text).join('');
    const [charIndex, setCharIndex] = useState(0);

    useEffect(() => {
        if (charIndex < fullPlainText.length) {
            const timeout = setTimeout(() => {
                setCharIndex(prev => prev + 1);
            }, speed);
            return () => clearTimeout(timeout);
        } else {
            if (onComplete) onComplete();
        }
    }, [charIndex, fullPlainText, speed, onComplete]);

    // 3. Render logic: reconstruction
    // We iterate through tokens. If token fits fully inside charIndex, render it total.
    // If token is partially inside charIndex, render partial.
    // If token is outside, stop.

    let charsConsumed = 0;

    return (
        <span className="typewriter-container">
            {tokens.map((token, i) => {
                if (charsConsumed >= charIndex) return null; // Not reached yet

                const charsNeeded = token.text.length;
                const charsAvailable = charIndex - charsConsumed;

                let textToDisplay = token.text;
                if (charsAvailable < charsNeeded) {
                    textToDisplay = token.text.slice(0, charsAvailable);
                }

                charsConsumed += charsNeeded;

                // Render span with style
                return (
                    <span key={i} className={`rt-${token.style}`}>
                        {textToDisplay}
                    </span>
                );
            })}
            <span className="cursor-block"></span>
        </span>
    );
};

export default Typewriter;
