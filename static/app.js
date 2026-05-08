/**
 * Bible Study Circle — Main JavaScript
 *
 * Handles the v3 interactive layout:
 * - Desktop: click passage → scripture shifts left, commentary panel opens right
 * - Mobile: accordion — commentary expands inline below passage
 * - Keyboard: Escape closes commentary
 */

let activePassage = null;

function isMobile() {
    return window.innerWidth <= 768;
}

/**
 * Initialize passage toggle for v3 layout.
 * Called from lecture template; safe to call when no passages exist.
 */
function initPassageToggle() {
    // Passages with data-passage attribute are interactive
    const passages = document.querySelectorAll('.passage[data-passage]');
    if (passages.length === 0) return;

    passages.forEach(passage => {
        passage.addEventListener('click', function(e) {
            // Don't toggle if clicking inside commentary-content
            if (e.target.closest('.commentary-content')) return;
            togglePassage(this.dataset.passage);
        });
    });
}

function togglePassage(id) {
    const passage = document.querySelector(`[data-passage="${id}"]`);
    const content = document.getElementById(`commentary-${id}`);
    if (!passage || !content) return;

    const panel = document.getElementById('commentaryPanel');
    const scriptureCol = document.getElementById('scriptureCol');

    // Same passage clicked — close
    if (activePassage === id) {
        closeCommentary();
        return;
    }

    // Deactivate previous
    if (activePassage) {
        const prevPassage = document.querySelector(`[data-passage="${activePassage}"]`);
        const prevContent = document.getElementById(`commentary-${activePassage}`);
        if (prevPassage) prevPassage.classList.remove('active');
        if (prevContent) prevContent.classList.remove('visible');

        // Desktop: move previous commentary back to its passage
        if (!isMobile() && prevPassage && prevContent) {
            prevPassage.appendChild(prevContent);
        }
    }

    // Activate new
    passage.classList.add('active');
    content.classList.add('visible');
    activePassage = id;

    if (!isMobile()) {
        // Desktop: move commentary to side panel
        const commentaryInner = document.getElementById('commentaryInner');
        if (commentaryInner && panel && scriptureCol) {
            commentaryInner.appendChild(content);
            scriptureCol.classList.add('shifted');
            panel.classList.add('open');
            panel.scrollTop = 0;
        }
    } else {
        // Mobile: scroll to commentary (inline under passage)
        setTimeout(() => {
            content.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 150);
    }

    // Invalidate any Leaflet maps inside the newly visible commentary
    setTimeout(() => {
        content.querySelectorAll('[id^="minimap"]').forEach(mapDiv => {
            const mapObj = window[mapDiv.id + '_map'];
            if (mapObj && typeof mapObj.invalidateSize === 'function') {
                mapObj.invalidateSize();
            }
        });
    }, 300);
}

function closeCommentary() {
    if (!activePassage) return;

    const passage = document.querySelector(`[data-passage="${activePassage}"]`);
    const content = document.getElementById(`commentary-${activePassage}`);
    const panel = document.getElementById('commentaryPanel');
    const scriptureCol = document.getElementById('scriptureCol');

    if (passage) passage.classList.remove('active');
    if (content) content.classList.remove('visible');

    // Desktop: move commentary back to its passage
    if (!isMobile() && passage && content) {
        passage.appendChild(content);
        if (scriptureCol) scriptureCol.classList.remove('shifted');
        if (panel) panel.classList.remove('open');
    }

    activePassage = null;
}

// Handle resize: reset layout if switching between mobile/desktop
let wasMobile = isMobile();
window.addEventListener('resize', () => {
    const nowMobile = isMobile();
    if (nowMobile !== wasMobile) {
        if (activePassage) {
            const passage = document.querySelector(`[data-passage="${activePassage}"]`);
            const content = document.getElementById(`commentary-${activePassage}`);
            const panel = document.getElementById('commentaryPanel');
            const scriptureCol = document.getElementById('scriptureCol');

            if (passage && content) passage.appendChild(content);
            if (scriptureCol) scriptureCol.classList.remove('shifted');
            if (panel) panel.classList.remove('open');
            passage.classList.remove('active');
            content.classList.remove('visible');
            activePassage = null;
        }
        wasMobile = nowMobile;
    }
});

// Keyboard: Escape closes commentary
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && activePassage) {
        closeCommentary();
    }
});
