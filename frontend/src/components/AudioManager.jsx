import { useEffect, useRef } from 'react';

const AudioManager = ({ music, sfxQueue }) => {
    const musicRef = useRef(new Audio());
    const currentMusicSrc = useRef(null);

    // Handle Music
    useEffect(() => {
        if (!music) {
            musicRef.current.pause();
            currentMusicSrc.current = null;
            return;
        }

        const musicPath = `/audio/music/${music}`;

        // Only change if the source is different
        if (currentMusicSrc.current !== musicPath) {
            // Fade out old music (optional enhancement for later)

            musicRef.current.src = musicPath;
            musicRef.current.loop = true;
            musicRef.current.volume = 0.5; // Default volume

            musicRef.current.play().catch(e => {
                console.warn("Audio play failed (user interaction needed?):", e);
            });

            currentMusicSrc.current = musicPath;
            console.log(`[Audio] Playing music: ${music}`);
        }

        return () => {
            // Cleanup: pause if unmounting or changing source
            // We don't strictly need to pause if we are just switching tracks (the next effect run handles it),
            // but it's good safety. However, since the next effect run will change the src, 
            // pausing here might cause a brief silence if not handled perfectly. 
            // But for now, let's keep it simple.
            // musicRef.current.pause(); 
            // currentMusicSrc.current = null;
        };
    }, [music]);

    // Handle SFX
    useEffect(() => {
        if (sfxQueue && sfxQueue.length > 0) {
            sfxQueue.forEach(sfx => {
                const sfxPath = `/audio/sfx/${sfx}`;
                const audio = new Audio(sfxPath);
                audio.volume = 0.8;
                audio.play().catch(e => console.warn("SFX play failed:", e));
                console.log(`[Audio] Playing SFX: ${sfx}`);
            });
        }
    }, [sfxQueue]); // Note: This depends on sfxQueue being a new array reference each time

    return null; // Invisible component
};

export default AudioManager;
