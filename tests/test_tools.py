from Tools.char_counter import count_characters
from Tools.tax_calculator import tax_calculator
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

def test_tax_calculator():
    data = {
        'items': [
            {'price': 100, 'tax_rate': 10},
            {'price': 50, 'tax_rate': 5}
        ],
        'discounts': [
            {'amount': 10, 'is_taxable': True}
        ],
        'shipping_cost': 15,
        'shipping_taxable': True,
        'shipping_tax_rate': 10
    }
    result = tax_calculator(data)
    
    print("Actual tax calculation result:", result)
    print("Total tax breakdown:", result['tax_breakdown'])
    print("Calculated total: ", 
          result['item_total'] - result['discount_total'] + 
          result['shipping_cost'] + result['total_tax'])
    
    assert result['item_total'] == 150
    assert result['discount_total'] == 10
    assert result['shipping_cost'] == 15
    assert result['total_tax'] == pytest.approx(13.0, abs=0.01)
    assert result['total_amount'] == pytest.approx(169.0, abs=0.01)  # Changed back to 169.0
