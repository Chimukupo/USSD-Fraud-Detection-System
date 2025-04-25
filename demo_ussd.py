import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# ========== USSD Menu ==========
def show_menu():
    print("\nZ Mobile Money Menu")
    print("1. Send Money")
    print("2. Respond to Alerts")
    print("3. Check SMS for Phishing")
    print("4. Check Balance")
    print("5. Manage Account")
    print("6. Exit")
    return input("Select option: ")

def send_money():
    print("\nSend Money")
    amount = float(input("Enter amount (ZMW): "))
    recipient = input("Enter recipient phone: ")
    payload = {
        "user_id": 1,  # ========== Mary's user_id ==========
        "amount": amount,
        "recipient": recipient
    }
    try:
        response = requests.post(f"{BASE_URL}/transaction", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"\nTransaction sent: tx_id={data['tx_id']}, flagged={data['flagged']}")
        return data["tx_id"]
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

def respond_to_alert():
    print("\nRespond to Alerts")
    tx_id = input("Enter transaction ID: ")
    print("1. Approve")
    print("2. Cancel")
    choice = input("Select option: ")
    payload = {
        "tx_id": int(tx_id),
        "response": choice
    }
    try:
        response = requests.post(f"{BASE_URL}/ussd_response", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"\nResponse sent: tx_id={data['tx_id']}, status={data['status']}")
    except requests.RequestException as e:
        print(f"Error: {e}")

def check_sms():
    print("\nCheck SMS for Phishing")
    sms_text = input("Enter SMS text: ")
    payload = {
        "user_id": 1,  # ========== Mary's user_id ==========
        "sms_text": sms_text
    }
    try:
        response = requests.post(f"{BASE_URL}/check_sms", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"\nSMS check: {data['status']}")
        if data.get("message"):
            print(data["message"])
    except requests.RequestException as e:
        print(f"Error: {e}")

def main():
    # print("Welcome")
    dial = input("Enter USSD Code:\n")
    if dial != "*115#":
        print("Invalid code.")
        return
    while True:
        choice = show_menu()
        if choice == "1":
            send_money()
        elif choice == "2":
            respond_to_alert()
        elif choice == "3":
            check_sms()
        elif choice == "6":
            print("Thank you for using Z Mobile Money.")
            break
        else:
            print("Invalid option. Try again.")
        time.sleep(1)

if __name__ == "__main__":
    main()