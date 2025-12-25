
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

    playKeySound() {
        // Very short blip for typing
        if (this.ctx.state === 'suspended') this.ctx.resume();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.frequency.setValueAtTime(800 + Math.random() * 200, this.ctx.currentTime);
        gain.gain.setValueAtTime(0.02, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.03);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.03);
    }
}

class TitleScreen {
    constructor() {
        this.audio = new AudioSystem();
        this.state = 'intro'; // intro, main_menu, transition, game
        this.socket = null;

        // Elements
        this.titleOverlay = document.querySelector('.main-title-glitch');
        this.menuOverlay = document.querySelector('.main-menu');
        this.crtContainer = document.querySelector('.crt-screen-container');
        this.menuItems = document.querySelectorAll('.main-menu li');
        this.crtContent = document.querySelector('.crt-inner-content');

        this.selectedIndex = 0;
        this.inputBuffer = "";

        // Typewriter queue
        this.printQueue = [];
        this.isTyping = false;
        this.typeSpeed = 10; // ms per char

        this.init();
    }

    init() {
        // Connect Socket
        if (typeof io !== 'undefined') {
            this.socket = io();
            this.setupSocketListeners();
        } else {
            console.warn("Socket.io not found. Game mode will not work.");
        }

        // Initial State
        this.titleOverlay.style.opacity = '0';
        this.menuOverlay.style.opacity = '0';
        this.crtContainer.style.opacity = '0';
        this.crtContainer.style.display = 'none';

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

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('game_output', (msg) => {
            this.queueOutput(msg.data);
        });

        this.socket.on('game_started', () => {
            console.log('Game Process Started');
        });
    }

    startIntro() {
        this.audio.playIntroDrone();

        setTimeout(() => {
            this.titleOverlay.style.transition = 'opacity 2s ease-in';
            this.titleOverlay.style.opacity = '1';
        }, 1000);

        setTimeout(() => {
            this.state = 'main_menu';
            this.menuOverlay.style.transition = 'opacity 1s ease';
            this.menuOverlay.style.opacity = '1';
            this.updateSelection();
        }, 3500);
    }

    handleInput(e) {
        if (this.state === 'main_menu') {
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
        } else if (this.state === 'game') {
            // Speed up typing on key press
            if (this.isTyping) {
                this.typeSpeed = 0;
                return; // Consume key press to just speed up
            }

            // Shortcuts
            if (e.key === 'F1') {
                e.preventDefault();
                this.inputBuffer = "feedback ";
                this.updateInputLine();
                return;
            }

            // Handle Game Input
            if (e.key === 'Enter') {
                this.sendInput(this.inputBuffer);
                this.inputBuffer = "";
            } else if (e.key === 'Backspace') {
                this.inputBuffer = this.inputBuffer.slice(0, -1);
                this.updateInputLine();
            } else if (e.key.length === 1) {
                this.inputBuffer += e.key;
                this.updateInputLine();
            }
        }
    }

    updateInputLine() {
        let inputLine = document.getElementById('input-line');
        if (!inputLine) {
             const div = document.createElement('div');
             div.id = 'input-line';
             this.crtContent.appendChild(div);
             inputLine = div;
        }
        inputLine.innerText = '> ' + this.inputBuffer + '_';
        this.scrollToBottom();
    }

    sendInput(text) {
        if (this.socket) {
            this.socket.emit('player_input', { input: text });
            // Freeze current input line
            const inputLine = document.getElementById('input-line');
            if (inputLine) {
                inputLine.innerText = '> ' + text;
                inputLine.id = ''; // Remove ID
            }
            // Add newline locally to separate output
            // this.queueOutput('\n');
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

        this.titleOverlay.style.transition = 'opacity 1s ease';
        this.titleOverlay.style.opacity = '0';

        this.menuOverlay.style.transition = 'opacity 1s ease';
        this.menuOverlay.style.opacity = '0';

        this.crtContainer.style.display = 'block';
        void this.crtContainer.offsetWidth;

        this.crtContainer.style.transition = 'opacity 2s ease, transform 2s ease-out';
        this.crtContainer.style.opacity = '1';
        this.crtContainer.style.transform = 'perspective(1000px) rotateX(0deg) scale(3) translate(-5%, -5%)';

        setTimeout(() => {
            this.state = 'game';
            this.crtContent.innerHTML = '';
            if (this.socket) {
                this.socket.emit('start_game');
            } else {
                this.crtContent.innerHTML = 'Socket connection failed.';
            }
        }, 2000);
    }

    queueOutput(text) {
        const tokens = this.parseAnsi(text);
        this.printQueue.push(...tokens);
        if (!this.isTyping) {
            this.processQueue();
        }
    }

    async processQueue() {
        if (this.printQueue.length === 0) {
            this.isTyping = false;
            this.typeSpeed = 10; // Reset speed
            this.updateInputLine(); // Ensure input line is at bottom
            return;
        }

        this.isTyping = true;
        const token = this.printQueue.shift();

        // Find or create current span
        // We append to the main container, before the input line
        const inputLine = document.getElementById('input-line');

        // If token has style, create new span, else stick to plain text?
        // Actually each token is a style block.

        const span = document.createElement('span');
        if (token.style) {
            span.style.cssText = token.style;
        }

        if (inputLine) {
            this.crtContent.insertBefore(span, inputLine);
        } else {
            this.crtContent.appendChild(span);
        }

        // Type out text content
        for (let char of token.text) {
            span.textContent += char;
            this.scrollToBottom();

            // Audio feedback occasionally
            if (Math.random() > 0.8) this.audio.playKeySound();

            if (this.typeSpeed > 0) {
                await new Promise(r => setTimeout(r, this.typeSpeed));
            }
        }

        // Next token
        this.processQueue();
    }

    scrollToBottom() {
        this.crtContent.scrollTop = this.crtContent.scrollHeight;
    }

    parseAnsi(text) {
        // Returns array of { text: string, style: string }
        if (!text) return [];

        const tokens = [];
        let currentStyle = "";

        const colors = {
            '91': 'var(--red-term)',
            '92': 'var(--green-term)',
            '93': 'yellow',
            '94': '#5050FF',
            '95': 'magenta',
            '96': 'cyan',
            '97': 'white',
            '36': 'cyan',
            '35': 'magenta',
            '33': 'yellow',
            '32': 'var(--green-term)',
            '1': 'font-weight:bold',
            '4': 'text-decoration:underline',
        };

        const parts = text.split(/(\033\[[0-9;]+m)/);

        for (let part of parts) {
            if (part.startsWith('\033[')) {
                // Parse code
                const codes = part.substring(2, part.length - 1).split(';');
                for (let c of codes) {
                    if (c === '0') {
                        currentStyle = "";
                    } else if (colors[c]) {
                         if (c === '1' || c === '4') {
                            currentStyle += colors[c] + ';';
                        } else {
                            currentStyle += `color:${colors[c]};`;
                        }
                    }
                }
            } else if (part.length > 0) {
                tokens.push({ text: part, style: currentStyle });
            }
        }

        return tokens;
    }
}

// Start on click
document.addEventListener('click', () => {
    if (!window.gameApp) {
        window.gameApp = new TitleScreen();
    }
}, { once: true });

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
