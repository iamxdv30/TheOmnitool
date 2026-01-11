from decimal import Decimal, ROUND_HALF_UP, InvalidOperation # decimal module for precise decimal arithmetic typically use for financial calculations

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
    except (ValueError, TypeError, InvalidOperation):
        return Decimal(str(default))

def calculate_tax(price, tax_rate):
    """Calculate tax amount with precise decimal arithmetic"""
    price_dec = Decimal(str(price))
    rate_dec = Decimal(str(tax_rate)) / Decimal('100')
    return price_dec * rate_dec

def validate_vat_rate(vat_rate):
    """
    Validate VAT rate input.

    Args:
        vat_rate: The VAT rate to validate (can be string, int, float, or Decimal)

    Returns:
        Decimal: Validated VAT rate

    Raises:
        ValueError: If VAT rate is invalid (negative, non-numeric, or out of reasonable range)
    """
    try:
        # Try to convert directly to Decimal to catch invalid inputs
        rate = Decimal(str(vat_rate)) if vat_rate not in (None, '') else Decimal('0')

        if rate < Decimal('0'):
            raise ValueError("VAT rate cannot be negative")

        if rate > Decimal('100'):
            raise ValueError("VAT rate cannot exceed 100%")

        return rate
    except (InvalidOperation, ValueError) as e:
        if "VAT rate cannot" in str(e):
            raise
        raise ValueError(f"Invalid VAT rate: must be a numeric value between 0 and 100")
    except TypeError:
        raise ValueError(f"Invalid VAT rate: must be a numeric value between 0 and 100")

