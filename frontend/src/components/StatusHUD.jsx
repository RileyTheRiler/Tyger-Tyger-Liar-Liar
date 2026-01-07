import React, { useEffect, useState } from 'react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import SubliminalText from './SubliminalText';
import './StatusHUD.css';

const StatusHUD = ({ uiState }) => {
    if (!uiState) return null;

    const { sanity, reality, location, time, day } = uiState;

    // Derived state for warnings
    const lowSanity = sanity < 30;
    const breakReality = reality < 30;

    return (
        <div className="hud-container">
            <div className="hud-header">
                <span className="hud-title">
                    <SubliminalText text="BIO_MONITOR_v9" sanity={sanity} />
                </span>
                <span className="hud-status blink">
                    ACTIVE
                </span>
            </div>

            <div className="hud-section stats-grid">
                <AnalogGauge
                    label="SANITY"
                    value={sanity}
                    color="var(--sanity-stable)"
                    criticalColor="var(--sanity-low)"
                />
                <AnalogGauge
                    label="REALITY"
                    value={reality}
                    color="var(--reality-anchor)"
                    criticalColor="var(--reality-break)"
                />
            </div>

            <div className="hud-section meta-info">
                <div className="meta-row">
                    <span className="meta-label">CASE ID:</span>
                    <span className="meta-value">88X-X-R</span>
                </div>
                <div className="meta-row">
                    <span className="meta-label">LOC:</span>
                    <span className="meta-value">{location?.toUpperCase() || "UNKNOWN"}</span>
                </div>
                <div className="meta-row">
                    <span className="meta-label">DATE:</span>
                    <span className="meta-value">OCT {day || "14"}</span>
                </div>
                <div className="meta-row">
                    <span className="meta-label">TIME:</span>
                    <span className="meta-value">{time || "06:00"}</span>
                </div>
            </div>

            <AnimatePresence>
                {(lowSanity || breakReality) && (
                    <Motion.div
                        className="hud-warning-box"
                        role="alert"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                    >
                        {lowSanity && <div className="warning-text">CRITICAL STRESS</div>}
                        {breakReality && <div className="warning-text">REALITY FRACTURE</div>}
                    </Motion.div>
                )}
            </AnimatePresence>

            {/* Decorative footer */}
            <div className="hud-footer">
                <div className="scan-line-decoration"></div>
                <span className="id-tag">REF: 893-K-X</span>
            </div>
        </div>
    );
};

// The new Analog Gauge Component
const AnalogGauge = ({ label, value, color, criticalColor }) => {
    // Map 0-100 to rotation degrees. 
    // Say -45deg is 0, +45deg is 100. Range = 90deg.
    const rotation = -45 + (value / 100) * 90;

    // Jitter the needle slightly based on value (lower = more jitter)
    const [jitter, setJitter] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            // More jitter if value is low (stress/instability)
            const stressFactor = Math.max(0, (50 - value) / 50);
            if (stressFactor > 0) {
                setJitter((Math.random() - 0.5) * (stressFactor * 5));
            } else {
                setJitter(0);
            }
        }, 100);
        return () => clearInterval(interval);
    }, [value]);

    return (
        <div
            className="stat-unit"
            role="progressbar"
            aria-valuenow={value}
            aria-valuemin="0"
            aria-valuemax="100"
            aria-label={`${label} Level`}
        >
            <div className="gauge-display">
                <div className="gauge-ticks" />
                <div
                    className="gauge-needle"
                    style={{
                        transform: `rotate(${rotation + jitter}deg)`,
                        backgroundColor: value < 30 ? criticalColor : color
                    }}
                />
            </div>
            <div className="stat-header">
                <span className="stat-label" aria-hidden="true">{label}</span>
                {/* Optional digital readout below */}
                {/* <span className="stat-value">{value}%</span> */}
            </div>
        </div>
    );
};

export default StatusHUD;
