# Tools/tax_calculator.py

def calculate_tax(price, tax_rate):
    return round(price * (tax_rate / 100), 3)

def process_discount(discount_items):
    discount_total = 0
    for item in discount_items:
        price = item['price']
        is_taxable = item['is_taxable']
        tax_rate = item.get('tax_rate', 0)
        if is_taxable:
            discount_total += calculate_tax(price, tax_rate)
        else:
            discount_total += price
    return discount_total

def tax_calculator(data):
    item_count = int(data.get('item_count', 0))
    items = []
    total_tax = 0
    total_amount = 0
    taxes = []

    # Process discount items if any
    discount_items = data.get('discount_items', [])
    discount_total = process_discount(discount_items)

    # Process line items
    for i in range(1, item_count + 1):
        price = float(data.get(f'item_price_{i}', 0))
        tax_rate = float(data.get(f'item_tax_rate_{i}', 0))
        tax = calculate_tax(price, tax_rate)
        total_tax += tax
        total_amount += round(price + tax, 3)
        taxes.append({'item': i, 'tax': tax})
        items.append({'item': i, 'price': price, 'tax_rate': tax_rate, 'tax': tax})

    # Process shipping cost if any
    shipping_cost = float(data.get('shipping_cost', 0))
    shipping_tax = 0
    if shipping_cost > 0:
        shipping_taxable = data.get('shipping_taxable', 'N') == 'Y'
        if shipping_taxable:
            shipping_tax_rate = float(data.get('shipping_tax_rate', 0))
            shipping_tax = calculate_tax(shipping_cost, shipping_tax_rate)
            shipping_total = shipping_cost + shipping_tax
        else:
            shipping_total = shipping_cost
    else:
        shipping_total = 0

    total_tax += shipping_tax
    total_amount += shipping_total - discount_total

    result = {
        'items': items,
        'discount_total': discount_total,
        'shipping_cost': shipping_cost,
        'shipping_tax': shipping_tax,
        'total_tax': total_tax,
        'total_amount': total_amount,
        'tax_breakdown': taxes,
        'item_total': total_amount - shipping_total - total_tax + discount_total,
    }

    return result
