import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import './MindMap.css';

const MindMap = ({ boardData, onClose }) => {
    // Simple pseudo-random function for deterministic positioning
    const pseudoRandom = (seed) => {
        const x = Math.sin(seed) * 10000;
        return x - Math.floor(x);
    };

    // Simple force-directed-like positioning (pseudo-random but deterministic based on ID)
    // In a real app we'd use d3-force, but for 5-10 nodes, static + random jitter is fine
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

            // Simple deterministic position based on char codes of ID if we wanted, 
            // but index-based circle is cleaner for now.
            // Using i + 1 to avoid sin(0) issues if relevant, though 0 is fine
            const jitterX = (pseudoRandom(i * 123) * 50) - 25;
            const jitterY = (pseudoRandom(i * 321) * 50) - 25;

            return {
                ...node,
                x: width / 2 + Math.cos(angle) * radius + jitterX,
                y: height / 2 + Math.sin(angle) * radius + jitterY
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
                            <motion.line
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
                            <motion.circle
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
                            <motion.text
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
                            </motion.text>

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
