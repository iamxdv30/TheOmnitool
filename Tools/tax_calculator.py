# Tools/tax_calculator.py

def calculate_tax(price, tax_rate):
    return round(price * (tax_rate / 100), 2)

def process_discount(discounts, base_tax_rate):
    discount_total = 0
    discount_tax = 0
    for discount in discounts:
        amount = discount['amount']
        is_taxable = discount['is_taxable']
        discount_total += amount
        if is_taxable:
            discount_tax += calculate_tax(amount, base_tax_rate)
    return discount_total, discount_tax

def tax_calculator(data):
    items = data.get('items', [])
    discounts = data.get('discounts', [])
    shipping_cost = data.get('shipping_cost', '')
    shipping_cost = float(shipping_cost) if shipping_cost else 0
    shipping_taxable = data.get('shipping_taxable', False)
    shipping_tax_rate = data.get('shipping_tax_rate', '')
    shipping_tax_rate = float(shipping_tax_rate) if shipping_tax_rate else 0

    total_tax = 0
    total_amount = 0
    item_total = 0
    tax_breakdown = []

    # Process line items
    for i, item in enumerate(items, 1):
        price = item['price']
        tax_rate = item['tax_rate']
        item_total += price
        tax = calculate_tax(price, tax_rate)
        total_tax += tax
        total_amount += price + tax
        tax_breakdown.append({'item': f'Item {i}', 'tax': tax})

    # Process discounts
    base_tax_rate = items[0]['tax_rate'] if items else 0  # Use the first item's tax rate for discounts
    discount_total, discount_tax = process_discount(discounts, base_tax_rate)
    total_amount -= discount_total
    total_tax -= discount_tax
    if discount_total > 0:
        tax_breakdown.append({'item': 'Discount', 'tax': -discount_tax})

    # Process shipping cost
    shipping_tax = 0
    if shipping_cost > 0 and shipping_taxable:
        shipping_tax = calculate_tax(shipping_cost, shipping_tax_rate)
        total_tax += shipping_tax
        tax_breakdown.append({'item': 'Shipping', 'tax': shipping_tax})
    
    total_amount += shipping_cost + shipping_tax

    result = {
        'items': items,
        'item_total': round(item_total, 2),
        'discount_total': round(discount_total, 2),
        'shipping_cost': round(shipping_cost, 2),
        'shipping_tax': round(shipping_tax, 2),
        'total_tax': round(total_tax, 2),
        'total_amount': round(total_amount, 2),
        'tax_breakdown': tax_breakdown
    }

    return result
