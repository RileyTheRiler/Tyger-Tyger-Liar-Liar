import React, { useEffect, useRef } from 'react';

// Defined outside component to avoid recreation on every render
// and to satisfy React Hook rules about class declarations inside hooks
class Particle {
    constructor(canvasWidth, canvasHeight) {
        this.canvasWidth = canvasWidth;
        this.canvasHeight = canvasHeight;
        this.reset();
    }

    reset() {
        this.x = Math.random() * this.canvasWidth;
        this.y = Math.random() * this.canvasHeight;
        this.size = Math.random() * 2;
        this.speedY = Math.random() * 0.5 + 0.1;
        this.speedX = (Math.random() - 0.5) * 0.2;
        this.opacity = Math.random() * 0.5;
        this.color = Math.random() > 0.8 ? '#ff9f1c' : '#7209b7'; // Orange or Purple
    }

    update() {
        this.y -= this.speedY; // Float up
        this.x += this.speedX;

        if (this.y < 0) {
            this.y = this.canvasHeight;
            this.x = Math.random() * this.canvasWidth;
        }
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

const ParticleCanvas = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let animationFrameId;

        // Use refs for particles to persist across potential re-runs of effect
        // (though effect only runs once due to [])
        let particles = [];
        const particleCount = 50;

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            // Re-initialize particles on resize if needed, or just update bounds
            // For simplicity, we just let them wrap based on new bounds in next update
        };

        window.addEventListener('resize', resize);
        resize();

        // Initialize particles
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle(canvas.width, canvas.height));
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                // Update bounds check in case of resize
                p.canvasWidth = canvas.width;
                p.canvasHeight = canvas.height;

                p.update();
                p.draw(ctx);
            });
            animationFrameId = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener('resize', resize);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                pointerEvents: 'none',
                zIndex: 1 // Behind content (2), above background (0)
            }}
        />
    );
};

export default ParticleCanvas;
