/**
 * Unified Tax Calculator
 * Manages tab switching and calculator instances
 */

document.addEventListener('DOMContentLoaded', function() {
    // Canada Province Tax Rates
    const CANADA_TAX_RATES = {
        'AB': { gst: 5, pst: 0, name: 'Alberta' },
        'BC': { gst: 5, pst: 7, name: 'British Columbia' },
        'MB': { gst: 5, pst: 7, name: 'Manitoba' },
        'NB': { gst: 15, pst: 0, name: 'New Brunswick (HST)' },
        'NL': { gst: 15, pst: 0, name: 'Newfoundland and Labrador (HST)' },
        'NT': { gst: 5, pst: 0, name: 'Northwest Territories' },
        'NS': { gst: 15, pst: 0, name: 'Nova Scotia (HST)' },
        'NU': { gst: 5, pst: 0, name: 'Nunavut' },
        'ON': { gst: 13, pst: 0, name: 'Ontario (HST)' },
        'PE': { gst: 15, pst: 0, name: 'Prince Edward Island (HST)' },
        'QC': { gst: 5, pst: 9.975, name: 'Quebec (GST + QST)' },
        'SK': { gst: 5, pst: 6, name: 'Saskatchewan' },
        'YT': { gst: 5, pst: 0, name: 'Yukon' }
    };

    // Initialize calculator instances
    const calculators = {
        us: new CalculatorEngine('us'),
        canada: new CalculatorEngine('canada'),
        vat: new CalculatorEngine('vat')
    };

    // Initialize each calculator
    calculators.us.init('tab-us');
    calculators.canada.init('tab-canada');
    calculators.vat.init('tab-vat');

    // Setup Canada province auto-population
    const provinceSelect = document.getElementById('canada-province-select');
    const taxRatesSection = document.getElementById('canada-tax-rates-section');
    const gstRateInput = document.getElementById('canada-gst-rate');
    const pstRateInput = document.getElementById('canada-pst-rate');

    if (provinceSelect) {
        provinceSelect.addEventListener('change', function() {
            const provinceCode = this.value;

            if (provinceCode && CANADA_TAX_RATES[provinceCode]) {
                const rates = CANADA_TAX_RATES[provinceCode];

                // Show tax rates section
                taxRatesSection.style.display = 'block';

                // Auto-populate rates (but keep them editable)
                gstRateInput.value = rates.gst;
                pstRateInput.value = rates.pst;

                console.log(`Auto-populated tax rates for ${rates.name}: GST/HST ${rates.gst}%, PST/QST ${rates.pst}%`);
            } else {
                // Hide tax rates section if no province selected
                taxRatesSection.style.display = 'none';
                gstRateInput.value = '';
                pstRateInput.value = '';
            }
        });
    }

    // Tab switching logic
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;

            // Save current tab state before switching
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab) {
                const activeType = activeTab.id.replace('tab-', '');
                if (calculators[activeType]) {
                    calculators[activeType].saveState();
                }
            }

            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Update active tab content
            tabContents.forEach(content => {
                if (content.id === `tab-${targetTab}`) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });

            // Restore state for new tab
            if (calculators[targetTab]) {
                calculators[targetTab].restoreState();
            }

            // Update URL hash for bookmarking
            window.location.hash = targetTab;
        });
    });

    // Handle initial hash in URL
    const initialHash = window.location.hash.substring(1);
    if (initialHash && ['us', 'canada', 'vat'].includes(initialHash)) {
        const targetButton = document.querySelector(`.tab-btn[data-tab="${initialHash}"]`);
        if (targetButton) {
            targetButton.click();
        }
    }

    // Handle browser back/forward buttons
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash.substring(1);
        if (hash && ['us', 'canada', 'vat'].includes(hash)) {
            const targetButton = document.querySelector(`.tab-btn[data-tab="${hash}"]`);
            if (targetButton && !targetButton.classList.contains('active')) {
                targetButton.click();
            }
        }
    });

    // Clear session storage on page unload (optional)
    window.addEventListener('beforeunload', function() {
        // Optionally clear saved states
        // sessionStorage.removeItem('calculator_state_us');
        // sessionStorage.removeItem('calculator_state_canada');
        // sessionStorage.removeItem('calculator_state_vat');
    });

    console.log('Unified Tax Calculator initialized successfully');
});
