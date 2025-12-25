class AudioSystem {
    constructor() {
        this.ctx = null;
    }

    init() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContext();
        }
    }

    playTone(freq, type, duration) {
        // Initialize on first play if not already (though browser requires user gesture typically)
        // We will try to init on interaction in the main script.
        if (!this.ctx) return;

        if (this.ctx.state === 'suspended') {
            // Can't resume here without user gesture usually, but we try.
            this.ctx.resume().catch(e => console.log(e));
        }

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

        gain.gain.setValueAtTime(0.05, this.ctx.currentTime); // Low volume
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + duration);
    }

    playHover() {
        this.playTone(800, 'square', 0.05);
    }

    playSelect() {
        this.playTone(400, 'square', 0.1);
        setTimeout(() => this.playTone(600, 'square', 0.2), 100);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const mainMenuItems = document.querySelectorAll('.main-menu li');
    const crtMenuItems = document.querySelectorAll('.crt-menu li');
    let currentIndex = 0;
    let interactionEnabled = false;
    const audio = new AudioSystem();

    // Hide items initially
    mainMenuItems.forEach(item => item.style.visibility = 'hidden');
    crtMenuItems.forEach(item => item.style.visibility = 'hidden');

    async function runIntro() {
        // Simple delay before starting
        await new Promise(r => setTimeout(r, 500));

        for (let i = 0; i < mainMenuItems.length; i++) {
            mainMenuItems[i].style.visibility = 'visible';
            crtMenuItems[i].style.visibility = 'visible';

            // Random typing delay
            await new Promise(r => setTimeout(r, 200 + Math.random() * 200));
        }

        interactionEnabled = true;
        // Select first item visually
        updateSelection(0);
    }

    function updateSelection(index) {
        if (!interactionEnabled) return;

        // Wrap index
        if (index < 0) index = mainMenuItems.length - 1;
        if (index >= mainMenuItems.length) index = 0;

        currentIndex = index;

        // Update classes
        mainMenuItems.forEach((item, i) => {
            if (i === currentIndex) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Sync CRT menu
        crtMenuItems.forEach((item, i) => {
            if (i === currentIndex) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        // Initialize audio on first keydown
        if (!audio.ctx) audio.init();
        if (audio.ctx && audio.ctx.state === 'suspended') audio.ctx.resume();

        if (!interactionEnabled) return;

        if (e.key === 'ArrowUp' || e.key === 'w') {
            audio.playHover();
            updateSelection(currentIndex - 1);
        } else if (e.key === 'ArrowDown' || e.key === 's') {
            audio.playHover();
            updateSelection(currentIndex + 1);
        } else if (e.key === 'Enter' || e.key === ' ') {
            audio.playSelect();
            triggerAction(currentIndex);
        }
    });

    // Mouse support
    mainMenuItems.forEach((item, i) => {
        item.addEventListener('mouseenter', () => {
             // Init audio on mouse interaction too
             if (!audio.ctx) audio.init();
             if (audio.ctx && audio.ctx.state === 'suspended') audio.ctx.resume();

            if (interactionEnabled) {
                if (currentIndex !== i) {
                     audio.playHover();
                     updateSelection(i);
                }
            }
        });
        item.addEventListener('click', () => {
             if (!audio.ctx) audio.init();
             if (audio.ctx && audio.ctx.state === 'suspended') audio.ctx.resume();

            if (interactionEnabled) {
                audio.playSelect();
                triggerAction(i);
            }
        });
    });

    function triggerAction(index) {
        const action = mainMenuItems[index].textContent.trim();
        console.log(`Action triggered: ${action}`);
    }

    // Start intro
    runIntro();
});
