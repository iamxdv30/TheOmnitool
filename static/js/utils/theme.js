/**
 * theme.js - Theme management utilities
 * Handles theme switching between light and dark modes
 */

const ThemeManager = (function() {
    'use strict';
    
    // Theme constants
    const THEME_STORAGE_KEY = 'theme';
    const DARK_THEME = 'dark';
    const LIGHT_THEME = 'light';
    
    // DOM elements
    let themeToggleButton;
    
    /**
     * Initialize the theme system
     */
    function init() {
        // Cache DOM elements
        themeToggleButton = document.getElementById('theme-toggle-button');
        
        // Set initial theme based on localStorage or system preference
        setInitialTheme();
        
        // Bind events
        bindEvents();
    }
    
    /**
     * Set the initial theme based on stored preference or system preference
     */
    function setInitialTheme() {
        // Check localStorage first
        const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
        
        if (storedTheme) {
            // Use stored preference
            applyTheme(storedTheme);
        } else {
            // Check system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            applyTheme(prefersDark ? DARK_THEME : LIGHT_THEME);
        }
        
        // Update toggle button state if it exists
        updateToggleButtonState();
    }
    
    /**
     * Bind event listeners
     */
    function bindEvents() {
        // Theme toggle button click handler
        if (themeToggleButton) {
            themeToggleButton.addEventListener('click', toggleTheme);
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            // Only apply system preference if user hasn't set a preference
            if (!localStorage.getItem(THEME_STORAGE_KEY)) {
                applyTheme(e.matches ? DARK_THEME : LIGHT_THEME);
                updateToggleButtonState();
            }
        });
    }
    
    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
        
        applyTheme(newTheme);
        saveThemePreference(newTheme);
        updateToggleButtonState();
        
        // Dispatch custom event for other components
        document.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: newTheme } 
        }));
    }
    
    /**
     * Apply the specified theme to the document
     * @param {string} theme - The theme to apply ('dark' or 'light')
     */
    function applyTheme(theme) {
        if (theme === DARK_THEME) {
            document.documentElement.classList.add(DARK_THEME);
        } else {
            document.documentElement.classList.remove(DARK_THEME);
        }
    }
    
    /**
     * Save theme preference to localStorage
     * @param {string} theme - The theme preference to save
     */
    function saveThemePreference(theme) {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
    }
    
    /**
     * Get the current active theme
     * @return {string} - The current theme ('dark' or 'light')
     */
    function getCurrentTheme() {
        return document.documentElement.classList.contains(DARK_THEME) ? DARK_THEME : LIGHT_THEME;
    }
    
    /**
     * Update the toggle button state to match current theme
     */
    function updateToggleButtonState() {
        if (!themeToggleButton) return;
        
        const currentTheme = getCurrentTheme();
        
        // Update button text/icon based on current theme
        if (currentTheme === DARK_THEME) {
            themeToggleButton.setAttribute('aria-label', 'Switch to light mode');
            // If using an icon font or SVG, update it here
        } else {
            themeToggleButton.setAttribute('aria-label', 'Switch to dark mode');
            // If using an icon font or SVG, update it here
        }
    }
    
    // Public API
    return {
        init: init,
        toggleTheme: toggleTheme,
        getCurrentTheme: getCurrentTheme,
        applyTheme: applyTheme
    };
})();

// Initialize theme manager when document is ready
document.addEventListener('DOMContentLoaded', function() {
    ThemeManager.init();
});
