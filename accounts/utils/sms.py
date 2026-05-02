import requests

def send_sms(phone_numbers, message):
    """
    Example SMS sender (mock or integrate real API)
    """

    # 🔥 FOR NOW (SIMULATION)
    for number in phone_numbers:
        print(f"Sending SMS to {number}: {message}")

    return f"Sent to {len(phone_numbers)} numbers"