import React, { useRef, useEffect, useState } from 'react';
import './InputConsole.css';

const InputConsole = ({ input, setInput, handleSend, loading }) => {
    const inputRef = useRef(null);
    const [history, setHistory] = useState([]);
    const [historyIndex, setHistoryIndex] = useState(-1);

    useEffect(() => {
        // Keep focus unless selecting text elsewhere
        const focusInterval = setInterval(() => {
            if (document.activeElement !== inputRef.current && !window.getSelection().toString()) {
                inputRef.current?.focus();
            }
        }, 100);
        return () => clearInterval(focusInterval);
    }, []);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !loading) {
            if (input.trim()) {
                setHistory(prev => [...prev, input]);
                setHistoryIndex(-1);
            }
            handleSend(input);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (history.length > 0) {
                const newIndex = historyIndex === -1 ? history.length - 1 : Math.max(0, historyIndex - 1);
                setHistoryIndex(newIndex);
                setInput(history[newIndex]);
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex !== -1) {
                const newIndex = Math.min(history.length - 1, historyIndex + 1);
                if (historyIndex === history.length - 1) {
                    setHistoryIndex(-1);
                    setInput("");
                } else {
                    setHistoryIndex(newIndex);
                    setInput(history[newIndex]);
                }
            }
        }
    }

    return (
        <div className="input-console">
            <div className="prompt-decoration">{(historyIndex !== -1 ? ":" : ">")}</div>
            <input
                ref={inputRef}
                type="text"
                className="terminal-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={loading ? "SYSTEM_BUSY..." : "AWAITING_INPUT..."}
                aria-label={loading ? "System busy, please wait" : "Command input"}
                disabled={loading}
                spellCheck="false"
                autoComplete="off"
                aria-label="Command input"
            />
            <div className={`cursor-block ${loading ? 'busy' : ''}`}></div>
        </div>
    );
};

export default InputConsole;
