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

    // 3. Render logic using reduce to track offset without side effects
    const { elements } = tokens.reduce((acc, token, i) => {
        if (acc.currentOffset >= charIndex) return acc;

        const charsNeeded = token.text.length;
        const charsAvailable = charIndex - acc.currentOffset;

        let textToDisplay = token.text;
        if (charsAvailable < charsNeeded) {
            textToDisplay = token.text.slice(0, charsAvailable);
        }

        acc.elements.push(
            <span key={i} className={`rt-${token.style}`}>
                {textToDisplay}
            </span>
        );

        acc.currentOffset += charsNeeded;
        return acc;
    }, { elements: [], currentOffset: 0 });

    return (
        <span className="typewriter-container">
            {elements}
            <span className="cursor-block"></span>
        </span>
    );
};

export default Typewriter;
