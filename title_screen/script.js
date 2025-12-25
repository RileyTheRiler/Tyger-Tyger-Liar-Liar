document.addEventListener('DOMContentLoaded', () => {
    const mainMenuItems = document.querySelectorAll('.main-menu li');
    const crtMenuItems = document.querySelectorAll('.crt-menu li');
    let currentIndex = 0;

    function updateSelection(index) {
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

    // Initial selection
    updateSelection(0);

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp' || e.key === 'w') {
            updateSelection(currentIndex - 1);
        } else if (e.key === 'ArrowDown' || e.key === 's') {
            updateSelection(currentIndex + 1);
        } else if (e.key === 'Enter' || e.key === ' ') {
            triggerAction(currentIndex);
        }
    });

    // Mouse support
    mainMenuItems.forEach((item, i) => {
        item.addEventListener('mouseenter', () => {
            updateSelection(i);
        });
        item.addEventListener('click', () => {
            triggerAction(i);
        });
    });

    function triggerAction(index) {
        const action = mainMenuItems[index].textContent.trim();
        console.log(`Action triggered: ${action}`);
        // Visual feedback or logic can go here. For now, log it.
    }
});
