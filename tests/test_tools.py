
from Tools.char_counter import count_characters
from Tools.tax_calculator import tax_calculator, calculate_tax, calculate_vat, validate_vat_rate
import pytest

def test_char_counter():
    result = count_characters("Hello, world!")
    assert result['total_characters'] == 13
    assert "Within character limit" in result['excess_message']

def test_char_counter_excess():
    long_string = "a" * 3600
    result = count_characters(long_string)
    assert result['total_characters'] == 3600
    assert "Character limit exceeded by 68 characters" in result['excess_message']

def test_char_counter():
    result = count_characters("Hello, world!")
    assert result['total_characters'] == 13
    assert "Within character limit" in result['excess_message']

def test_char_counter_excess():
    long_string = "a" * 3600
    result = count_characters(long_string)
    assert result['total_characters'] == 3600
    assert "Character limit exceeded by 68 characters" in result['excess_message']

def test_calculate_tax():
    assert calculate_tax(100, 10) == 10.0
    assert calculate_tax(50, 5) == 2.5
    assert calculate_tax(0, 10) == 0.0

def test_condition_1():
    """Condition 1: prices before tax=false, discount taxable=true, shipping taxable=false"""
    data = {
        'items': [
            {'price': 100, 'tax_rate': 10},
            {'price': 50, 'tax_rate': 5}
        ],
        'discounts': [
            {'amount': 10, 'is_taxable': True, 'item_index': 1}, 
            {'amount': 2.5, 'is_taxable': True, 'item_index': 2}
        ],
        'shipping_cost': 15,
        'shipping_taxable': False,
        'is_sales_before_tax': False,
        'discount_is_taxable': True
    }
    
    result = tax_calculator(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 12.5
    assert result['total_tax'] == 13.63
    assert result['shipping_cost'] == 15
    assert result['shipping_tax'] == 0
    assert round(result['total_amount'], 2) == 166.13

def test_condition_2():
    """Condition 2: prices before tax=true, discount taxable=true, shipping taxable=false"""
    data = {
        'items': [
            {'price': 100, 'tax_rate': 10},
            {'price': 50, 'tax_rate': 5}
        ],
        'discounts': [
            {'amount': 10, 'is_taxable': True, 'item_index': 1}, 
            {'amount': 2.5, 'is_taxable': True, 'item_index': 2}
        ],
        'shipping_cost': 15,
        'shipping_taxable': False,
        'is_sales_before_tax': True,
        'discount_is_taxable': True
    }
    
    result = tax_calculator(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 12.5
    assert round(result['total_tax'], 2) == 12.5
    assert result['shipping_cost'] == 15
    assert result['shipping_tax'] == 0
    assert round(result['total_amount'], 2) == 165

def test_condition_3():
    """Condition 3: prices before tax=false, discount taxable=false, shipping taxable=false"""
    data = {
        'items': [
            {'price': 100, 'tax_rate': 10},
            {'price': 50, 'tax_rate': 5}
        ],
        'discounts': [
            {'amount': 10, 'is_taxable': False, 'item_index': 1}, 
            {'amount': 2.5, 'is_taxable': False, 'item_index': 2}
        ],
        'shipping_cost': 15,
        'shipping_taxable': False,
        'is_sales_before_tax': False,
        'discount_is_taxable': False
    }
    
    result = tax_calculator(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 12.5
    assert round(result['total_tax'], 2) == 12.5
    assert result['shipping_cost'] == 15
    assert result['shipping_tax'] == 0
    assert round(result['total_amount'], 2) == 165

def test_condition_4():
    """Condition 4: prices before tax=true, discount taxable=false, shipping taxable=false"""
    data = {
        'items': [
            {'price': 100, 'tax_rate': 10},
            {'price': 50, 'tax_rate': 5}
        ],
        'discounts': [
            {'amount': 10, 'is_taxable': False, 'item_index': 1}, 
            {'amount': 2.5, 'is_taxable': False, 'item_index': 2}
        ],
        'shipping_cost': 15,
        'shipping_taxable': False,
        'is_sales_before_tax': True,
        'discount_is_taxable': False
    }
    
    result = tax_calculator(data)
    
    assert result['item_total'] == 137.5
    assert result['discount_total'] == 12.5
    assert round(result['total_tax'], 2) == 11.38
    assert result['shipping_cost'] == 15
    assert result['shipping_tax'] == 0
    assert round(result['total_amount'], 2) == 163.88

def test_shipping_tax():
    """Test with shipping tax"""
    data = {
        'items': [
            {'price': 100, 'tax_rate': 10}
        ],
        'discounts': [],
        'shipping_cost': 20,
        'shipping_taxable': True,
        'shipping_tax_rate': 5,
        'is_sales_before_tax': True,
        'discount_is_taxable': False
    }
    
    result = tax_calculator(data)
    
    assert result['shipping_cost'] == 20
    assert result['shipping_tax'] == 1
    assert round(result['total_tax'], 2) == 11
    assert round(result['total_amount'], 2) == 131

def test_empty_items():
    """Test with no items"""
    data = {
        'items': [],
        'discounts': [],
        'shipping_cost': 15,
        'shipping_taxable': False
    }
    
    result = tax_calculator(data)
    
    assert result['item_total'] == 0
    assert round(result['total_tax'], 2) == 0
    assert round(result['total_amount'], 2) == 15

# VAT (Value Added Tax) Tests for International Markets

def test_vat_basic():
    """Test basic VAT calculation without discounts or shipping"""
    data = {
        'items': [{'price': 100}, {'price': 50}],
        'vat_rate': 12
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 0
    assert result['net_amount'] == 150
    assert result['vat_amount'] == 18.00
    assert result['gross_amount'] == 168.00
    assert result['vat_rate_applied'] == 12.00

def test_vat_discount_before_tax_taxable():
    """VAT Condition 2: Discounts before tax, discounts taxable"""
    data = {
        'items': [{'price': 100}, {'price': 50}],
        'vat_rate': 12,
        'discounts': [{'amount': 10}],
        'is_sales_before_tax': True,
        'discount_is_taxable': True
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 10
    assert result['net_amount'] == 140
    assert result['vat_amount'] == 18.00  # (140 * 0.12) + (10 * 0.12)
    assert result['gross_amount'] == 158.00

def test_vat_discount_before_tax_non_taxable():
    """VAT Condition 4: Discounts before tax, discounts not taxable"""
    data = {
        'items': [{'price': 100}, {'price': 50}],
        'vat_rate': 12,
        'discounts': [{'amount': 10}],
        'is_sales_before_tax': True,
        'discount_is_taxable': False
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 10
    assert result['net_amount'] == 140
    assert result['vat_amount'] == 16.80  # (140 * 0.12) only
    assert result['gross_amount'] == 156.80

def test_vat_discount_after_tax_taxable():
    """VAT Condition 1: Discounts after tax, discounts taxable"""
    data = {
        'items': [{'price': 100}, {'price': 50}],
        'vat_rate': 12,
        'discounts': [{'amount': 10}],
        'is_sales_before_tax': False,
        'discount_is_taxable': True
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 10
    assert result['net_amount'] == 140
    assert result['vat_amount'] == 19.20  # (150 * 0.12) + (10 * 0.12)
    assert result['gross_amount'] == 159.20

def test_vat_discount_after_tax_non_taxable():
    """VAT Condition 3: Discounts after tax, discounts not taxable"""
    data = {
        'items': [{'price': 100}, {'price': 50}],
        'vat_rate': 12,
        'discounts': [{'amount': 10}],
        'is_sales_before_tax': False,
        'discount_is_taxable': False
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 10
    assert result['net_amount'] == 140
    assert result['vat_amount'] == 18.00  # (150 * 0.12) only
    assert result['gross_amount'] == 158.00

def test_vat_with_taxable_shipping():
    """Test VAT calculation with taxable shipping"""
    data = {
        'items': [{'price': 100}],
        'vat_rate': 20,
        'shipping_cost': 10,
        'shipping_taxable': True
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 100
    assert result['shipping_cost'] == 10
    assert result['net_amount'] == 110
    assert result['vat_amount'] == 22.00  # (100 * 0.20) + (10 * 0.20)
    assert result['gross_amount'] == 132.00

def test_vat_with_non_taxable_shipping():
    """Test VAT calculation with non-taxable shipping"""
    data = {
        'items': [{'price': 100}],
        'vat_rate': 20,
        'shipping_cost': 10,
        'shipping_taxable': False
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 100
    assert result['shipping_cost'] == 10
    assert result['net_amount'] == 110
    assert result['vat_amount'] == 20.00  # (100 * 0.20) only
    assert result['gross_amount'] == 130.00

def test_vat_rate_negative():
    """Test that negative VAT rate raises error"""
    data = {
        'items': [{'price': 100}],
        'vat_rate': -5
    }
    with pytest.raises(ValueError, match="VAT rate cannot be negative"):
        calculate_vat(data)

def test_vat_rate_exceeds_100():
    """Test that VAT rate > 100% raises error"""
    data = {
        'items': [{'price': 100}],
        'vat_rate': 150
    }
    with pytest.raises(ValueError, match="VAT rate cannot exceed 100%"):
        calculate_vat(data)

def test_vat_rate_invalid():
    """Test that invalid VAT rate raises error"""
    data = {
        'items': [{'price': 100}],
        'vat_rate': 'invalid'
    }
    with pytest.raises(ValueError, match="Invalid VAT rate"):
        calculate_vat(data)

def test_vat_empty_items():
    """Test VAT with no items"""
    data = {
        'items': [],
        'vat_rate': 12,
        'shipping_cost': 15,
        'shipping_taxable': True
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 0
    assert result['net_amount'] == 15
    assert result['vat_amount'] == 1.80
    assert result['gross_amount'] == 16.80

def test_vat_breakdown():
    """Test that VAT breakdown is correctly generated"""
    data = {
        'items': [{'price': 100}],
        'vat_rate': 20,
        'shipping_cost': 10,
        'shipping_taxable': True
    }
    result = calculate_vat(data)
    
    assert len(result['vat_breakdown']) == 2
    assert result['vat_breakdown'][0]['item'] == 'Items'
    assert result['vat_breakdown'][0]['net_amount'] == 100.00
    assert result['vat_breakdown'][0]['vat'] == 20.00
    assert result['vat_breakdown'][1]['item'] == 'Shipping'
    assert result['vat_breakdown'][1]['net_amount'] == 10.00
    assert result['vat_breakdown'][1]['vat'] == 2.00

def test_vat_complex_scenario():
    """Test complex VAT scenario with multiple items, discounts, and shipping"""
    data = {
        'items': [{'price': 100}, {'price': 50}, {'price': 75}],
        'vat_rate': 20,
        'discounts': [{'amount': 15}, {'amount': 5}],
        'shipping_cost': 12,
        'shipping_taxable': True,
        'is_sales_before_tax': True,
        'discount_is_taxable': False
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 225
    assert result['discount_total'] == 20
    assert result['net_amount'] == 217  # (225 - 20) + 12
    assert result['vat_amount'] == 43.40  # (205 * 0.20) + (12 * 0.20)
    assert result['gross_amount'] == 260.40

def test_vat_philippines_rate():
    """Test VAT with Philippines standard rate (12%)"""
    data = {
        'items': [{'price': 1000}],
        'vat_rate': 12,
        'shipping_cost': 50,
        'shipping_taxable': True
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 1000
    assert result['net_amount'] == 1050
    assert result['vat_amount'] == 126.00
    assert result['gross_amount'] == 1176.00

def test_vat_eu_rate():
    """Test VAT with EU standard rate (20%)"""
    data = {
        'items': [{'price': 500}],
        'vat_rate': 20,
        'discounts': [{'amount': 50}],
        'is_sales_before_tax': False,
        'discount_is_taxable': False
    }
    result = calculate_vat(data)
    
    assert result['item_total'] == 500
    assert result['discount_total'] == 50
    assert result['net_amount'] == 450
    assert result['vat_amount'] == 100.00  # Only on items: 500 * 0.20
    assert result['gross_amount'] == 550.00

def test_validate_vat_rate_valid():
    """Test validate_vat_rate with valid inputs"""
    assert validate_vat_rate(12) == 12
    assert validate_vat_rate(20.5) == 20.5
    assert validate_vat_rate('15') == 15
    assert validate_vat_rate(0) == 0
    assert validate_vat_rate(100) == 100

def test_validate_vat_rate_invalid():
    """Test validate_vat_rate with invalid inputs"""
    with pytest.raises(ValueError, match="VAT rate cannot be negative"):
        validate_vat_rate(-1)
    
    with pytest.raises(ValueError, match="VAT rate cannot exceed 100%"):
        validate_vat_rate(101)
    
    with pytest.raises(ValueError, match="Invalid VAT rate"):
        validate_vat_rate('abc')