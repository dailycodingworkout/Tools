#!/usr/bin/env python3
"""
Example: Configure Phone Numbers for WhatsApp Messenger

This script shows how to configure phone numbers for the WhatsApp Messenger tool.
"""

import json

def create_phone_numbers_config():
    """Create or update phone numbers configuration."""
    
    print("WhatsApp Messenger - Phone Number Configuration")
    print("=" * 50)
    print()
    
    # Example phone numbers - replace with real ones
    example_numbers = [
        "+919876543210",  # India
        "+919876543211",  # India
        "+1234567890",    # US
        "+442012345678"   # UK
    ]
    
    print("Current example phone numbers:")
    for i, number in enumerate(example_numbers, 1):
        print(f"  {i}. {number}")
    
    print()
    print("Important notes:")
    print("- Include country code (e.g., +91 for India, +1 for US)")
    print("- Use international format")
    print("- Make sure the numbers are valid WhatsApp numbers")
    print()
    
    # Option to use custom numbers
    use_custom = input("Do you want to enter custom phone numbers? (y/N): ").strip().lower()
    
    if use_custom == 'y':
        numbers = []
        print("\nEnter phone numbers (press Enter on empty line to finish):")
        
        while True:
            number = input("Phone number (with country code): ").strip()
            if not number:
                break
            
            # Basic validation
            if not number.startswith('+'):
                print("  Warning: Number should start with + (country code)")
                
            numbers.append(number)
            print(f"  Added: {number}")
        
        if not numbers:
            print("No numbers entered. Using example numbers.")
            numbers = example_numbers
    else:
        numbers = example_numbers
    
    # Save to JSON file
    config = {
        "numbers": numbers,
        "note": "Replace with actual phone numbers including country code (e.g., +91 for India, +1 for US, etc.)",
        "message": "I need 1BHK flat under 9k",
        "created": "2024-01-01"
    }
    
    filename = "phone_numbers.json"
    
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguration saved to {filename}")
    print(f"Total numbers: {len(numbers)}")
    print("\nYou can now run: python whatsapp_messenger.py")

if __name__ == "__main__":
    create_phone_numbers_config()