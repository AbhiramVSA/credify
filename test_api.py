#!/usr/bin/env python3
"""
Test script for the customer registration API endpoint.
This script demonstrates how to use the /register endpoint.
"""

import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
REGISTER_URL = f"{BASE_URL}/register"

def test_customer_registration():
    """Test customer registration with sample data"""
    
    # Sample customer data
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9876543210"
    }
    
    print("Testing Customer Registration API")
    print("=" * 40)
    print(f"Sending POST request to: {REGISTER_URL}")
    print(f"Request data: {json.dumps(customer_data, indent=2)}")
    print()
    
    try:
        response = requests.post(REGISTER_URL, json=customer_data)
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Customer registration successful!")
            data = response.json()
            print(f"Customer ID: {data['customer_id']}")
            print(f"Name: {data['name']}")
            print(f"Approved Limit: ₹{data['approved_limit']:,.2f}")
        else:
            print("❌ Customer registration failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")


def test_validation_errors():
    """Test API validation with invalid data"""
    
    print("\nTesting Validation Errors")
    print("=" * 40)
    
    # Test cases with invalid data
    test_cases = [
        {
            "name": "Missing required fields",
            "data": {"first_name": "John"}
        },
        {
            "name": "Invalid age (too young)",
            "data": {
                "first_name": "Jane",
                "last_name": "Doe",
                "age": 15,
                "monthly_income": 30000,
                "phone_number": "9876543210"
            }
        },
        {
            "name": "Invalid monthly_income (negative)",
            "data": {
                "first_name": "Bob",
                "last_name": "Smith",
                "age": 25,
                "monthly_income": -1000,
                "phone_number": "9876543210"
            }
        },
        {
            "name": "Invalid phone number (too short)",
            "data": {
                "first_name": "Alice",
                "last_name": "Johnson",
                "age": 28,
                "monthly_income": 40000,
                "phone_number": "12345"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Data: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(REGISTER_URL, json=test_case['data'])
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to the API server.")
            break
        except Exception as e:
            print(f"❌ Error occurred: {str(e)}")


if __name__ == "__main__":
    test_customer_registration()
    test_validation_errors()