#!/usr/bin/env python3
"""
WhatsApp Messenger Tool
======================

A tool to send WhatsApp messages to a list of phone numbers.
This script sends the message "I need 1BHK flat under 9k" to multiple recipients.

Usage:
    python whatsapp_messenger.py

Requirements:
    - pywhatkit library
    - Internet connection
    - WhatsApp Web access
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List
import json
import os

# Import pywhatkit with error handling
try:
    import pywhatkit as kit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
    print("Warning: pywhatkit not installed. Please install it using: pip install pywhatkit")
    kit = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_messenger.log'),
        logging.StreamHandler()
    ]
)

class WhatsAppMessenger:
    """Class to handle WhatsApp messaging functionality."""
    
    def __init__(self):
        self.message = "I need 1BHK flat under 9k"
        self.numbers_file = "phone_numbers.json"
        
    def load_phone_numbers(self) -> List[str]:
        """
        Load phone numbers from a JSON file.
        
        Returns:
            List[str]: List of phone numbers with country code
        """
        if os.path.exists(self.numbers_file):
            try:
                with open(self.numbers_file, 'r') as f:
                    data = json.load(f)
                    return data.get('numbers', [])
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logging.error(f"Error loading phone numbers: {e}")
                return []
        else:
            # Create sample file if it doesn't exist
            self.create_sample_numbers_file()
            logging.info(f"Created sample {self.numbers_file}. Please update it with actual numbers.")
            return []
    
    def create_sample_numbers_file(self):
        """Create a sample phone numbers file."""
        sample_data = {
            "numbers": [
                "+919876543210",
                "+919876543211",
                "+919876543212"
            ],
            "note": "Replace with actual phone numbers including country code (e.g., +91 for India)"
        }
        
        with open(self.numbers_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    def validate_phone_number(self, number: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            number (str): Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation - should start with + and have at least 10 digits
        if not number.startswith('+'):
            return False
        
        # Remove + and check if remaining characters are digits
        digits_only = number[1:]
        if not digits_only.isdigit():
            return False
            
        # Should have at least 10 digits (most countries)
        if len(digits_only) < 10:
            return False
            
        return True
    
    def send_message_to_number(self, number: str, delay_minutes: int = 1) -> bool:
        """
        Send message to a single phone number.
        
        Args:
            number (str): Phone number with country code
            delay_minutes (int): Minutes to wait before sending
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if pywhatkit is available
            if not PYWHATKIT_AVAILABLE:
                logging.error("pywhatkit library not available. Please install it using: pip install pywhatkit")
                return False
            
            # Validate phone number
            if not self.validate_phone_number(number):
                logging.error(f"Invalid phone number format: {number}")
                return False
            
            # Calculate send time (current time + delay)
            now = datetime.now()
            send_time = now + timedelta(minutes=delay_minutes)
            hour = send_time.hour
            minute = send_time.minute
            
            logging.info(f"Scheduling message to {number} at {hour:02d}:{minute:02d}")
            
            # Send message using pywhatkit
            kit.sendwhatmsg(number, self.message, hour, minute)
            
            logging.info(f"Message scheduled successfully for {number}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send message to {number}: {e}")
            return False
    
    def send_messages_to_list(self, numbers: List[str], delay_between_messages: int = 2) -> dict:
        """
        Send messages to a list of phone numbers.
        
        Args:
            numbers (List[str]): List of phone numbers
            delay_between_messages (int): Minutes between each message
            
        Returns:
            dict: Summary of results
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(numbers)
        }
        
        logging.info(f"Starting to send messages to {len(numbers)} numbers")
        
        for i, number in enumerate(numbers):
            delay = (i + 1) * delay_between_messages  # Staggered timing
            
            if self.send_message_to_number(number, delay):
                results['successful'].append(number)
            else:
                results['failed'].append(number)
            
            # Small delay to prevent overwhelming the system
            time.sleep(1)
        
        logging.info(f"Messaging complete. Success: {len(results['successful'])}, Failed: {len(results['failed'])}")
        return results
    
    def run(self):
        """Main method to run the messenger."""
        print("WhatsApp Messenger Tool")
        print("=" * 30)
        print(f"Message: '{self.message}'")
        print()
        
        # Check if pywhatkit is available
        if not PYWHATKIT_AVAILABLE:
            print("Error: pywhatkit library is required but not installed.")
            print("Please install it using: pip install pywhatkit")
            return
        
        # Load phone numbers
        numbers = self.load_phone_numbers()
        
        if not numbers:
            print(f"No phone numbers found. Please update {self.numbers_file} with actual numbers.")
            return
        
        print(f"Loaded {len(numbers)} phone numbers:")
        for i, number in enumerate(numbers, 1):
            print(f"  {i}. {number}")
        
        # Confirm before sending
        confirm = input("\nProceed with sending messages? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
        
        # Send messages
        results = self.send_messages_to_list(numbers)
        
        # Display results
        print("\nResults:")
        print(f"Total numbers: {results['total']}")
        print(f"Successful: {len(results['successful'])}")
        print(f"Failed: {len(results['failed'])}")
        
        if results['failed']:
            print("\nFailed numbers:")
            for number in results['failed']:
                print(f"  - {number}")
        
        print(f"\nDetailed logs saved to: whatsapp_messenger.log")

def main():
    """Main function."""
    try:
        messenger = WhatsAppMessenger()
        messenger.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()