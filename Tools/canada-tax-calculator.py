import json

def get_float_input(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

def get_yes_no_input(prompt: str) -> bool:
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'Y' or 'N'.")

def get_shipping_province():
    provinces = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']
    while True:
        province = input("Enter the shipping province code (e.g., ON for Ontario): ").upper()
        if province in provinces:
            return province
        print("Invalid province code. Please try again.")

def get_tax_structure(province):
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
    rates = {}
    if 'HST' in tax_structure['rates']:
        rates['HST'] = get_float_input("Enter HST rate (%): ")
    elif 'GST' in tax_structure['rates']:
        rates['GST'] = get_float_input("Enter GST rate (%): ")
        if tax_structure['type'] in ['GST_PST', 'GST_QST']:
            rate_name = 'PST' if tax_structure['type'] == 'GST_PST' else 'QST'
            rates[rate_name] = get_float_input(f"Enter {rate_name} rate (%): ")
    return rates

def calculate_tax(items, tax_rates, shipping_cost, shipping_taxable):
    order_total = 0
    item_total = 0
    tax_total = 0
    discount_total = 0
    tax_breakdown = {}

    for i, item in enumerate(items, 1):
        item_price = item['price']
        item_total += item_price

        if 'discount' in item:
            discount = item['discount']
            discount_total += discount
            taxable_amount = item_price - discount if item['discount_taxable'] else item_price
        else:
            taxable_amount = item_price

        item_tax = 0
        tax_breakdown[f'item{i}'] = {}
        for tax_type, rate in tax_rates.items():
            tax_amount = taxable_amount * rate / 100
            item_tax += tax_amount
            tax_breakdown[f'item{i}'][f"{tax_type}_amount"] = round(tax_amount, 4)

        tax_total += item_tax

    if shipping_taxable:
        shipping_tax = 0
        for tax_type, rate in tax_rates.items():
            tax_amount = shipping_cost * rate / 100
            shipping_tax += tax_amount
            tax_breakdown['shipping'] = {f"{tax_type}_amount": round(tax_amount, 4)}
        tax_total += shipping_tax
    else:
        shipping_tax = 0

    order_total = item_total + tax_total + shipping_cost - discount_total

    return {
        "orderTotal": round(order_total, 2),
        "itemTotal": round(item_total, 2),
        "taxTotal": round(tax_total, 2),
        "shippingCost": round(shipping_cost, 2),
        "shippingTax": round(shipping_tax, 2),
        "discountTotal": round(discount_total, 2),
        "taxBreakdown": tax_breakdown
    }

def main():
    shipping_province = get_shipping_province()
    tax_structure = get_tax_structure(shipping_province)
    tax_rates = get_tax_rates(tax_structure)
    
    items = []
    while True:
        print("\nEnter line item details:")
        item = {
            'price': get_float_input("Item price: $"),
        }
        
        if get_yes_no_input("Is there a discount for this item? (Y/N): "):
            item['discount'] = get_float_input("Discount amount: $")
            item['discount_taxable'] = get_yes_no_input("Is the discount taxable? (Y/N): ")
        
        items.append(item)
        
        if not get_yes_no_input("Add another item? (Y/N): "):
            break
    
    shipping_cost = 0
    shipping_taxable = False
    
    if get_yes_no_input("Is there a shipping cost? (Y/N): "):
        shipping_cost = get_float_input("Shipping cost: $")
        shipping_taxable = get_yes_no_input("Is shipping taxable? (Y/N): ")

    result = calculate_tax(items, tax_rates, shipping_cost, shipping_taxable)

    print("\nCalculation Results:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
