import React, { useMemo } from 'react';
import { motion as Motion } from 'framer-motion';
import './MindMap.css';

// Simple hash function to generate a stable number between 0 and 1 based on a string seed
// This replaces Math.random() to ensure node positions are deterministic and stable across renders
const stableRandom = (seed) => {
    let hash = 0;
    for (let i = 0; i < seed.length; i++) {
        const char = seed.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    // Normalize to 0-1
    return (Math.abs(hash) % 10000) / 10000;
};

const MindMap = ({ boardData, onClose }) => {
    const { nodes, links } = useMemo(() => {
        if (!boardData || !boardData.nodes || boardData.nodes.length === 0) {
            return { nodes: [], links: [] };
        }

        const width = 800; // Virtual canvas width
        const height = 600;

        // Position theories in center-ish
        // Position evidence in orbit

        const processedNodes = boardData.nodes.map((node, i) => {
            const isTheory = node.type === 'theory';
            const angle = (i / boardData.nodes.length) * Math.PI * 2;
            const radius = isTheory ? 100 : 250;

            // Deterministic jitter based on node ID
            const r1 = stableRandom(node.id + '_x');
            const r2 = stableRandom(node.id + '_y');

            return {
                ...node,
                x: width / 2 + Math.cos(angle) * radius + (r1 * 50 - 25),
                y: height / 2 + Math.sin(angle) * radius + (r2 * 50 - 25)
            };
        });

        return { nodes: processedNodes, links: boardData.links };
    }, [boardData]);

    if (!boardData || !boardData.nodes || boardData.nodes.length === 0) {
        return (
            <div className="mindmap-overlay empty" onClick={onClose}>
                <div className="empty-message">NO ACTIVE THEORIES</div>
            </div>
        );
    }

    return (
        <div className="mindmap-overlay">
            <div className="mindmap-container">
                <h2 className="board-title">CASE_LOGIC_GRAPH</h2>
                <button className="close-btn" onClick={onClose}>[CLOSE]</button>

                <svg viewBox="0 0 800 600" className="mindmap-svg">
                    {/* Defs for markers */}
                    <defs>
                        <marker id="arrow" markerWidth="10" markerHeight="10" refX="20" refY="3" orient="auto" markerUnits="strokeWidth">
                            <path d="M0,0 L0,6 L9,3 z" fill="var(--danger-red)" />
                        </marker>
                    </defs>

                    {/* Links */}
                    {links.map((link, i) => {
                        const source = nodes.find(n => n.id === link.source);
                        const target = nodes.find(n => n.id === link.target);
                        if (!source || !target) return null;

                        return (
                            <Motion.line
                                key={i}
                                x1={source.x} y1={source.y}
                                x2={target.x} y2={target.y}
                                stroke={link.has_friction ? "var(--danger-red)" : "var(--text-dim)"}
                                strokeWidth={link.has_friction ? 4 : 2}
                                strokeDasharray={link.has_friction ? "0" : "5,5"}
                                initial={{ pathLength: 0, opacity: 0 }}
                                animate={{ pathLength: 1, opacity: 0.6 }}
                                transition={{ duration: 1, delay: 0.5 + (i * 0.1) }}
                                className={link.has_friction ? 'link-friction' : ''}
                            />
                        );
                    })}

                    {/* Nodes */}
                    {nodes.map((node, i) => (
                        <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
                            <Motion.circle
                                r={node.type === 'theory' ? 20 : 10}
                                fill={node.type === 'theory' ? "var(--bg-void)" : "var(--text-ghost)"}
                                stroke={node.type === 'theory' ? "var(--tyger-orange)" : "var(--text-dim)"}
                                strokeWidth={node.type === 'theory' ? 3 : 1}
                                initial={{ scale: 0 }}
                                animate={{
                                    scale: 1,
                                    x: node.is_strained ? [0, -1, 1, -1, 0] : 0,
                                    y: node.is_strained ? [0, 1, -1, 1, 0] : 0
                                }}
                                transition={{
                                    scale: { type: "spring", delay: i * 0.1 },
                                    x: { repeat: Infinity, duration: 0.2 },
                                    y: { repeat: Infinity, duration: 0.2 }
                                }}
                            />

                            {/* Label */}
                            <Motion.text
                                y={node.type === 'theory' ? 35 : 25}
                                textAnchor="middle"
                                fill="var(--text-primary)"
                                fontSize={node.type === 'theory' ? "14" : "10"}
                                fontFamily="var(--font-mono)"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 1 + (i * 0.1) }}
                                className={node.is_glitched ? 'node-glitch' : ''}
                            >
                                {node.label}
                            </Motion.text>

                            {/* Status Indicator for theories */}
                            {node.type === 'theory' && (
                                <text y="50" textAnchor="middle" fill={node.health < 50 ? "var(--danger-red)" : "var(--sanity-stable)"} fontSize="10">
                                    {node.status.toUpperCase()} ({Math.round(node.health)}%)
                                </text>
                            )}
                        </g>
                    ))}
                </svg>
            </div>
        </div>
    );
};

export default MindMap;
