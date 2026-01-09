import React, { useEffect, useRef, memo } from 'react';
// eslint-disable-next-line no-unused-vars
import { motion } from 'framer-motion';
import './Terminal.css';

// Regex patterns defined outside to avoid recreation
const SKILL_CHECK_REGEX = /\[([A-Z\s]+)\]/g;
const BOLD_REGEX = /\*\*(.*?)\*\*/g;
const SYSTEM_TEXT_REGEX = /(EVIDENCE ADDED|ITEM GAINED)/g;

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

// ⚡ Bolt: Wrapped in React.memo to prevent re-rendering of existing entries
// when new history items are added. This changes rendering from O(N) to O(1).
const TerminalEntry = memo(({ entry }) => {
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
});

TerminalEntry.displayName = 'TerminalEntry';

// Simple formatter for bold/color (can be expanded)
const formatLine = (text) => {
    if (!text) return "";

    // 1. Handle Skill Checks: [PATTERN RECOGNITION] -> <span class="skill-check">...</span>
    let formatted = text.replace(
        SKILL_CHECK_REGEX,
        '<span class="skill-check">[$1]</span>'
    );

    // 2. Handle Markdown bold **text**
    formatted = formatted.replace(BOLD_REGEX, '<strong>$1</strong>');

    // 3. Handle specific system text if needed (e.g. EVIDENCE ADDED)
    formatted = formatted.replace(
        SYSTEM_TEXT_REGEX,
        '<span class="system-text">$1</span>'
    );

    return formatted;
};

export default Terminal;
