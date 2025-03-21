
from Tools.char_counter import count_characters
from Tools.tax_calculator import tax_calculator, calculate_tax
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
    
    assert result['item_total'] == 150
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