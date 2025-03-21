from decimal import Decimal, ROUND_HALF_UP

def calculate_tax(price, tax_rate):
    """Calculate tax amount with precise decimal arithmetic"""
    price_dec = Decimal(str(price))
    rate_dec = Decimal(str(tax_rate)) / Decimal('100')
    return price_dec * rate_dec

def tax_calculator(data):
    # Convert inputs to Decimal
    items = data.get('items', [])
    discounts = data.get('discounts', [])
    shipping_cost = Decimal(str(data.get('shipping_cost', 0)))
    shipping_taxable = data.get('shipping_taxable', False)
    shipping_tax_rate = Decimal(str(data.get('shipping_tax_rate', 0)))
    is_sales_before_tax = data.get('is_sales_before_tax', False)
    discount_is_taxable = data.get('discount_is_taxable', True)

    total_tax = Decimal('0')
    total_amount = Decimal('0')
    item_total = Decimal('0')
    discount_total = Decimal('0')
    shipping_tax = Decimal('0')
    tax_breakdown = []

    # Calculate item totals
    for i, item in enumerate(items, 1):
        price = Decimal(str(item['price']))
        tax_rate = Decimal(str(item['tax_rate']))
        item_total += price

    # Calculate discount totals
    for discount in discounts:
        discount_total += Decimal(str(discount['amount']))

    # Process taxes based on conditions
    if is_sales_before_tax:
        # Conditions 2 or 4
        if discount_is_taxable:
            # Condition 2
            for i, item in enumerate(items, 1):
                price = Decimal(str(item['price']))
                tax_rate = Decimal(str(item['tax_rate']))
                
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                item_discount = sum(Decimal(str(d['amount'])) for d in item_discounts)
                
                item_tax = calculate_tax(price - item_discount, tax_rate)
                discount_tax = calculate_tax(item_discount, tax_rate)
                
                total_tax += item_tax + discount_tax
                tax_breakdown.append({'item': f'Item {i}', 'tax': float(item_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
                if item_discount > 0:
                    tax_breakdown.append({'item': f'Item {i} Discount', 'tax': float(discount_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
        else:
            # Condition 4
            for i, item in enumerate(items, 1):
                price = Decimal(str(item['price']))
                tax_rate = Decimal(str(item['tax_rate']))
                
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                item_discount = sum(Decimal(str(d['amount'])) for d in item_discounts)
                
                item_tax = calculate_tax(price - item_discount, tax_rate)
                
                total_tax += item_tax
                tax_breakdown.append({'item': f'Item {i}', 'tax': float(item_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
    else:
        # Conditions 1 or 3
        for i, item in enumerate(items, 1):
            price = Decimal(str(item['price']))
            tax_rate = Decimal(str(item['tax_rate']))
            
            item_tax = calculate_tax(price, tax_rate)
            total_tax += item_tax
            tax_breakdown.append({'item': f'Item {i}', 'tax': float(item_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
            
            if discount_is_taxable:
                # Condition 1
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                for discount in item_discounts:
                    discount_tax = calculate_tax(Decimal(str(discount['amount'])), tax_rate)
                    total_tax += discount_tax
                    tax_breakdown.append({'item': f'Item {i} Discount', 'tax': float(discount_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})

    # Process shipping
    if shipping_cost > 0 and shipping_taxable:
        shipping_tax = calculate_tax(shipping_cost, shipping_tax_rate)
        total_tax += shipping_tax
        tax_breakdown.append({'item': 'Shipping', 'tax': float(shipping_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
    
    # Calculate final amount
    total_amount = item_total + total_tax + shipping_cost - discount_total
    
    if not discount_is_taxable:
        tax_breakdown = [tb for tb in tax_breakdown if 'Discount' not in tb['item']]

    # Round properly with Decimal
    result = {
        'item_total': float(item_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'discount_total': float(discount_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'shipping_cost': float(shipping_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'shipping_tax': float(shipping_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'total_tax': float(total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'total_amount': float(total_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'tax_breakdown': tax_breakdown
    }

    return result