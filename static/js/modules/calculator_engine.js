/**
 * Modular Calculator Engine
 * Core engine for tax calculations with pluggable configurations
 */

class CalculatorEngine {
    constructor(calculatorType) {
        this.calculatorType = calculatorType;
        this.state = {
            items: [],
            discounts: [],
            shipping: {
                cost: 0,
                taxable: false,
                taxRate: 0
            },
            options: {}
        };
        this.itemCounter = 0;
        this.discountCounter = 0;
    }

    /**
     * Initialize the calculator for a specific tab
     */
    init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        this.form = this.container.querySelector('.calculator-form');
        this.setupEventListeners();
        this.addInitialItem();
    }

    /**
     * Setup event listeners for the calculator
     */
    setupEventListeners() {
        // Add item button
        const addItemBtn = this.container.querySelector('[data-action="add-item"]');
        if (addItemBtn) {
            addItemBtn.addEventListener('click', () => this.addItem());
        }

        // Add discount button
        const addDiscountBtn = this.container.querySelector('[data-action="add-discount"]');
        if (addDiscountBtn) {
            addDiscountBtn.addEventListener('click', () => this.addDiscount());
        }

        // Reset button
        const resetBtn = this.container.querySelector('[data-action="reset"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.reset());
        }

        // Shipping taxable toggle
        const shippingTaxableSelect = this.form.querySelector('select[name="shipping_taxable"]');
        if (shippingTaxableSelect) {
            shippingTaxableSelect.addEventListener('change', (e) => {
                this.toggleShippingTaxRate(e.target.value === 'true');
            });
        }

        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });
    }

    /**
     * Add an item input row
     */
    addItem() {
        this.itemCounter++;
        const itemsContainer = this.form.querySelector('.items-container');
        const itemRow = this.createItemRow(this.itemCounter);
        itemsContainer.appendChild(itemRow);
    }

    /**
     * Create item row HTML based on calculator type
     */
    createItemRow(index) {
        const row = document.createElement('div');
        row.className = 'item-row';
        row.dataset.itemIndex = index;

        // VAT and Canada use simple price-only rows (tax rates are separate)
        if (this.calculatorType === 'vat' || this.calculatorType === 'canada') {
            row.classList.add('vat-item');
            row.innerHTML = `
                <div class="form-field">
                    <label class="field-label">Item ${index} Price</label>
                    <input type="number" class="field-input" name="item_price_${index}"
                           step="0.01" min="0" placeholder="0.00" required>
                </div>
                <button type="button" class="btn-delete" data-action="delete-item" data-index="${index}">
                    Delete
                </button>
            `;
        } else {
            // US calculator has tax rate per item
            row.innerHTML = `
                <div class="form-field">
                    <label class="field-label">Item ${index} Price</label>
                    <input type="number" class="field-input" name="item_price_${index}"
                           step="0.01" min="0" placeholder="0.00" required>
                </div>
                <div class="form-field">
                    <label class="field-label">Tax Rate (%)</label>
                    <input type="number" class="field-input" name="item_tax_rate_${index}"
                           step="0.01" min="0" placeholder="0.00" required>
                </div>
                <button type="button" class="btn-delete" data-action="delete-item" data-index="${index}">
                    Delete
                </button>
            `;
        }

        // Add delete event listener
        const deleteBtn = row.querySelector('[data-action="delete-item"]');
        deleteBtn.addEventListener('click', () => this.deleteItem(index));

        return row;
    }

    /**
     * Delete an item row
     */
    deleteItem(index) {
        const itemsContainer = this.form.querySelector('.items-container');
        const itemRow = itemsContainer.querySelector(`[data-item-index="${index}"]`);
        if (itemRow) {
            itemRow.remove();
        }

        // Ensure at least one item exists
        const remainingItems = itemsContainer.querySelectorAll('.item-row');
        if (remainingItems.length === 0) {
            this.addInitialItem();
        }
    }

    /**
     * Add initial item on load
     */
    addInitialItem() {
        this.addItem();
    }

    /**
     * Add a discount input row
     */
    addDiscount() {
        this.discountCounter++;
        const discountsContainer = this.form.querySelector('.discounts-container');
        const discountRow = this.createDiscountRow(this.discountCounter);
        discountsContainer.appendChild(discountRow);
    }

    /**
     * Create discount row HTML
     */
    createDiscountRow(index) {
        const row = document.createElement('div');
        row.className = 'discount-row';
        row.dataset.discountIndex = index;

        row.innerHTML = `
            <div class="form-field">
                <label class="field-label">Discount ${index} Amount</label>
                <input type="number" class="field-input" name="discount_amount_${index}"
                       step="0.01" min="0" placeholder="0.00">
            </div>
            <button type="button" class="btn-delete" data-action="delete-discount" data-index="${index}">
                Delete
            </button>
        `;

        // Add delete event listener
        const deleteBtn = row.querySelector('[data-action="delete-discount"]');
        deleteBtn.addEventListener('click', () => this.deleteDiscount(index));

        return row;
    }

    /**
     * Delete a discount row
     */
    deleteDiscount(index) {
        const discountsContainer = this.form.querySelector('.discounts-container');
        const discountRow = discountsContainer.querySelector(`[data-discount-index="${index}"]`);
        if (discountRow) {
            discountRow.remove();
        }
    }

    /**
     * Toggle shipping tax rate field visibility
     */
    toggleShippingTaxRate(show) {
        const shippingTaxRateSection = this.form.querySelector(`#${this.calculatorType}-shipping-tax-rate`);
        if (shippingTaxRateSection) {
            shippingTaxRateSection.style.display = show ? 'block' : 'none';
        }
    }

    /**
     * Reset the calculator form
     */
    reset() {
        if (confirm('Are you sure you want to clear all data?')) {
            this.form.reset();

            // Clear items
            const itemsContainer = this.form.querySelector('.items-container');
            itemsContainer.innerHTML = '';
            this.itemCounter = 0;
            this.addInitialItem();

            // Clear discounts
            const discountsContainer = this.form.querySelector('.discounts-container');
            discountsContainer.innerHTML = '';
            this.discountCounter = 0;

            // Hide results
            this.hideResults();
        }
    }

    /**
     * Collect form data for submission
     */
    collectFormData() {
        const formData = new FormData(this.form);
        const data = {
            calculator_type: this.calculatorType,
            items: [],
            discounts: [],
            shipping_cost: parseFloat(formData.get('shipping_cost')) || 0,
            shipping_taxable: formData.get('shipping_taxable') === 'true',
            options: {}
        };

        // Collect items
        const itemRows = this.form.querySelectorAll('.item-row');
        itemRows.forEach((row) => {
            const index = row.dataset.itemIndex;
            const priceStr = formData.get(`item_price_${index}`);
            const taxRateStr = formData.get(`item_tax_rate_${index}`);

            // Only add item if price is a valid number
            const price = parseFloat(priceStr);
            if (!isNaN(price) && price > 0) {
                const item = { price: price };
                // For US calculator, each item has its own tax rate
                if (this.calculatorType === 'us') {
                    const taxRate = parseFloat(taxRateStr);
                    item.tax_rate = !isNaN(taxRate) ? taxRate : 0;
                }
                data.items.push(item);
            }
        });

        // Collect discounts (with item_index for proper tax calculation)
        const discountRows = this.form.querySelectorAll('.discount-row');
        let discountIndex = 1;
        discountRows.forEach((row) => {
            const index = row.dataset.discountIndex;
            const amountStr = formData.get(`discount_amount_${index}`);
            const amount = parseFloat(amountStr);

            if (!isNaN(amount) && amount > 0) {
                // Apply discounts to first item by default for proper tax calculation
                data.discounts.push({ amount: amount, item_index: 1 });
                discountIndex++;
            }
        });

        // Collect calculator-specific options
        if (this.calculatorType === 'us') {
            data.options.is_sales_before_tax = formData.get('is_sales_before_tax') === 'on';
            data.options.discount_is_taxable = formData.get('discount_is_taxable') === 'on';

            if (data.shipping_taxable) {
                data.shipping_tax_rate = parseFloat(formData.get('shipping_tax_rate') || 0);
            }
        }

        if (this.calculatorType === 'canada') {
            data.options.is_sales_before_tax = formData.get('is_sales_before_tax') === 'on';
            data.options.discount_is_taxable = formData.get('discount_is_taxable') === 'on';
            data.province = formData.get('province');
            data.gst_rate = parseFloat(formData.get('gst_rate') || 0);
            data.pst_rate = parseFloat(formData.get('pst_rate') || 0);
        }

        if (this.calculatorType === 'vat') {
            data.vat_rate = parseFloat(formData.get('vat_rate') || 0);
            data.options.is_sales_before_tax = formData.get('is_sales_before_tax') === 'on';
            data.options.discount_is_taxable = formData.get('discount_is_taxable') === 'on';
        }

        return data;
    }

    /**
     * Handle form submission
     */
    async handleSubmit() {
        try {
            const data = this.collectFormData();

            // Validate data
            if (data.items.length === 0) {
                this.showError('Please add at least one item');
                return;
            }

            if (this.calculatorType === 'vat' && !data.vat_rate) {
                this.showError('Please enter a VAT rate');
                return;
            }

            if (this.calculatorType === 'canada') {
                if (!data.province) {
                    this.showError('Please select a province');
                    return;
                }
                if (!data.gst_rate && !data.pst_rate) {
                    this.showError('Please enter GST/PST rates (at least one must be greater than 0)');
                    return;
                }
            }

            // Show loading state
            this.showLoading();

            // Submit to server
            const response = await fetch('/tools/unified_tax_calculator', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                this.displayResults(result.data);
            } else {
                this.showError(result.error || 'Calculation failed');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showError('An error occurred while calculating. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Display calculation results
     */
    displayResults(data) {
        const resultsSection = this.container.querySelector('.results-section');
        resultsSection.innerHTML = this.formatResults(data);
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Format results HTML based on calculator type
     */
    formatResults(data) {
        if (this.calculatorType === 'vat') {
            return this.formatVATResults(data);
        } else {
            return this.formatSalesTaxResults(data);
        }
    }

    /**
     * Format sales tax results (US/Canada)
     */
    formatSalesTaxResults(data) {
        return `
            <div class="results-header">
                <h2 class="results-title">Calculation Results</h2>
            </div>
            <div class="results-summary">
                <div class="result-item">
                    <div class="result-label">Item Total</div>
                    <div class="result-value">$${data.item_total.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Discount Total</div>
                    <div class="result-value">-$${data.discount_total.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Shipping Cost</div>
                    <div class="result-value">$${data.shipping_cost.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Total Tax</div>
                    <div class="result-value highlight">$${data.total_tax.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Total Amount</div>
                    <div class="result-value highlight">$${data.total_amount.toFixed(2)}</div>
                </div>
            </div>
            ${data.tax_breakdown && data.tax_breakdown.length > 0 ? `
                <div class="result-breakdown">
                    <h3 class="breakdown-title">Tax Breakdown</h3>
                    <ul class="breakdown-list">
                        ${data.tax_breakdown.map(item => `
                            <li class="breakdown-item">
                                <span class="breakdown-item-label">${item.item}</span>
                                <span class="breakdown-item-value">$${item.tax.toFixed(2)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }

    /**
     * Format VAT results
     */
    formatVATResults(data) {
        return `
            <div class="results-header">
                <h2 class="results-title">VAT Calculation Results</h2>
            </div>
            <div class="results-summary">
                <div class="result-item">
                    <div class="result-label">Item Total</div>
                    <div class="result-value">$${data.item_total.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Discount Total</div>
                    <div class="result-value">-$${data.discount_total.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Shipping Cost</div>
                    <div class="result-value">$${data.shipping_cost.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Net Amount</div>
                    <div class="result-value">$${data.net_amount.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">VAT Amount (${data.vat_rate_applied.toFixed(2)}%)</div>
                    <div class="result-value highlight">$${data.vat_amount.toFixed(2)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">Gross Amount</div>
                    <div class="result-value highlight">$${data.gross_amount.toFixed(2)}</div>
                </div>
            </div>
            ${data.vat_breakdown && data.vat_breakdown.length > 0 ? `
                <div class="result-breakdown">
                    <h3 class="breakdown-title">VAT Breakdown</h3>
                    <ul class="breakdown-list">
                        ${data.vat_breakdown.map(item => `
                            <li class="breakdown-item">
                                <span class="breakdown-item-label">${item.item} (Net: $${item.net_amount.toFixed(2)})</span>
                                <span class="breakdown-item-value">$${item.vat.toFixed(2)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }

    /**
     * Hide results section
     */
    hideResults() {
        const resultsSection = this.container.querySelector('.results-section');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        const submitBtn = this.form.querySelector('.btn-calculate');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Calculating...';
        }
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        const submitBtn = this.form.querySelector('.btn-calculate');
        if (submitBtn) {
            submitBtn.disabled = false;
            const btnText = this.calculatorType === 'vat' ? 'Calculate VAT' : 'Calculate Tax';
            submitBtn.textContent = btnText;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        alert(message); // You can replace this with a more elegant error display
    }

    /**
     * Save current state (for tab switching)
     */
    saveState() {
        const data = this.collectFormData();
        sessionStorage.setItem(`calculator_state_${this.calculatorType}`, JSON.stringify(data));
    }

    /**
     * Restore saved state (for tab switching)
     */
    restoreState() {
        const savedState = sessionStorage.getItem(`calculator_state_${this.calculatorType}`);
        if (savedState) {
            try {
                const data = JSON.parse(savedState);
                this.populateForm(data);
            } catch (e) {
                console.error('Error restoring state:', e);
            }
        }
    }

    /**
     * Populate form with saved data
     */
    populateForm(data) {
        // This would be implemented to restore form values
        // For now, we'll keep forms independent on tab switch
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CalculatorEngine;
}