def calculate_vat(data):
    """
    Calculate VAT (Value Added Tax) for international markets.

    This function handles VAT-exclusive pricing where tax is calculated on the net price
    and added to get the gross (total) price.

    Args:
        data: A dictionary containing the following keys:
            - items: List of item dictionaries with 'price'
            - vat_rate: The VAT percentage to apply (e.g., 12.00 for Philippines, 20.00 for EU)
            - discounts: (Optional) List of discount dictionaries with 'amount'
            - shipping_cost: (Optional) The cost of shipping
            - shipping_taxable: (Optional) Boolean indicating if shipping is subject to VAT
            - is_sales_before_tax: (Optional) Boolean indicating if discounts are applied before tax calculation
            - discount_is_taxable: (Optional) Boolean indicating if discounts themselves are taxable

    Returns:
        A dictionary containing:
            - net_amount: Total before VAT (items + shipping - discounts)
            - vat_amount: Total VAT charged
            - gross_amount: Total including VAT (net + vat)
            - vat_rate_applied: The VAT rate that was applied
            - item_total: Total amount of items before VAT
            - discount_total: Total amount of discounts
            - shipping_cost: Shipping cost
            - vat_breakdown: List of VAT breakdown items

    Raises:
        ValueError: If vat_rate is invalid

    Example:
        data = {
            'items': [{'price': 100}, {'price': 50}],
            'vat_rate': 12,
            'discounts': [{'amount': 10}],
            'shipping_cost': 5,
            'shipping_taxable': True,
            'is_sales_before_tax': False,
            'discount_is_taxable': True
        }
        result = calculate_vat(data)
        # Returns: {
        #     'net_amount': 145.00,
        #     'vat_amount': 17.40,
        #     'gross_amount': 162.40,
        #     'vat_rate_applied': 12.00,
        #     ...
        # }
    """
    # Validate VAT rate
    vat_rate = validate_vat_rate(data.get('vat_rate', 0))

    # Extract data
    items = data.get('items', [])
    discounts = data.get('discounts', [])
    shipping_cost = safe_decimal(data.get('shipping_cost', 0))
    shipping_taxable = data.get('shipping_taxable', True)  # VAT typically applies to shipping
    is_sales_before_tax = data.get('is_sales_before_tax', False)
    discount_is_taxable = data.get('discount_is_taxable', True)

    # Initialize totals
    item_total = Decimal('0')
    discount_total = Decimal('0')
    net_amount = Decimal('0')
    vat_amount = Decimal('0')
    vat_breakdown = []

    # Calculate item totals
    for item in items:
        price = safe_decimal(item.get('price', 0))
        item_total += price

    # Calculate discount totals
    for discount in discounts:
        discount_total += safe_decimal(discount.get('amount', 0))

    # Calculate VAT based on discount behavior settings
    if is_sales_before_tax:
        # Apply discounts before calculating VAT
        taxable_items_amount = item_total - discount_total
        
        if discount_is_taxable:
            # Condition 2: Discounts applied before tax, but discounts are taxable
            # Tax on (items - discounts) + tax on discounts
            if taxable_items_amount > 0 and vat_rate > 0:
                items_vat = calculate_tax(taxable_items_amount, vat_rate)
                vat_amount += items_vat
                vat_breakdown.append({
                    'item': 'Items',
                    'net_amount': float(taxable_items_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'vat': float(items_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                })
            
            if discount_total > 0 and vat_rate > 0:
                discount_vat = calculate_tax(discount_total, vat_rate)
                vat_amount += discount_vat
                vat_breakdown.append({
                    'item': 'Discounts',
                    'net_amount': float(discount_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'vat': float(discount_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                })
        else:
            # Condition 4: Discounts applied before tax, discounts not taxable
            # Tax only on (items - discounts)
            if taxable_items_amount > 0 and vat_rate > 0:
                items_vat = calculate_tax(taxable_items_amount, vat_rate)
                vat_amount += items_vat
                vat_breakdown.append({
                    'item': 'Items',
                    'net_amount': float(taxable_items_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'vat': float(items_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                })
    else:
        # Apply discounts after calculating VAT
        if discount_is_taxable:
            # Condition 1: Discounts applied after tax, discounts are taxable
            # Tax on items + tax on discounts
            if item_total > 0 and vat_rate > 0:
                items_vat = calculate_tax(item_total, vat_rate)
                vat_amount += items_vat
                vat_breakdown.append({
                    'item': 'Items',
                    'net_amount': float(item_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'vat': float(items_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                })
            
            if discount_total > 0 and vat_rate > 0:
                discount_vat = calculate_tax(discount_total, vat_rate)
                vat_amount += discount_vat
                vat_breakdown.append({
                    'item': 'Discounts',
                    'net_amount': float(discount_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'vat': float(discount_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                })
        else:
            # Condition 3: Discounts applied after tax, discounts not taxable
            # Tax only on items
            if item_total > 0 and vat_rate > 0:
                items_vat = calculate_tax(item_total, vat_rate)
                vat_amount += items_vat
                vat_breakdown.append({
                    'item': 'Items',
                    'net_amount': float(item_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    'vat': float(items_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                })

    # Calculate net amount for display
    if is_sales_before_tax and not discount_is_taxable:
        # For condition 4, net amount is already reduced by discounts
        net_amount = item_total - discount_total
    else:
        # For other conditions, net amount shows items before discounts
        net_amount = item_total - discount_total

    # Add shipping to net amount
    net_amount += shipping_cost

    # Calculate VAT on shipping if applicable
    if shipping_cost > 0 and shipping_taxable and vat_rate > 0:
        shipping_vat = calculate_tax(shipping_cost, vat_rate)
        vat_amount += shipping_vat
        vat_breakdown.append({
            'item': 'Shipping',
            'net_amount': float(shipping_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'vat': float(shipping_vat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        })

    # Calculate gross amount (total including VAT)
    gross_amount = net_amount + vat_amount

    # Return results with proper rounding
    result = {
        'item_total': float(item_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'discount_total': float(discount_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'shipping_cost': float(shipping_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'net_amount': float(net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'vat_amount': float(vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'gross_amount': float(gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'vat_rate_applied': float(vat_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        'vat_breakdown': vat_breakdown
    }

    return result

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
