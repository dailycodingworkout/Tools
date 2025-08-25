#!/usr/bin/env python3
"""
Demo: WhatsApp Messenger Tool Usage

This script demonstrates how the WhatsApp Messenger tool would work
in a real scenario (without actually sending messages).
"""

import json
from datetime import datetime, timedelta

def demo_whatsapp_messenger():
    """Demonstrate the WhatsApp Messenger tool functionality."""
    
    print("🔥 WhatsApp Messenger Tool - DEMO")
    print("=" * 40)
    print()
    
    # Show the message that would be sent
    message = "I need 1BHK flat under 9k"
    print(f"📱 Message to send: \"{message}\"")
    print()
    
    # Load and display phone numbers
    try:
        with open('phone_numbers.json', 'r') as f:
            config = json.load(f)
            numbers = config.get('numbers', [])
    except FileNotFoundError:
        numbers = ["+919876543210", "+919876543211", "+919876543212"]
    
    print(f"📋 Found {len(numbers)} phone numbers:")
    for i, number in enumerate(numbers, 1):
        print(f"   {i}. {number}")
    print()
    
    # Show scheduling simulation
    print("⏰ Message scheduling simulation:")
    now = datetime.now()
    
    for i, number in enumerate(numbers):
        send_time = now + timedelta(minutes=(i + 1) * 2)
        print(f"   {number} → {send_time.strftime('%H:%M:%S')}")
    print()
    
    # Show what would happen
    print("🚀 What would happen next:")
    print("   1. WhatsApp Web opens in your browser")
    print("   2. You scan QR code (if not logged in)")
    print("   3. Messages are scheduled and sent automatically")
    print("   4. Each message sent with 2-minute intervals")
    print("   5. Results logged to whatsapp_messenger.log")
    print()
    
    print("💡 To actually send messages:")
    print("   1. Install dependencies: pip install pywhatkit")
    print("   2. Update phone_numbers.json with real numbers")
    print("   3. Run: python whatsapp_messenger.py")
    print()
    
    print("✅ Demo complete! The tool is ready for flat hunting! 🏠")

if __name__ == "__main__":
    demo_whatsapp_messenger()