import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import './Terminal.css';

const Terminal = ({ history }) => {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history]);

    return (
        <div className="terminal-window">
            <div className="terminal-content">
                {history.map((entry, index) => (
                    <TerminalEntry key={index} entry={entry} />
                ))}
                <div ref={bottomRef} />
            </div>
        </div>
    );
};

const TerminalEntry = ({ entry }) => {
    const isInput = entry.type === 'input';

    // Split text by newlines to handle multi-line outputs (for staggered animation)
    const lines = entry.text.split('\n');

    return (
        <div className={`term-entry ${isInput ? 'term-input' : 'term-output'}`}>
            {lines.map((line, i) => (
                <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{
                        duration: 0.3,
                        delay: i * 0.05, // Stagger effect
                        ease: "easeOut"
                    }}
                    className="term-line"
                >
                    {isInput && i === 0 && <span className="prompt-char">{">"}</span>}
                    {/* Basic markdown-like highlighting can go here if needed */}
                    <span dangerouslySetInnerHTML={{ __html: formatLine(line) }} />
                </motion.div>
            ))}
        </div>
    );
};

// Simple formatter for bold/color (can be expanded)
const formatLine = (text) => {
    // Replace **text** with bold
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Replace [COLOR]text[/COLOR] with color spans if backend sends them
    // Or handle specific keywords

    return formatted;
};

export default Terminal;
