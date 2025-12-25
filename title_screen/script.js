
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
        this.socket = null;

        // Elements
        this.titleOverlay = document.querySelector('.main-title-glitch');
        this.menuOverlay = document.querySelector('.main-menu');
        this.crtContainer = document.querySelector('.crt-screen-container');
        this.menuItems = document.querySelectorAll('.main-menu li');
        this.crtContent = document.querySelector('.crt-inner-content');

        this.selectedIndex = 0;
        this.inputBuffer = "";

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
            this.appendGameOutput(msg.data);
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
            // Handle Game Input
            if (e.key === 'Enter') {
                this.sendInput(this.inputBuffer);
                this.inputBuffer = "";
                // Append locally for immediate feedback?
                // Better wait for echo or handle manually if server doesn't echo input
                // this.appendGameOutput('> ' + this.inputBuffer + '\n');
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
        // Scroll to bottom
        this.crtContent.scrollTop = this.crtContent.scrollHeight;
    }

    sendInput(text) {
        if (this.socket) {
            this.socket.emit('player_input', { input: text });
            // Remove the temporary input line or reset it
            const inputLine = document.getElementById('input-line');
            if (inputLine) inputLine.innerText = '> ' + text; // Freeze it
            inputLine.id = ''; // remove id so new one is created
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
            this.crtContent.innerHTML = ''; // Clear content
            if (this.socket) {
                this.socket.emit('start_game');
            } else {
                this.crtContent.innerHTML = 'Socket connection failed.';
            }
        }, 2000);
    }

    appendGameOutput(text) {
        // Convert ANSI to HTML
        const html = this.ansiToHtml(text);

        // Append to content
        // If there's an active input line, insert before it
        const inputLine = document.getElementById('input-line');
        const span = document.createElement('span');
        span.innerHTML = html;

        if (inputLine) {
            this.crtContent.insertBefore(span, inputLine);
        } else {
            this.crtContent.appendChild(span);
        }

        // Scroll
        this.crtContent.scrollTop = this.crtContent.scrollHeight;
    }

    ansiToHtml(text) {
        // Simple ANSI parser for the colors we used
        // \033[91m -> <span style="color:red">
        // \033[0m -> </span>

        if (!text) return "";

        let html = text
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');

        // Colors from src/interface.py
        const colors = {
            '91': 'var(--red-term)', // Red
            '92': 'var(--green-term)', // Green
            '93': 'yellow', // Yellow
            '94': '#5050FF', // Blue
            '95': 'magenta', // Magenta
            '96': 'cyan', // Cyan
            '97': 'white', // White
            '36': 'cyan', // Sanity
            '35': 'magenta', // Reality
            '33': 'yellow', // Skill
            '32': 'var(--green-term)', // Item
            '1': 'font-weight:bold', // Bold
            '4': 'text-decoration:underline', // Underline
        };

        // Regex for ANSI codes: \033[...m
        html = html.replace(/\033\[([0-9;]+)m/g, (match, codes) => {
            const codeList = codes.split(';');
            let style = "";
            let reset = false;

            for (let c of codeList) {
                if (c === '0') {
                    reset = true;
                } else if (colors[c]) {
                    if (c === '1' || c === '4') {
                        style += colors[c] + ';';
                    } else {
                        style += `color:${colors[c]};`;
                    }
                }
            }

            if (reset) {
                return '</span>';
            } else {
                return `<span style="${style}">`;
            }
        });

        return html;
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
