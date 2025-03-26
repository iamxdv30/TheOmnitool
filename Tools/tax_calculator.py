from decimal import Decimal, ROUND_HALF_UP # decimal module for precise decimal arithmetic typically use for financial calculations

def safe_decimal(value, default=0):
    """
    Safely convert a value to a Decimal.
    
    Args:
        value: The value to convert to a Decimal.
        default: The default value to use if conversion fails.
    
    Returns:
        A Decimal representation of the value or the default value.
    """
    try:
        return Decimal(str(value or default))
    except (ValueError, TypeError):
        return Decimal(str(default))

def calculate_tax(price, tax_rate):
    """Calculate tax amount with precise decimal arithmetic"""
    price_dec = Decimal(str(price))
    rate_dec = Decimal(str(tax_rate)) / Decimal('100')
    return price_dec * rate_dec

def tax_calculator(data):
    """
    Calculate tax based on provided data.
    
    Args:
        data: A dictionary containing the following keys:
            - items: List of item dictionaries with 'price' and 'tax_rate'
            - discounts: List of discount dictionaries with 'amount' and 'item_index'
            - shipping_cost: The cost of shipping
            - shipping_taxable: Boolean indicating if shipping is taxable
            - shipping_tax_rate: Tax rate for shipping
            - is_sales_before_tax: Boolean indicating if sales tax is applied before discounts
            - discount_is_taxable: Boolean indicating if discounts are taxable
    
    Returns:
        A dictionary containing the following keys:
            - total_tax: Total tax amount
            - total_amount: Total amount including tax
            - item_total: Total amount of items
            - discount_total: Total amount of discounts
            - shipping_tax: Tax amount on shipping
            - tax_breakdown: List of tax breakdown items
    """
    # Extract data from request
    items = data.get('items', [])
    discounts = data.get('discounts', [])
    shipping_cost = safe_decimal(data.get('shipping_cost'))
    shipping_taxable = data.get('shipping_taxable', False)
    shipping_tax_rate = safe_decimal(data.get('shipping_tax_rate'))
    is_sales_before_tax = data.get('is_sales_before_tax', False)
    discount_is_taxable = data.get('discount_is_taxable', True)

    total_tax = Decimal('0')
    total_amount = Decimal('0')
    item_total = Decimal('0')
    discount_total = Decimal('0')
    shipping_tax = Decimal('0')
    tax_breakdown = []

    # Validate shipping tax rate
    if shipping_cost > 0 and shipping_taxable and shipping_tax_rate == Decimal('0'):
        raise ValueError("Shipping is marked as taxable but no tax rate provided. Please enter a shipping tax rate.")
    
    # Initialize total tax
    total_tax = Decimal('0')

    # Calculate item totals
    for i, item in enumerate(items, 1):
        price = safe_decimal(item['price'])
        tax_rate = safe_decimal(item['tax_rate'])
        item_total += price

    # Calculate discount totals
    for discount in discounts:
        discount_total += safe_decimal(discount['amount'])

    # Subtract discounts from item_total for conditions 4 and 5
    if is_sales_before_tax and not discount_is_taxable:
        item_total -= discount_total

    # Process taxes based on conditions of is_sales_before_tax and discount_is_taxable
    if is_sales_before_tax:
        # Conditions 2 or 4 are both is_sales_before_tax is True
        if discount_is_taxable:
            # Condition 2 (When discount_is_taxable is True and is_sales_before_tax is True)
            for i, item in enumerate(items, 1):
                price = safe_decimal(item['price'])
                tax_rate = safe_decimal(item['tax_rate'])
                
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                item_discount = sum(safe_decimal(d['amount']) for d in item_discounts)
                
                item_tax = calculate_tax(price - item_discount, tax_rate)
                discount_tax = calculate_tax(item_discount, tax_rate)
                
                total_tax += item_tax + discount_tax
                tax_breakdown.append({'item': f'Item {i}', 'tax': float(item_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
                if item_discount > 0:
                    tax_breakdown.append({'item': f'Item {i} Discount', 'tax': float(discount_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
        else:
            # Condition 4 (When discount_is_taxable is False and is_sales_before_tax is True)
            for i, item in enumerate(items, 1):
                price = safe_decimal(item['price'])
                tax_rate = safe_decimal(item['tax_rate'])
                
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                item_discount = sum(safe_decimal(d['amount']) for d in item_discounts)
                
                item_tax = calculate_tax(price - item_discount, tax_rate)
                
                total_tax += item_tax
                tax_breakdown.append({'item': f'Item {i}', 'tax': float(item_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
    else:
        # Conditions 1 or 3 are both is_sales_before_tax is False
        for i, item in enumerate(items, 1):
            price = safe_decimal(item['price'])
            tax_rate = safe_decimal(item['tax_rate'])
            
            item_tax = calculate_tax(price, tax_rate)
            total_tax += item_tax
            tax_breakdown.append({'item': f'Item {i}', 'tax': float(item_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
            
            if discount_is_taxable:
                # Condition 1 (When discount_is_taxable is True and is_sales_before_tax is False)
                item_discounts = [d for d in discounts if d.get('item_index') == i]
                for discount in item_discounts:
                    discount_tax = calculate_tax(safe_decimal(discount['amount']), tax_rate)
                    total_tax += discount_tax
                    tax_breakdown.append({'item': f'Item {i} Discount', 'tax': float(discount_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})

    # Process shipping
    if shipping_cost > 0 and shipping_taxable:
        shipping_tax = calculate_tax(shipping_cost, shipping_tax_rate)
        total_tax += shipping_tax
        tax_breakdown.append({'item': 'Shipping', 'tax': float(shipping_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))})
    
    # Calculate final amount for case: is_sales_before_tax is True and discount_is_taxable is False
    if is_sales_before_tax and not discount_is_taxable:
        total_amount = item_total + total_tax + shipping_cost
    else:
        total_amount = item_total + total_tax + shipping_cost - discount_total
    
    if not discount_is_taxable:
        tax_breakdown = [tb for tb in tax_breakdown if 'Discount' not in tb['item']]

    # Round properly with Decimal module for accuracy
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