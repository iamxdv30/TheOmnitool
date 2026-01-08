/**
 * tax_calculator.js - Tax Calculator functionality
 * Handles tax calculation logic, form interactions, and result display
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        TaxCalculator.init();
    });
    
    const TaxCalculator = {
        // State variables
        itemCount: 0,
        discountCount: 0,
        
        init() {
            this.cacheElements();
            this.initializeCounters();
            this.bindEvents();
        },
        
        cacheElements() {
            this.elements = {
                form: document.getElementById('taxForm'),
                calculatorType: document.getElementById('calculator-type'),
                itemsContainer: document.getElementById('itemsContainer'),
                discountsContainer: document.getElementById('discountsContainer'),
                shippingTaxable: document.querySelector('select[name="shipping_taxable"]'),
                shippingTaxRateSection: document.getElementById('shipping_tax_rate_section'),
                addItemButton: document.getElementById('addItemBtn'),
                addDiscountButton: document.getElementById('addDiscountBtn'),
                calculateButton: document.querySelector('#taxForm button[type="submit"]')
            };
        },
        
        initializeCounters() {
            // Get initial counts from the form or default values
            const itemElements = document.querySelectorAll('.item');
            const discountElements = document.querySelectorAll('.discount');
            
            this.itemCount = itemElements.length || 1;
            this.discountCount = discountElements.length || 0;
        },
        
        bindEvents() {
            if (this.elements.form) {
                // Remove inline event handlers and replace with proper listeners
                this.elements.form.addEventListener('submit', this.handleFormSubmit.bind(this));
            }
            
            if (this.elements.calculatorType) {
                this.elements.calculatorType.removeAttribute('onchange');
                this.elements.calculatorType.addEventListener('change', this.handleCalculatorChange.bind(this));
            }
            
            if (this.elements.shippingTaxable) {
                this.elements.shippingTaxable.removeAttribute('onchange');
                this.elements.shippingTaxable.addEventListener('change', this.toggleShippingTaxRate.bind(this));
            }
            
            if (this.elements.addItemButton) {
                this.elements.addItemButton.removeAttribute('onclick');
                this.elements.addItemButton.addEventListener('click', this.addItem.bind(this));
            }
            
            if (this.elements.addDiscountButton) {
                this.elements.addDiscountButton.removeAttribute('onclick');
                this.elements.addDiscountButton.addEventListener('click', this.addDiscount.bind(this));
            }
            
            if (this.elements.calculateButton) {
                this.elements.calculateButton.addEventListener('click', this.handleFormSubmit.bind(this));
            }
        },
        
        /**
         * Handle calculator type change
         * @param {Event} event - Change event
         */
        handleCalculatorChange(event) {
            const selectElement = event.target;
            if (selectElement.value === 'canada') {
                window.location.href = selectElement.dataset.caCalculatorUrl;
            } else {
                // Stay on current page for US calculator
                return;
            }
        },
        
        /**
         * Add a new item row to the form
         */
        addItem() {
            this.itemCount++;
            const newItem = document.createElement('div');
            newItem.classList.add('item');
            newItem.innerHTML = `
                <label for="item_price_${this.itemCount}">Item ${this.itemCount} Price:</label>
                <input type="number" step="0.0001" name="item_price_${this.itemCount}" required>
                <label for="item_tax_rate_${this.itemCount}">Tax Rate (%):</label>
                <input type="number" step="0.0001" name="item_tax_rate_${this.itemCount}" required>
                <button type="button" class="delete-item-btn" data-item-id="${this.itemCount}">Delete</button>
            `;

            // Find the Add Item button and insert the new item before it
            const addItemBtn = this.elements.addItemButton;
            addItemBtn.parentNode.insertBefore(newItem, addItemBtn);

            // Bind delete button event
            const deleteBtn = newItem.querySelector('.delete-item-btn');
            deleteBtn.addEventListener('click', () => this.deleteItem(newItem));
        },
        
        /**
         * Add a new discount row to the form
         */
        addDiscount() {
            this.discountCount++;
            const newDiscount = document.createElement('div');
            newDiscount.classList.add('discount');
            newDiscount.innerHTML = `
                <label for="discount_amount_${this.discountCount}">Discount ${this.discountCount} Amount:</label>
                <input type="number" step="0.0001" name="discount_amount_${this.discountCount}">

                <label for="discount_item_${this.discountCount}">Apply to Item:</label>
                <select name="discount_item_${this.discountCount}">
                    ${Array.from({length: this.itemCount}, (_, i) =>
                        `<option value="${i+1}">Item ${i+1}</option>`
                    ).join('')}
                </select>
                <button type="button" class="delete-discount-btn" data-discount-id="${this.discountCount}">Delete</button>
            `;

            // Find the Add Discount button and insert the new discount before it
            const addDiscountBtn = this.elements.addDiscountButton;
            addDiscountBtn.parentNode.insertBefore(newDiscount, addDiscountBtn);

            // Bind delete button event
            const deleteBtn = newDiscount.querySelector('.delete-discount-btn');
            deleteBtn.addEventListener('click', () => this.deleteDiscount(newDiscount));
        },
        
        /**
         * Delete an item row (must keep at least 1 item)
         * @param {HTMLElement} itemElement - The item element to delete
         */
        deleteItem(itemElement) {
            const itemElements = document.querySelectorAll('.item');
            
            // Cannot delete if only 1 item remains
            if (itemElements.length <= 1) {
                alert('You must have at least one item.');
                return;
            }
            
            itemElement.remove();
        },
        
        /**
         * Delete a discount row (can delete all)
         * @param {HTMLElement} discountElement - The discount element to delete
         */
        deleteDiscount(discountElement) {
            discountElement.remove();
        },
        
        /**
         * Toggle shipping tax rate section visibility
         */
        toggleShippingTaxRate() {
            if (!this.elements.shippingTaxable || !this.elements.shippingTaxRateSection) return;
            
            const shippingTaxable = this.elements.shippingTaxable.value;
            this.elements.shippingTaxRateSection.style.display = shippingTaxable === 'Y' ? 'block' : 'none';
        },
        
        /**
         * Handle form submission
         * @param {Event} event - Submit event
         */
        handleFormSubmit(event) {
            event.preventDefault();
            this.calculateTaxes();
        },
        
        /**
         * Calculate taxes based on form inputs
         */
        calculateTaxes() {
            console.log("Calculating taxes...");
            
            // Get form data
            const items = [];
            let currentItemCount = 0;
            
            // Gather all item inputs
            while (document.querySelector(`input[name="item_price_${currentItemCount + 1}"]`)) {
                currentItemCount++;
                const priceInput = document.querySelector(`input[name="item_price_${currentItemCount}"]`);
                const taxRateInput = document.querySelector(`input[name="item_tax_rate_${currentItemCount}"]`);
                
                if (priceInput && taxRateInput) {
                    items.push({
                        price: parseFloat(priceInput.value) || 0,
                        tax_rate: parseFloat(taxRateInput.value) || 0
                    });
                }
            }
            
            // Gather all discount inputs
            const discounts = [];
            let currentDiscountCount = 0;
            
            while (document.querySelector(`input[name="discount_amount_${currentDiscountCount + 1}"]`)) {
                currentDiscountCount++;
                const discountInput = document.querySelector(`input[name="discount_amount_${currentDiscountCount}"]`);
                const itemIndexInput = document.querySelector(`select[name="discount_item_${currentDiscountCount}"]`);
                
                if (discountInput) {
                    discounts.push({
                        amount: parseFloat(discountInput.value) || 0,
                        item_index: itemIndexInput ? parseInt(itemIndexInput.value) : 1
                    });
                }
            }
            
            // Store the current form state in hidden fields to preserve it
            this.updateHiddenFields(currentItemCount, currentDiscountCount);
            
            // Get shipping inputs
            const shippingCost = parseFloat(document.querySelector('input[name="shipping_cost"]').value) || 0;
            const shippingTaxable = document.querySelector('select[name="shipping_taxable"]').value === 'Y';
            const shippingTaxRate = parseFloat(document.querySelector('input[name="shipping_tax_rate"]').value) || 0;
            
            // Get global settings
            const isSalesBeforeTax = document.querySelector('input[name="is_sales_before_tax"]').checked;
            const discountIsTaxable = document.querySelector('input[name="discount_is_taxable"]').checked;
            
            console.log("Items:", items);
            console.log("Discounts:", discounts);
            console.log("Settings:", { isSalesBeforeTax, discountIsTaxable, shippingCost, shippingTaxable, shippingTaxRate });
            
            // Calculate tax
            const result = this.calculateTax({
                items,
                discounts,
                shipping_cost: shippingCost,
                shipping_taxable: shippingTaxable,
                shipping_tax_rate: shippingTaxRate,
                is_sales_before_tax: isSalesBeforeTax,
                discount_is_taxable: discountIsTaxable
            });
            
            console.log("Result:", result);
            
            // Display results
            this.displayResults(result);
        },
        
        /**
         * Update hidden fields to preserve form state
         * @param {number} itemCount - Current item count
         * @param {number} discountCount - Current discount count
         */
        updateHiddenFields(itemCount, discountCount) {
            // Update item count hidden field
            let formStateField = document.querySelector('input[name="item_count"]');
            if (!formStateField) {
                formStateField = document.createElement('input');
                formStateField.type = 'hidden';
                formStateField.name = 'item_count';
                this.elements.form.appendChild(formStateField);
            }
            formStateField.value = itemCount;
        
            // Update discount count hidden field
            let discountCountField = document.querySelector('input[name="discount_count"]');
            if (!discountCountField) {
                discountCountField = document.createElement('input');
                discountCountField.type = 'hidden';
                discountCountField.name = 'discount_count';
                this.elements.form.appendChild(discountCountField);
            }
            discountCountField.value = discountCount;
        },
        
        /**
         * Calculate tax based on provided data
         * @param {Object} data - Tax calculation data
         * @returns {Object} - Tax calculation results
         */
        calculateTax(data) {
            const items = data.items || [];
            const discounts = data.discounts || [];
            const shippingCost = data.shipping_cost || 0;
            const shippingTaxable = data.shipping_taxable || false;
            const shippingTaxRate = data.shipping_tax_rate || 0;
            const isSalesBeforeTax = data.is_sales_before_tax || false;
            const discountIsTaxable = data.discount_is_taxable || false;
            
            let totalTax = 0;
            let totalAmount = 0;
            let itemTotal = 0;
            let discountTotal = 0;
            let shippingTax = 0;
            let taxBreakdown = [];
            
            // Calculate item totals
            for (const item of items) {
                itemTotal += item.price;
            }
            
            // Calculate discount totals
            for (const discount of discounts) {
                discountTotal += discount.amount;
            }
            
            // Adjust item_total for display in conditions 4 and 5
            let adjustedItemTotal = itemTotal;
            if (isSalesBeforeTax && !discountIsTaxable) {
                adjustedItemTotal = itemTotal - discountTotal;
            }
            
            // Process taxes based on conditions
            if (isSalesBeforeTax) {
                // Conditions 2 or 4
                if (discountIsTaxable) {
                    // Condition 2
                    for (let i = 0; i < items.length; i++) {
                        const item = items[i];
                        const itemDiscounts = discounts.filter(d => d.item_index === i + 1);
                        const itemDiscount = itemDiscounts.reduce((sum, d) => sum + d.amount, 0);
                        
                        const itemTax = (item.price - itemDiscount) * (item.tax_rate / 100);
                        const discountTax = itemDiscount * (item.tax_rate / 100);
                        
                        totalTax += itemTax + discountTax;
                        taxBreakdown.push({
                            item: `Item ${i + 1}`,
                            tax: Math.round(itemTax * 100) / 100
                        });
                        
                        if (itemDiscount > 0) {
                            taxBreakdown.push({
                                item: `Item ${i + 1} Discount`,
                                tax: Math.round(discountTax * 100) / 100
                            });
                        }
                    }
                } else {
                    // Adapted the Condition 4 from test_tools
                    for (let i = 0; i < items.length; i++) {
                        const item = items[i];
                        const itemDiscounts = discounts.filter(d => d.item_index === i + 1);
                        const itemDiscount = itemDiscounts.reduce((sum, d) => sum + d.amount, 0);
                        
                        const itemTax = (item.price - itemDiscount) * (item.tax_rate / 100);
                        
                        totalTax += itemTax;
                        taxBreakdown.push({
                            item: `Item ${i + 1}`,
                            tax: Math.round(itemTax * 100) / 100
                        });
                    }
                }
            } else {
                // Adapted the Conditions 1 or 3 from test_tools
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    const itemTax = item.price * (item.tax_rate / 100);
                    totalTax += itemTax;
                    taxBreakdown.push({
                        item: `Item ${i + 1}`,
                        tax: Math.round(itemTax * 100) / 100
                    });
                    
                    if (discountIsTaxable) {
                        // Adapted the Condition 1 from test_tools
                        const itemDiscounts = discounts.filter(d => d.item_index === i + 1);
                        for (const discount of itemDiscounts) {
                            const discountTax = discount.amount * (item.tax_rate / 100);
                            totalTax += discountTax;
                            taxBreakdown.push({
                                item: `Item ${i + 1} Discount`,
                                tax: Math.round(discountTax * 100) / 100
                            });
                        }
                    }
                }
            }
            
            // Process shipping
            if (shippingCost > 0 && shippingTaxable) {
                shippingTax = shippingCost * (shippingTaxRate / 100);
                totalTax += shippingTax;
                taxBreakdown.push({
                    item: 'Shipping',
                    tax: Math.round(shippingTax * 100) / 100
                });
            }
            
            // Calculate final amount using the correct formula based on conditions
            if (isSalesBeforeTax && !discountIsTaxable) {
                // For conditions 4 and 5
                totalAmount = adjustedItemTotal + totalTax + shippingCost;
            } else {
                // For other conditions
                totalAmount = itemTotal + totalTax + shippingCost - discountTotal;
            }
            
            // Filter out discount breakdowns for non-taxable discounts
            if (!discountIsTaxable) {
                taxBreakdown = taxBreakdown.filter(tb => !tb.item.includes('Discount'));
            }
            
            return {
                item_total: Math.round(adjustedItemTotal * 100) / 100,
                discount_total: Math.round(discountTotal * 100) / 100,
                shipping_cost: Math.round(shippingCost * 100) / 100,
                shipping_tax: Math.round(shippingTax * 100) / 100,
                total_tax: Math.round(totalTax * 100) / 100,
                total_amount: Math.round(totalAmount * 100) / 100,
                tax_breakdown: taxBreakdown
            };
        },
        
        /**
         * Display calculation results
         * @param {Object} result - Tax calculation results
         */
        displayResults(result) {
            // Find or create the result container
            let resultContainer = document.querySelector('.result-container');
            
            // If no container exists, create one
            if (!resultContainer) {
                console.log("Creating result container");
                resultContainer = document.createElement('div');
                resultContainer.className = 'result-container';
                document.querySelector('.tax-calculator').appendChild(resultContainer);
            }
            
            // Generate result HTML
            let html = `
                <h2>Results</h2>
                <p><strong>Item Total:</strong> $${result.item_total.toFixed(2)}</p>
                <p><strong>Discount Total:</strong> $${result.discount_total.toFixed(2)}</p>
                <p><strong>Shipping Cost:</strong> $${result.shipping_cost.toFixed(2)}</p>
                <p><strong>Total Tax:</strong> $${result.total_tax.toFixed(2)}</p>
                <p><strong>Total Amount:</strong> $${result.total_amount.toFixed(2)}</p>
                
                <div class="tax-breakdown">
                    <h3>Tax Breakdown:</h3>
                    <ul>
            `;
            
            for (const tax of result.tax_breakdown) {
                html += `<li>${tax.item}: $${tax.tax.toFixed(2)}</li>`;
            }
            
            html += `
                    </ul>
                </div>
            `;
            
            resultContainer.innerHTML = html;
        }
    };
})();
