
class AudioSystem {
    constructor() {
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.masterGain = this.ctx.createGain();
        this.masterGain.connect(this.ctx.destination);
        this.masterGain.gain.value = 0.3; // Low volume default
    }

    playHover() {
        if (this.ctx.state === 'suspended') this.ctx.resume();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, this.ctx.currentTime + 0.05);

        gain.gain.setValueAtTime(0.1, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.05);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.05);
    }

    playSelect() {
        if (this.ctx.state === 'suspended') this.ctx.resume();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'square';
        osc.frequency.setValueAtTime(220, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(55, this.ctx.currentTime + 0.3);

        gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.3);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start();
        osc.stop(this.ctx.currentTime + 0.3);
    }

    playIntroDrone() {
        if (this.ctx.state === 'suspended') this.ctx.resume();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(55, this.ctx.currentTime);

        gain.gain.setValueAtTime(0, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.05, this.ctx.currentTime + 2);
        gain.gain.linearRampToValueAtTime(0, this.ctx.currentTime + 6);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start();
        osc.stop(this.ctx.currentTime + 6);
    }
}

class TitleScreen {
    constructor() {
        this.audio = new AudioSystem();
        this.state = 'intro'; // intro, main_menu, transition, game

        // Elements
        this.titleOverlay = document.querySelector('.main-title-glitch');
        this.menuOverlay = document.querySelector('.main-menu');
        this.crtContainer = document.querySelector('.crt-screen-container');
        this.menuItems = document.querySelectorAll('.main-menu li');

        // CRT Elements
        this.crtContent = document.querySelector('.crt-inner-content');

        this.selectedIndex = 0;

        this.init();
    }

    init() {
        // Initial State
        this.titleOverlay.style.opacity = '0';
        this.menuOverlay.style.opacity = '0';
        this.crtContainer.style.opacity = '0';
        this.crtContainer.style.display = 'none'; // Hide initially

        // Setup Inputs
        document.addEventListener('keydown', (e) => this.handleInput(e));

        this.menuItems.forEach((item, index) => {
            item.addEventListener('mouseenter', () => {
                if (this.state === 'main_menu') {
                    this.selectedIndex = index;
                    this.updateSelection();
                    this.audio.playHover();
                }
            });
            item.addEventListener('click', () => {
                if (this.state === 'main_menu') {
                    this.selectItem();
                }
            });
        });

        // Start Sequence
        setTimeout(() => this.startIntro(), 500);
    }

    startIntro() {
        this.audio.playIntroDrone();

        // Phase 2: Title
        setTimeout(() => {
            this.titleOverlay.style.transition = 'opacity 2s ease-in';
            this.titleOverlay.style.opacity = '1';
        }, 1000);

        // Phase 3: Menu
        setTimeout(() => {
            this.state = 'main_menu';
            this.menuOverlay.style.transition = 'opacity 1s ease';
            this.menuOverlay.style.opacity = '1';
            this.updateSelection();
        }, 3500);
    }

    handleInput(e) {
        if (this.state !== 'main_menu') return;

        if (e.key === 'ArrowUp') {
            this.selectedIndex--;
            if (this.selectedIndex < 0) this.selectedIndex = this.menuItems.length - 1;
            this.updateSelection();
            this.audio.playHover();
        } else if (e.key === 'ArrowDown') {
            this.selectedIndex++;
            if (this.selectedIndex >= this.menuItems.length) this.selectedIndex = 0;
            this.updateSelection();
            this.audio.playHover();
        } else if (e.key === 'Enter') {
            this.selectItem();
        }
    }

    updateSelection() {
        this.menuItems.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.style.textDecoration = 'underline';
                item.style.color = '#fff';
            } else {
                item.style.textDecoration = 'none';
                item.style.color = 'var(--green-term)';
            }
        });
    }

    selectItem() {
        this.audio.playSelect();
        const text = this.menuItems[this.selectedIndex].innerText;

        if (text === 'NEW GAME') {
            this.transitionToCRT();
        } else {
            console.log('Selected:', text);
        }
    }

    transitionToCRT() {
        this.state = 'transition';

        // Fade out overlays
        this.titleOverlay.style.transition = 'opacity 1s ease';
        this.titleOverlay.style.opacity = '0';

        this.menuOverlay.style.transition = 'opacity 1s ease';
        this.menuOverlay.style.opacity = '0';

        // Show CRT and Zoom
        this.crtContainer.style.display = 'block';

        // Force reflow
        void this.crtContainer.offsetWidth;

        this.crtContainer.style.transition = 'opacity 2s ease, transform 2s ease-out';
        this.crtContainer.style.opacity = '1';
        this.crtContainer.style.transform = 'perspective(1000px) rotateX(0deg) scale(1.0)'; // Reset perspective to look like full screen or keep it styled?

        // Let's actually keep the monitor look but center it better or just fade it in
        // The CSS has it at rotateX(2deg) and scaled.
        // If we want to "Enter" the monitor, we should scale it UP to cover the screen.

        this.crtContainer.style.transform = 'perspective(1000px) rotateX(0deg) scale(3) translate(-5%, -5%)'; // Zoom in

        setTimeout(() => {
            this.state = 'game';
            // Here we would clear the CRT menu and show game text
            const crtInner = document.querySelector('.crt-inner-content');
            crtInner.innerHTML = '<div style="padding: 2rem; color: #50FF50; font-size: 1.5rem;">INITIALIZING NEURAL LINK...<br>CONNECTING TO TYGER PROTOCOL...<br><br>>_</div>';
        }, 2000);
    }
}

// Start on click to allow AudioContext (browsers block auto audio)
document.addEventListener('click', () => {
    if (!window.gameApp) {
        window.gameApp = new TitleScreen();
    }
}, { once: true });

// Also add a visible prompt to click if needed, or rely on user interaction
const prompt = document.createElement('div');
prompt.innerText = '[ CLICK TO START ]';
prompt.style.position = 'absolute';
prompt.style.bottom = '20%';
prompt.style.width = '100%';
prompt.style.textAlign = 'center';
prompt.style.color = '#555';
prompt.style.fontFamily = 'VT323';
prompt.style.fontSize = '2rem';
prompt.id = 'start-prompt';
document.body.appendChild(prompt);

document.addEventListener('click', () => {
    const p = document.getElementById('start-prompt');
    if (p) p.remove();
});
