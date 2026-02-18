// clipboard.js — Blazor JSInterop helpers

/**
 * Fallback clipboard copy (for browsers where navigator.clipboard is unavailable).
 * @param {string} text
 */
window.clipboardFallback = function (text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    try {
        document.execCommand('copy');
    } finally {
        document.body.removeChild(textarea);
    }
};

/**
 * Scroll an element to its bottom.
 * @param {string} elementId
 */
window.scrollToBottom = function (elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.scrollTop = el.scrollHeight;
    }
};
