/**
 * Bible Study Circle — Main JavaScript v2
 *
 * Handles the v3 interactive layout:
 * - Desktop: click passage → scripture shifts left, commentary panel opens right
 * - Mobile: accordion — commentary expands inline below passage
 * - Keyboard: Escape closes commentary or fullscreen map
 * - Fullscreen maps: overlay approach (appended to body)
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
                if (mapObj.getBounds && mapObj.getBounds().isValid()) {
                    mapObj.fitBounds(mapObj.getBounds().pad(0.15));
                }
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


/* ================================================================
   FULLSCREEN MAP — Overlay approach
   ================================================================
 *
 * Instead of making the map container position:fixed (which can fail
 * inside panels with overflow/transform), we create a dedicated
 * overlay div appended to document.body and move the map div into it.
 * On exit, we move the map div back to its original parent.
 *
 * Two entry points:
 *   toggleMiniMapFullscreen(btn)  — for lecture mini-maps (onclick on button)
 *   toggleMapFullscreen()         — for geography page (no params)
 */

// Track the overlay state
let _fsOverlay = null;      // the overlay div
let _fsMapDiv = null;       // the map div that was moved
let _fsOriginalParent = null; // original parent of mapDiv
let _fsOriginalNextSibling = null; // original next sibling for reinsertion
let _fsMapObjName = null;   // window property name for the Leaflet map object
let _fsIsGeography = false; // geography vs mini-map

/**
 * Mini-map fullscreen toggle (called from lecture buttons).
 * @param {HTMLElement} btn - The fullscreen toggle button
 */
function toggleMiniMapFullscreen(btn) {
    // If already in fullscreen via overlay, exit
    if (_fsOverlay) {
        _exitMapFullscreen();
        return;
    }

    var mc = btn.parentElement;
    var mapDiv = mc ? mc.querySelector('[id^="minimap"]') : null;
    if (!mapDiv) return;

    var mapObjName = mapDiv.id + '_map';
    var mapObj = window[mapObjName];

    _enterMapFullscreen(mapDiv, mapObj, mapObjName, false);
}

/**
 * Geography page fullscreen toggle (called from geography page).
 */
function toggleMapFullscreen() {
    // If already in fullscreen via overlay, exit
    if (_fsOverlay) {
        _exitMapFullscreen();
        return;
    }

    var mapDiv = document.getElementById('map');
    if (!mapDiv) return;

    // The geography map object is stored in a variable called 'map'
    var mapObj = window.map;
    _enterMapFullscreen(mapDiv, mapObj, 'map', true);
}

/**
 * Enter fullscreen: create overlay, move map into it.
 */
function _enterMapFullscreen(mapDiv, mapObj, mapObjName, isGeography) {
    _fsMapDiv = mapDiv;
    _fsOriginalParent = mapDiv.parentElement;
    _fsOriginalNextSibling = mapDiv.nextElementSibling;
    _fsMapObjName = mapObjName;
    _fsIsGeography = isGeography;

    // Remember original height
    var origHeight = mapDiv.style.height || (isGeography ? '500px' : '280px');

    // Create overlay
    var overlay = document.createElement('div');
    overlay.className = 'map-fullscreen-overlay';
    overlay.setAttribute('data-orig-height', origHeight);

    // Close button
    var closeBtn = document.createElement('button');
    closeBtn.className = 'map-fs-close';
    closeBtn.textContent = '✕';
    closeBtn.onclick = function(e) {
        e.stopPropagation();
        _exitMapFullscreen();
    };
    overlay.appendChild(closeBtn);

    // Map container inside overlay
    var mapContainer = document.createElement('div');
    mapContainer.className = 'map-fs-map';
    overlay.appendChild(mapContainer);

    // Append overlay to body
    document.body.appendChild(overlay);
    _fsOverlay = overlay;

    // Move map div into the overlay container
    mapContainer.appendChild(mapDiv);
    mapDiv.style.height = '100%';
    mapDiv.style.width = '100%';

    // Invalidate and refocus
    setTimeout(function() {
        if (mapObj && typeof mapObj.invalidateSize === 'function') {
            mapObj.invalidateSize();
            if (isGeography) {
                mapObj.setView([32.1, 35.3], 8);
            } else if (mapObj.getBounds && mapObj.getBounds().isValid()) {
                mapObj.fitBounds(mapObj.getBounds().pad(0.15));
            }
        }
    }, 250);
}

