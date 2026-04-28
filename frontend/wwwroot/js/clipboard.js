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

const TG_SESSION_KEY = 'tg_session_id';

window.getTrackedSessionId = function () {
    return window.sessionStorage.getItem(TG_SESSION_KEY);
};

window.setTrackedSessionId = function (sessionId) {
    if (!sessionId) {
        return;
    }
    window.sessionStorage.setItem(TG_SESSION_KEY, sessionId);
};

window.clearTrackedSessionId = function () {
    window.sessionStorage.removeItem(TG_SESSION_KEY);
};
