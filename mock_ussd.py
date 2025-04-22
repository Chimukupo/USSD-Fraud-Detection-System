def send_ussd(phone: str, message: str) -> str:
    print(f"*115# to {phone}: {message}")
    return f"Sent to {phone}: {message}"

def receive_ussd(tx_id: int, response: str) -> str:
    print(f"Received for tx_id {tx_id}: {response}")
    return f"Processed tx_id {tx_id}: {response}"