/**
 * Exit fullscreen: move map back, remove overlay.
 */
function _exitMapFullscreen() {
    if (!_fsOverlay || !_fsMapDiv || !_fsOriginalParent) return;

    var mapObj = window[_fsMapObjName];
    var origHeight = _fsOverlay.getAttribute('data-orig-height') || '280px';

    // Move map div back to original parent
    if (_fsOriginalNextSibling) {
        _fsOriginalParent.insertBefore(_fsMapDiv, _fsOriginalNextSibling);
    } else {
        _fsOriginalParent.appendChild(_fsMapDiv);
    }

    // Restore map div dimensions
    _fsMapDiv.style.height = origHeight;
    _fsMapDiv.style.width = '';
    _fsMapDiv.style.borderRadius = '6px';
    _fsMapDiv.style.border = '1px solid var(--border)';

    // Remove overlay
    _fsOverlay.remove();
    _fsOverlay = null;

    // Invalidate and refocus
    setTimeout(function() {
        if (mapObj && typeof mapObj.invalidateSize === 'function') {
            mapObj.invalidateSize();
            if (_fsIsGeography) {
                mapObj.setView([32.1, 35.3], 8);
            } else if (mapObj.getBounds && mapObj.getBounds().isValid()) {
                mapObj.fitBounds(mapObj.getBounds().pad(0.15));
            }
        }
    }, 250);

    // Reset state
    _fsMapDiv = null;
    _fsOriginalParent = null;
    _fsOriginalNextSibling = null;
    _fsMapObjName = null;
    _fsIsGeography = false;
}

// Keyboard: Escape closes drawer first, then fullscreen map, then commentary
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        var drawer = document.getElementById('courseDrawer');
        if (drawer && drawer.classList.contains('open')) {
            toggleCourseDrawer();
        } else if (_fsOverlay) {
            _exitMapFullscreen();
        } else if (activePassage) {
            closeCommentary();
        }
    }
});


/* ================================================================
   COURSE DRAWER — Right slide-out panel with search & accordion
   ================================================================ */

function toggleCourseDrawer() {
    var drawer = document.getElementById('courseDrawer');
    var overlay = document.getElementById('drawerOverlay');
    var btn = document.querySelector('.menu-btn');
    if (!drawer || !overlay) return;

    var isOpen = drawer.classList.contains('open');
    drawer.classList.toggle('open');
    overlay.classList.toggle('show');
    if (btn) btn.classList.toggle('open');

    if (!isOpen) {
        if (btn) btn.innerHTML = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/></svg> Закрыть';
        var searchInput = document.getElementById('drawerSearchInput');
        if (searchInput) setTimeout(function() { searchInput.focus(); }, 300);
    } else {
        if (btn) btn.innerHTML = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="2" y1="4" x2="14" y2="4"/><line x1="2" y1="8" x2="14" y2="8"/><line x1="2" y1="12" x2="14" y2="12"/></svg> Все курсы';
        var searchInput = document.getElementById('drawerSearchInput');
        if (searchInput) { searchInput.value = ''; filterDrawerCourses(); }
    }
}

function toggleDrawerGroup(header) {
    header.closest('.drawer-group').classList.toggle('collapsed');
}

function filterDrawerCourses() {
    var input = document.getElementById('drawerSearchInput');
    if (!input) return;
    var q = input.value.toLowerCase().trim();
    var groups = document.querySelectorAll('.drawer-group');
    groups.forEach(function(g) {
        var links = g.querySelectorAll('.drawer-link');
        var anyVisible = false;
        links.forEach(function(l) {
            var match = !q || l.textContent.toLowerCase().indexOf(q) !== -1;
            l.style.display = match ? '' : 'none';
            if (match) anyVisible = true;
        });
        g.style.display = anyVisible ? '' : 'none';
        // Auto-expand groups with matches when searching
        if (q && anyVisible) g.classList.remove('collapsed');
    });
}
