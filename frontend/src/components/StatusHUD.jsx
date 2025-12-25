import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
                <span className="hud-title">BIO_MONITOR</span>
                <span className="hud-status blink">ACTIVE</span>
            </div>

            <div className="hud-section stats-grid">
                <StatBar
                    label="SANITY"
                    value={sanity}
                    color="var(--sanity-stable)"
                    criticalColor="var(--sanity-low)"
                />
                <StatBar
                    label="REALITY"
                    value={reality}
                    color="var(--reality-anchor)"
                    criticalColor="var(--reality-break)"
                />
            </div>

            <div className="hud-divider" />

            <div className="hud-section meta-info">
                <div className="meta-row">
                    <span className="meta-label">LOC:</span>
                    <span className="meta-value">{location?.toUpperCase() || "UNKNOWN"}</span>
                </div>
                <div className="meta-row">
                    <span className="meta-label">DAY:</span>
                    <span className="meta-value">{day || "01"}</span>
                </div>
                <div className="meta-row">
                    <span className="meta-label">TIME:</span>
                    <span className="meta-value">{time || "00:00"}</span>
                </div>
            </div>

            <AnimatePresence>
                {(lowSanity || breakReality) && (
                    <motion.div
                        className="hud-warning-box"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                    >
                        {lowSanity && <div className="warning-text text-panic">CRITICAL STRESS</div>}
                        {breakReality && <div className="warning-text text-panic">REALITY FRACTURE</div>}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Decorative footer */}
            <div className="hud-footer">
                <div className="scan-line-decoration"></div>
                <span className="id-tag">ID: 893-K-X</span>
            </div>
        </div>
    );
};

const StatBar = ({ label, value, color, criticalColor }) => {
    const isCritical = value < 30;
    const barColor = isCritical ? criticalColor : color;

    return (
        <div className="stat-unit">
            <div className="stat-header">
                <span className="stat-label">{label}</span>
                <span className="stat-value" style={{ color: barColor }}>{value}%</span>
            </div>
            <div className="bar-track">
                <motion.div
                    className="bar-fill"
                    initial={{ width: 0 }}
                    animate={{
                        width: `${value}%`,
                        backgroundColor: barColor,
                        filter: isCritical ? [`drop-shadow(0 0 2px ${barColor})`, `drop-shadow(0 0 8px ${barColor})`] : "none"
                    }}
                    transition={{
                        width: { duration: 1, type: "spring" },
                        filter: { duration: 0.2, repeat: isCritical ? Infinity : 0, repeatType: "reverse" }
                    }}
                />
            </div>
        </div>
    );
};

export default StatusHUD;
