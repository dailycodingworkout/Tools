#!/usr/bin/env python3
"""
Test script for WhatsApp Messenger Tool
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from whatsapp_messenger import WhatsAppMessenger

def test_phone_number_validation():
    """Test phone number validation functionality."""
    messenger = WhatsAppMessenger()
    
    # Test valid numbers
    valid_numbers = [
        "+919876543210",
        "+1234567890123",
        "+442012345678"
    ]
    
    # Test invalid numbers
    invalid_numbers = [
        "9876543210",  # No country code
        "+91876",      # Too short
        "+91abc123",   # Contains letters
        "invalid"      # Not a number
    ]
    
    print("Testing phone number validation...")
    
    # Test valid numbers
    for number in valid_numbers:
        result = messenger.validate_phone_number(number)
        assert result == True, f"Valid number {number} failed validation"
        print(f"✓ {number} - Valid")
    
    # Test invalid numbers
    for number in invalid_numbers:
        result = messenger.validate_phone_number(number)
        assert result == False, f"Invalid number {number} passed validation"
        print(f"✗ {number} - Invalid (as expected)")
    
    print("Phone number validation tests passed!\n")

def test_json_loading():
    """Test JSON file loading functionality."""
    messenger = WhatsAppMessenger()
    
    print("Testing JSON file loading...")
    
    # Test loading existing file
    numbers = messenger.load_phone_numbers()
    assert isinstance(numbers, list), "Should return a list"
    print(f"✓ Loaded {len(numbers)} numbers from JSON file")
    
    # Validate loaded numbers
    for number in numbers:
        assert messenger.validate_phone_number(number), f"Invalid number in JSON: {number}"
        print(f"✓ {number} - Valid format")
    
    print("JSON loading tests passed!\n")

def test_message_content():
    """Test that the message content is correct."""
    messenger = WhatsAppMessenger()
    
    print("Testing message content...")
    
    expected_message = "I need 1BHK flat under 9k"
    assert messenger.message == expected_message, f"Message should be '{expected_message}'"
    print(f"✓ Message content: '{messenger.message}'")
    
    print("Message content test passed!\n")

def main():
    """Run all tests."""
    print("WhatsApp Messenger Tool - Test Suite")
    print("=" * 40)
    
    try:
        test_phone_number_validation()
        test_json_loading()
        test_message_content()
        
        print("All tests passed! ✓")
        print("\nThe WhatsApp Messenger tool is ready to use.")
        print("Run 'python whatsapp_messenger.py' to start sending messages.")
        
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()