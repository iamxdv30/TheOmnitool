import json

def get_float_input(prompt: str) -> float:
    """
    Get a float input from the user.
    
    Args:
        prompt: The prompt to display to the user.
    
    Returns:
        A float value entered by the user.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def get_yes_no_input(prompt: str) -> bool:
    """
    Get a yes/no input from the user.
    
    Args:
        prompt: The prompt to display to the user.
    
    Returns:
        A boolean value (True for yes, False for no).
    """
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'Y' or 'N'.")

def get_shipping_province():
    """
    Get the shipping province code from the user.
    
    Returns:
        A string representing the province code.
    """
    provinces = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']
    while True:
        province = input("Enter the shipping province code (e.g., ON for Ontario): ").upper()
        if province in provinces:
            return province
        print("Invalid province code. Please try again.")

def get_tax_structure(province):
    """
    Get the tax structure for a given province.
    
    Args:
        province: The province code.
    
    Returns:
        A dictionary containing the tax structure.
    """
    tax_structure = {
        'ON': {'type': 'HST', 'rates': ['HST']},
        'BC': {'type': 'GST_PST', 'rates': ['GST', 'PST']},
        'AB': {'type': 'GST', 'rates': ['GST']},
        'MB': {'type': 'GST_PST', 'rates': ['GST', 'PST']},
        'NB': {'type': 'HST', 'rates': ['HST']},
        'NL': {'type': 'HST', 'rates': ['HST']},
        'NS': {'type': 'HST', 'rates': ['HST']},
        'NT': {'type': 'GST', 'rates': ['GST']},
        'NU': {'type': 'GST', 'rates': ['GST']},
        'PE': {'type': 'HST', 'rates': ['HST']},
        'QC': {'type': 'GST_QST', 'rates': ['GST', 'QST']},
        'SK': {'type': 'GST_PST', 'rates': ['GST', 'PST']},
        'YT': {'type': 'GST', 'rates': ['GST']},
    }
    return tax_structure.get(province)

def get_tax_rates(tax_structure):
    """
    Get the tax rates for a given tax structure.
    
    Args:
        tax_structure: The tax structure dictionary.
    
    Returns:
        A dictionary containing the tax rates.
    """
    rates = {}
    if 'HST' in tax_structure['rates']:
        rates['HST'] = get_float_input("Enter HST rate (%): ")
    elif 'GST' in tax_structure['rates']:
        rates['GST'] = get_float_input("Enter GST rate (%): ")
        if tax_structure['type'] in ['GST_PST', 'GST_QST']:
            rate_name = 'PST' if tax_structure['type'] == 'GST_PST' else 'QST'
            rates[rate_name] = get_float_input(f"Enter {rate_name} rate (%): ")
    return rates

def calculate_tax(items, tax_rates, shipping_cost, shipping_taxable, is_sales_before_tax=False, discount_taxable=True):
    """
    Calculate tax based on provided data.
    
    Args:
        items: A list of item dictionaries with 'price' and 'discount' keys.
        tax_rates: A dictionary containing the tax rates.
        shipping_cost: The cost of shipping.
        shipping_taxable: Boolean indicating if shipping is taxable.
        is_sales_before_tax: Boolean indicating if sales tax is applied before discounts.
        discount_taxable: Boolean indicating if discounts are taxable.
    
    Returns:
        A dictionary containing the following keys:
            - total_tax: Total tax amount
            - total_amount: Total amount including tax
            - item_total: Total amount of items
            - discount_total: Total amount of discounts
            - shipping_tax: Tax amount on shipping
            - tax_breakdown: Dictionary containing tax breakdown for each item
    """
    order_total = 0
    item_total = 0
    tax_total = 0
    discount_total = 0
    tax_breakdown = {}

    # Calculate item totals and discount totals
    for i, item in enumerate(items, 1):
        item_price = item['price']
        item_total += item_price
        
        # Track discount total
        if 'discount' in item:
            discount = item['discount']
            discount_total += discount
    
    # Adjust item_total for conditions 4 and 5
    adjusted_item_total = item_total
    if is_sales_before_tax and not discount_taxable:
        adjusted_item_total -= discount_total

    # Calculate taxes based on conditions
    for i, item in enumerate(items, 1):
        item_price = item['price']
        
        # Calculate taxable amount based on global settings
        if 'discount' in item:
            discount = item['discount']
            
            if is_sales_before_tax:
                # Apply discount before calculating tax
                taxable_amount = item_price - discount
            else:
                # When not calculating tax on sales before discount
                taxable_amount = item_price
                
                # Skip tax on discount if applicable
                if not discount_taxable:
                    # Don't include discount in tax calculation
                    taxable_amount = item_price
        else:
            taxable_amount = item_price

        item_tax = 0
        tax_breakdown[f'item{i}'] = {}
        for tax_type, rate in tax_rates.items():
            tax_amount = taxable_amount * rate / 100
            item_tax += tax_amount
            tax_breakdown[f'item{i}'][f"{tax_type}_amount"] = round(tax_amount, 4)

        tax_total += item_tax

    # Handle shipping tax
    shipping_tax = 0
    if shipping_taxable:
        for tax_type, rate in tax_rates.items():
            tax_amount = shipping_cost * rate / 100
            shipping_tax += tax_amount
            tax_breakdown['shipping'] = {f"{tax_type}_amount": round(tax_amount, 4)}
        tax_total += shipping_tax

    # Calculate final amount with special handling for conditions 4 and 5
    if is_sales_before_tax and not discount_taxable:
        # For conditions 4 and 5
        order_total = adjusted_item_total + tax_total + shipping_cost
    else:
        # Standard calculation for other conditions
        order_total = item_total + tax_total + shipping_cost - discount_total

    return {
        "orderTotal": round(order_total, 2),
        "itemTotal": round(adjusted_item_total, 2),  # Use adjusted item total for display
        "taxTotal": round(tax_total, 2),
        "shippingCost": round(shipping_cost, 2),
        "shippingTax": round(shipping_tax, 2),
        "discountTotal": round(discount_total, 2),
        "taxBreakdown": tax_breakdown
    }
