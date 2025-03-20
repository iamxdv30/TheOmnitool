def calculate_tax(price, tax_rate):
    """
    Calculate tax amount based on price and tax rate
    
    Args:
        price (float): The price amount
        tax_rate (float): The tax rate percentage
        
    Returns:
        float: The calculated tax amount
    """
    return round(price * (tax_rate / 100), 2)

def tax_calculator(data):
    """
    Calculate taxes for items with various conditions
    
    Args:
        data (dict): Dictionary containing:
            - items: List of dictionaries with price and tax_rate
            - discounts: List of discount information
            - shipping_cost: Cost of shipping
            - shipping_taxable: Whether shipping is taxable
            - shipping_tax_rate: Tax rate for shipping
            - is_sales_before_tax: Whether sales are taxed after or before discount
            - discount_is_taxable: Whether discounts are taxable
            
    Returns:
        dict: Dictionary with tax calculation results
    """
    items = data.get('items', [])
    discounts = data.get('discounts', [])
    shipping_cost = float(data.get('shipping_cost', 0))
    shipping_taxable = data.get('shipping_taxable', False)
    shipping_tax_rate = float(data.get('shipping_tax_rate', 0))
    is_sales_before_tax = data.get('is_sales_before_tax', False)
    discount_is_taxable = data.get('discount_is_taxable', False)

    total_tax = 0
    total_amount = 0
    item_total = 0
    discount_total = 0
    shipping_tax = 0
    tax_breakdown = []

    # Calculate item totals
    for i, item in enumerate(items, 1):
        price = item['price']
        tax_rate = item['tax_rate']
        item_total += price

    # Calculate discount totals
    for discount in discounts:
        discount_total += discount['amount']

    # Process taxes based on conditions
    if is_sales_before_tax:
        # Condition 2 or 4: Prices before tax
        if discount_is_taxable:
            # Condition 2: Prices before tax, discount taxable
            for i, item in enumerate(items, 1):
                price = item['price']
                tax_rate = item['tax_rate']
                
                # Find discounts for this item
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                item_discount = sum(d['amount'] for d in item_discounts)
                
                # Calculate tax on item price minus discount
                item_tax = calculate_tax(price - item_discount, tax_rate)
                
                # Add discount tax (since discount is taxable)
                discount_tax = calculate_tax(item_discount, tax_rate)
                
                total_tax += item_tax + discount_tax
                tax_breakdown.append({'item': f'Item {i}', 'tax': item_tax})
                if item_discount > 0:
                    tax_breakdown.append({'item': f'Item {i} Discount', 'tax': discount_tax})
        else:
            # Condition 4: Prices before tax, discount not taxable
            for i, item in enumerate(items, 1):
                price = item['price']
                tax_rate = item['tax_rate']
                
                # Find discounts for this item
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                item_discount = sum(d['amount'] for d in item_discounts)
                
                # Calculate tax on item price minus discount
                item_tax = calculate_tax(price - item_discount, tax_rate)
                
                total_tax += item_tax
                tax_breakdown.append({'item': f'Item {i}', 'tax': item_tax})
    else:
        # Condition 1 or 3: Prices after tax
        for i, item in enumerate(items, 1):
            price = item['price']
            tax_rate = item['tax_rate']
            
            # Calculate item tax
            item_tax = calculate_tax(price, tax_rate)
            total_tax += item_tax
            tax_breakdown.append({'item': f'Item {i}', 'tax': item_tax})
            
            if discount_is_taxable:
                # Condition 1: Prices after tax, discount taxable
                # Find discounts for this item
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                for discount in item_discounts:
                    discount_tax = calculate_tax(discount['amount'], tax_rate)
                    total_tax += discount_tax
                    tax_breakdown.append({'item': f'Item {i} Discount', 'tax': discount_tax})

    # Process shipping cost and tax
    if shipping_cost > 0 and shipping_taxable:
        shipping_tax = calculate_tax(shipping_cost, shipping_tax_rate)
        total_tax += shipping_tax
        tax_breakdown.append({'item': 'Shipping', 'tax': shipping_tax})
    
    # Calculate final amount
    total_amount = item_total + total_tax + shipping_cost - discount_total
    
    # Fix tax breakdown to match expected structure
    # For conditions with no discount tax, ensure we don't include it
    if not discount_is_taxable:
        tax_breakdown = [tb for tb in tax_breakdown if 'Discount' not in tb['item']]

    result = {
        'item_total': round(item_total, 2),
        'discount_total': round(discount_total, 2),
        'shipping_cost': round(shipping_cost, 2),
        'shipping_tax': round(shipping_tax, 2),
        'total_tax': round(total_tax, 2),
        'total_amount': round(total_amount, 2),
        'tax_breakdown': tax_breakdown
    }

    return result