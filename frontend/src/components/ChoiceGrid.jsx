import React from 'react';
import { motion } from 'framer-motion';
import './ChoiceGrid.css';

const ChoiceGrid = ({ choices, handleChoice, loading }) => {
    if (!choices || choices.length === 0) return null;

    return (
        <div className="choice-grid-container">
            {choices.map((choice, index) => (
                <ChoiceButton
                    key={index}
                    choice={choice}
                    index={index}
                    onClick={() => handleChoice(choice.id)}
                    disabled={loading}
                />
            ))}
        </div>
    );
};

const ChoiceButton = ({ choice, index, onClick, disabled }) => {
    return (
        <motion.button
            className="choice-btn"
            onClick={onClick}
            disabled={disabled}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
                duration: 0.4,
                delay: index * 0.1, // Cascade effect
                type: "spring",
                stiffness: 100
            }}
            whileHover={{
                scale: 1.02,
                backgroundColor: "rgba(255, 159, 28, 0.1)", // Generic orange tint
                borderColor: "var(--tyger-orange)",
                textShadow: "0 0 8px var(--tyger-orange)"
            }}
            whileTap={{ scale: 0.98 }}
        >
            <span className="choice-index">0{index + 1}</span>
            <span className="choice-text">{choice.text}</span>
            {/* Optional decorative corner */}
            <div className="corner-decor" />
        </motion.button>
    );
};

export default ChoiceGrid;
