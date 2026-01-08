/**
 * canada_tax_calculator.js - Canadian Tax Calculator functionality
 * Handles Canadian tax calculation logic, form interactions, and result display
 */
(function() {
    'use strict';

    const CanadaTaxCalculator = {
        // Tax structure by province
        taxStructure: {
            ON: { type: 'HST', rates: ['HST'] },
            BC: { type: 'GST_PST', rates: ['GST', 'PST'] },
            AB: { type: 'GST', rates: ['GST'] },
            MB: { type: 'GST_PST', rates: ['GST', 'PST'] },
            NB: { type: 'HST', rates: ['HST'] },
            NL: { type: 'HST', rates: ['HST'] },
            NS: { type: 'HST', rates: ['HST'] },
            NT: { type: 'GST', rates: ['GST'] },
            NU: { type: 'GST', rates: ['GST'] },
            PE: { type: 'HST', rates: ['HST'] },
            QC: { type: 'GST_QST', rates: ['GST', 'QST'] },
            SK: { type: 'GST_PST', rates: ['GST', 'PST'] },
            YT: { type: 'GST', rates: ['GST'] },
        },
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.initializeForm();
        },
        
        cacheElements() {
            this.elements = {
                country: document.getElementById('country'),
                province: document.getElementById('province'),
                taxRates: document.getElementById('taxRates'),
                itemsContainer: document.getElementById('itemsContainer'),
                addItemBtn: document.getElementById('addItemBtn'),
                calculateTaxBtn: document.getElementById('calculateTaxBtn'),
                shippingCost: document.getElementById('shippingCost'),
                shippingTaxable: document.getElementById('shippingTaxable'),
                isSalesBeforeTax: document.getElementById('isSalesBeforeTax'),
                discountTaxable: document.getElementById('discountTaxable'),
                container: document.querySelector('.ca-container')
            };
        },
        
        bindEvents() {
            if (this.elements.province) {
                this.elements.province.addEventListener('change', this.updateTaxRates.bind(this));
            }
            
            if (this.elements.country) {
                this.elements.country.addEventListener('change', this.selectTaxCalculator.bind(this));
            }
            
            if (this.elements.addItemBtn) {
                this.elements.addItemBtn.addEventListener('click', this.addItem.bind(this));
            }
            
            if (this.elements.calculateTaxBtn) {
                this.elements.calculateTaxBtn.addEventListener('click', this.calculateTax.bind(this));
            }
        },
        
        initializeForm() {
            this.updateTaxRates();
            this.addItem(false); // First item should not have delete button
        },
        
        updateTaxRates() {
            const province = this.elements.province.value;
            this.elements.taxRates.innerHTML = '';
            
            if (province) {
                const rates = this.taxStructure[province].rates;
                const fragment = document.createDocumentFragment();

                rates.forEach((rate) => {
                    const div = document.createElement('div');
                    div.className = 'form-group ca-tax-rate-field';
                    let defaultValue = '5'; // Default for GST
                    if (rate === 'HST') {
                        defaultValue = '13';
                    } else if (rate === 'PST') {
                        defaultValue = '7';
                    } else if (rate === 'QST') {
                        defaultValue = '9.975';
                    }

                    div.innerHTML = `
                        <label for="${rate.toLowerCase()}Rate">${rate} Rate (%):</label>
                        <input type="number" id="${rate.toLowerCase()}Rate" class="tax-rate-input" step="0.01" min="0" max="100" value="${defaultValue}" required>
                    `;
                    fragment.appendChild(div);
                });
                this.elements.taxRates.appendChild(fragment);
            }
        },
        
        selectTaxCalculator() {
            const country = this.elements.country.value;
            if (country === 'US') {
                window.location.href = this.elements.country.dataset.usCalculatorUrl;
            } else if (country === 'CA') {
                window.location.href = this.elements.country.dataset.caCalculatorUrl;
            }
        },
        
        addItem(includeDeleteButton = true) {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'item';
            
            let deleteButtonHtml = '';
            if (includeDeleteButton) {
                deleteButtonHtml = '<button type="button" class="delete-ca-item-btn">Delete</button>';
            }
            
            itemDiv.innerHTML = `
                <div class="form-group">
                    <label>Item Price ($):</label>
                    <input type="number" class="itemPrice" step="0.01" min="0" value="0.00" required>
                </div>
                <div class="form-group">
                    <label>Discount Amount ($):</label>
                    <input type="number" class="discountAmount" step="0.01" min="0" value="0.00" required>
                </div>
                ${deleteButtonHtml}
            `;
            this.elements.itemsContainer.appendChild(itemDiv);
            
            // Bind delete button event only if button exists
            if (includeDeleteButton) {
                const deleteBtn = itemDiv.querySelector('.delete-ca-item-btn');
                deleteBtn.addEventListener('click', () => this.deleteItem(itemDiv));
            }
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
        
        calculateTax() {
            const province = this.elements.province.value;
            if (!province) return;

            const taxRates = {};
            
            this.taxStructure[province].rates.forEach((rate) => {
                const input = document.getElementById(rate.toLowerCase() + 'Rate');
                if (input) {
                    taxRates[rate] = parseFloat(input.value);
                }
            });
            
            const items = Array.from(document.querySelectorAll('.item')).map(
                (itemDiv) => ({
                    price: parseFloat(itemDiv.querySelector('.itemPrice').value) || 0,
                    discount: parseFloat(itemDiv.querySelector('.discountAmount').value) || 0
                })
            );
            
            const shippingCost = parseFloat(this.elements.shippingCost.value) || 0;
            const shippingTaxable = this.elements.shippingTaxable.checked;
            const isSalesBeforeTax = this.elements.isSalesBeforeTax.checked;
            const discountTaxable = this.elements.discountTaxable.checked;
            
            const result = this.calculateTaxResult(
                items,
                taxRates,
                shippingCost,
                shippingTaxable,
                isSalesBeforeTax,
                discountTaxable
            );
            
            this.displayResults(result);
        },
        
        calculateTaxResult(items, taxRates, shippingCost, shippingTaxable, isSalesBeforeTax, discountTaxable) {
            let orderTotal = 0;
            let itemTotal = 0;
            let taxTotal = 0;
            let discountTotal = 0;
            let taxBreakdown = {};
            
            items.forEach((item) => {
                itemTotal += item.price;
                if (item.discount > 0) {
                    discountTotal += item.discount;
                }
            });
            
            let adjustedItemTotal = itemTotal;
            if (isSalesBeforeTax && !discountTaxable) {
                adjustedItemTotal = itemTotal - discountTotal;
            }
            
            items.forEach((item, index) => {
                let taxableAmount = item.price;
                
                if (item.discount > 0) {
                    if (isSalesBeforeTax) {
                        taxableAmount = item.price - item.discount;
                    }
                }
                
                let itemTax = 0;
                taxBreakdown[`item${index + 1}`] = {};
                
                for (const [taxType, rate] of Object.entries(taxRates)) {
                    if (isNaN(rate)) continue;
                    const taxAmount = (taxableAmount * rate) / 100;
                    itemTax += taxAmount;
                    taxBreakdown[`item${index + 1}`][`${taxType}_amount`] = Math.round(taxAmount * 10000) / 10000;
                }
                taxTotal += itemTax;
            });
            
            let shippingTax = 0;
            if (shippingTaxable) {
                taxBreakdown['shipping'] = {};
                for (const [taxType, rate] of Object.entries(taxRates)) {
                     if (isNaN(rate)) continue;
                    const taxAmount = (shippingCost * rate) / 100;
                    shippingTax += taxAmount;
                    taxBreakdown['shipping'][`${taxType}_amount`] = Math.round(taxAmount * 10000) / 10000;
                }
                taxTotal += shippingTax;
            }
            
            if (isSalesBeforeTax && !discountTaxable) {
                orderTotal = adjustedItemTotal + taxTotal + shippingCost;
            } else {
                orderTotal = itemTotal + taxTotal + shippingCost - discountTotal;
            }
            
            return {
                orderTotal: Math.round(orderTotal * 100) / 100,
                itemTotal: Math.round(adjustedItemTotal * 100) / 100,
                taxTotal: Math.round(taxTotal * 100) / 100,
                shippingCost: Math.round(shippingCost * 100) / 100,
                shippingTax: Math.round(shippingTax * 100) / 100,
                discountTotal: Math.round(discountTotal * 100) / 100,
                taxBreakdown: taxBreakdown,
            };
        },
        
        displayResults(result) {
            let resultsDiv = document.getElementById('results');
            if (!resultsDiv) {
                resultsDiv = document.createElement('div');
                resultsDiv.id = 'results';
                this.elements.container.appendChild(resultsDiv);
            }
            
            resultsDiv.innerHTML = `
                <h2>Calculation Results:</h2>
                <p>Order Total: $${result.orderTotal.toFixed(2)}</p>
                <p>Item Total: $${result.itemTotal.toFixed(2)}</p>
                <p>Tax Total: $${result.taxTotal.toFixed(2)}</p>
                <p>Shipping Cost: $${result.shippingCost.toFixed(2)}</p>
                <p>Shipping Tax: $${result.shippingTax.toFixed(2)}</p>
                <p>Discount Total: $${result.discountTotal.toFixed(2)}</p>
                <h3>Tax Breakdown:</h3>
                ${Object.entries(result.taxBreakdown)
                    .map(
                        ([itemKey, taxes]) => `
                    <p>${itemKey === 'shipping' ? 'Shipping' : `Item ${itemKey.slice(4)}`} Taxes:</p>
                    <ul>
                        ${Object.entries(taxes)
                            .map(
                                ([taxType, amount]) => `
                            <li>${taxType.toUpperCase().replace('_AMOUNT', '')}: $${amount.toFixed(2)}</li>
                        `
                            )
                            .join('')}
                    </ul>
                `
                    )
                    .join('')}
            `;
        }
    };

    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        CanadaTaxCalculator.init();
    });
})();
