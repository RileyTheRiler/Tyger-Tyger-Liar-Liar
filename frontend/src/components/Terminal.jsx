import React, { useEffect, useRef, memo } from 'react';
import { motion } from 'framer-motion';
import './Terminal.css';

// Alias motion to PascalCase to satisfy ESLint no-unused-vars rule
const Motion = motion;

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

// Memoized to prevent re-rendering previous entries when history updates
const TerminalEntry = memo(({ entry }) => {
    const isInput = entry.type === 'input';

    // Split text by newlines to handle multi-line outputs (for staggered animation)
    const lines = entry.text.split('\n');

    return (
        <div className={`term-entry ${isInput ? 'term-input' : 'term-output'}`}>
            {lines.map((line, i) => (
                <Motion.div
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
                </Motion.div>
            ))}
        </div>
    );
});

// Helper to escape HTML characters to prevent XSS
const escapeHtml = (unsafe) => {
    if (!unsafe) return "";
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
};

// Simple formatter for bold/color (can be expanded)
const formatLine = (text) => {
    if (!text) return "";

    // Security: Escape HTML first!
    let formatted = escapeHtml(text);

    // 1. Handle Skill Checks: [PATTERN RECOGNITION] -> <span class="skill-check">...</span>
    // Regex matching [WORDS] at the start or distinctively
    formatted = formatted.replace(
        /\[([A-Z\s]+)\]/g,
        '<span class="skill-check">[$1]</span>'
    );

    // 2. Handle Markdown bold **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // 3. Handle specific system text if needed (e.g. EVIDENCE ADDED)
    formatted = formatted.replace(
        /(EVIDENCE ADDED|ITEM GAINED)/g,
        '<span class="system-text">$1</span>'
    );

    return formatted;
};

export default Terminal;
