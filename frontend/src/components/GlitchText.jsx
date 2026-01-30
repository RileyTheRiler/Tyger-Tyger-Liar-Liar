import React from 'react';
import './GlitchText.css'; // We'll create this specific CSS

const GlitchText = ({ text, as = 'span', className = '' }) => {
    const Tag = as;
    return (
        <Tag className={`glitch-wrapper ${className}`} data-text={text} aria-label={text}>
            {text}
        </Tag>
    );
};

export default GlitchText;
