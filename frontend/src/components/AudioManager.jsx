import { useEffect, useRef } from 'react';

const AudioManager = ({ music, sfxQueue, fearLevel = 0, mentalLoad = 0 }) => {
    const musicRef = useRef(new Audio());
    const currentMusicSrc = useRef(null);

    // Web Audio API refs
    const audioCtx = useRef(null);
    const musicSource = useRef(null);
    const filterNode = useRef(null);
    const heartbeatOsc = useRef(null);
    const tensionOsc = useRef(null);
    const gainNodes = useRef({});

    // Initialize Web Audio Context on first interaction/mount
    const initAudio = () => {
        if (!audioCtx.current) {
            audioCtx.current = new (window.AudioContext || window.webkitAudioContext)();

            // Filter for high fear "muffling"
            filterNode.current = audioCtx.current.createBiquadFilter();
            filterNode.current.type = 'lowpass';
            filterNode.current.frequency.value = 22000; // Default open
            filterNode.current.connect(audioCtx.current.destination);

            // Connect musicRef to filter
            musicSource.current = audioCtx.current.createMediaElementSource(musicRef.current);
            musicSource.current.connect(filterNode.current);

            // Setup Tension Hum (Synthesized)
            const tensionGain = audioCtx.current.createGain();
            tensionGain.gain.value = 0;
            tensionGain.connect(audioCtx.current.destination);
            gainNodes.current.tension = tensionGain;

            const tOsc = audioCtx.current.createOscillator();
            tOsc.type = 'sine';
            tOsc.frequency.value = 60; // 60Hz hum
            tOsc.connect(tensionGain);
            tOsc.start();
            tensionOsc.current = tOsc;

            // Setup Heartbeat (Simplistic Pulse)
            const hbGain = audioCtx.current.createGain();
            hbGain.gain.value = 0;
            hbGain.connect(audioCtx.current.destination);
            gainNodes.current.heartbeat = hbGain;
        }
    };

    // Handle Music
    useEffect(() => {
        if (!music) {
            musicRef.current.pause();
            currentMusicSrc.current = null;
            return;
        }

        const musicPath = `/audio/music/${music}`;

        if (currentMusicSrc.current !== musicPath) {
            musicRef.current.src = musicPath;
            musicRef.current.loop = true;
            musicRef.current.volume = 0.5;

            musicRef.current.play().catch(() => {
                // Wait for user interaction
                document.addEventListener('click', () => {
                    initAudio();
                    musicRef.current.play();
                }, { once: true });
            });

            currentMusicSrc.current = musicPath;
        }
    }, [music]);

    // Handle Dynamic Psychological Audio
    useEffect(() => {
        if (!audioCtx.current) return;
        if (audioCtx.current.state === 'suspended') audioCtx.current.resume();

        const now = audioCtx.current.currentTime;

        // 1. Muffle music at high fear
        if (filterNode.current) {
            const freq = fearLevel > 80 ? 400 : 22000;
            filterNode.current.frequency.setTargetAtTime(freq, now, 0.5);
        }

        // 2. Adjust Tension Hum (based on mental load)
        if (gainNodes.current.tension) {
            const vol = (mentalLoad / 100) * 0.15; // Subtle background hum
            gainNodes.current.tension.gain.setTargetAtTime(vol, now, 1);
            tensionOsc.current.frequency.setTargetAtTime(60 + (mentalLoad / 10), now, 1);
        }

        // 3. Heartbeat Effect (Triggers when fear > 50)
        let hbInterval;
        if (fearLevel > 50) {
            const bpm = 60 + (fearLevel - 50) * 1.5; // Scale from 60 to ~135 BPM
            const period = 60000 / bpm;

            hbInterval = setInterval(() => {
                // Play a simple double-thump
                const thump = (timeOffset) => {
                    const osc = audioCtx.current.createOscillator();
                    const gain = audioCtx.current.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(40, audioCtx.current.currentTime + timeOffset);
                    osc.frequency.exponentialRampToValueAtTime(0.01, audioCtx.current.currentTime + timeOffset + 0.1);
                    gain.gain.setValueAtTime(0.2, audioCtx.current.currentTime + timeOffset);
                    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.current.currentTime + timeOffset + 0.1);
                    osc.connect(gain);
                    gain.connect(audioCtx.current.destination);
                    osc.start();
                    osc.stop(audioCtx.current.currentTime + timeOffset + 0.12);
                };
                thump(0);
                thump(0.15);
            }, period);
        }

        return () => clearInterval(hbInterval);
    }, [fearLevel, mentalLoad]);

    // Handle SFX
    useEffect(() => {
        if (sfxQueue && sfxQueue.length > 0) {
            sfxQueue.forEach(sfx => {
                const sfxPath = `/audio/sfx/${sfx}`;
                const audio = new Audio(sfxPath);
                audio.volume = 0.8;
                audio.play().catch(e => console.warn("SFX failed:", e));
            });
        }
    }, [sfxQueue]);

    return null;
};

export default AudioManager;
