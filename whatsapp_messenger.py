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

# Import pyautogui for browser tab closing
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not installed. Please install it using: pip install pyautogui")
    pyautogui = None

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
    
    def close_browser_tab(self):
        """
        Close the current browser tab using keyboard shortcut.
        
        This function sends Ctrl+W to close the WhatsApp Web tab after message is sent.
        """
        try:
            if not PYAUTOGUI_AVAILABLE:
                logging.warning("pyautogui not available - cannot close browser tab automatically")
                return False
            
            # Wait a moment for the message to be fully sent
            time.sleep(2)
            
            # Send Ctrl+W to close the current tab
            pyautogui.hotkey('ctrl', 'w')
            logging.info("Browser tab closed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to close browser tab: {e}")
            return False
    
    def validate_phone_number(self, number: str) -> bool:
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
    
    def send_message_to_number(self, number: str, delay_seconds: int = 15) -> bool:
        """
        Send message to a single phone number and close browser tab.
        
        Args:
            number (str): Phone number with country code
            delay_seconds (int): Seconds to wait before sending (default: 15)
            
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
            
            # For delays <= 15 seconds, use sendwhatmsg_instantly for faster delivery
            # This sends the message immediately after opening WhatsApp Web
            if delay_seconds <= 15:
                logging.info(f"Sending immediate message to {number}")
                kit.sendwhatmsg_instantly(number, self.message, delay_seconds)
                logging.info(f"Message sent instantly to {number}")
                
                # Close the browser tab after sending message
                self.close_browser_tab()
                return True
            else:
                # Calculate send time (current time + delay in seconds)
                now = datetime.now()
                send_time = now + timedelta(seconds=delay_seconds)
                hour = send_time.hour
                minute = send_time.minute
                
                logging.info(f"Scheduling message to {number} at {hour:02d}:{minute:02d}")
                
                # Send message using pywhatkit
                kit.sendwhatmsg(number, self.message, hour, minute)
                
                logging.info(f"Message scheduled successfully for {number}")
                
                # Close the browser tab after sending message
                self.close_browser_tab()
                return True
            
        except Exception as e:
            logging.error(f"Failed to send message to {number}: {e}")
            return False
    
    def send_messages_to_list(self, numbers: List[str], delay_between_messages: int = 15) -> dict:
        """
        Send messages to a list of phone numbers with 15-second intervals.
        
        Args:
            numbers (List[str]): List of phone numbers
            delay_between_messages (int): Seconds between each message (default: 15)
            
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
            logging.info(f"Processing number {i+1}/{len(numbers)}: {number}")
            
            # Send message with 15-second delay (opens WhatsApp and sends immediately)
            if self.send_message_to_number(number, delay_between_messages):
                results['successful'].append(number)
                logging.info(f"Successfully sent message to {number}")
            else:
                results['failed'].append(number)
                logging.error(f"Failed to send message to {number}")
            
            # Wait 15 seconds before processing the next number (except for the last one)
            if i < len(numbers) - 1:
                logging.info(f"Waiting {delay_between_messages} seconds before next message...")
                time.sleep(delay_between_messages)
        
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
        
        # Check if pyautogui is available for tab closing
        if not PYAUTOGUI_AVAILABLE:
            print("Warning: pyautogui library not installed - browser tabs won't be closed automatically.")
            print("Install it using: pip install pyautogui")
            print("You can still proceed, but you'll need to close browser tabs manually.")
            print()
        
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