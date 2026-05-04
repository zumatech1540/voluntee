import random

def generate_otp():
    return str(random.randint(100000, 999999))


def send_sms(phone_numbers, message):
    results = []

    for number in phone_numbers:
        print(f"[SMS SENT] {number}: {message}")

        results.append({
            "number": number,
            "status": "sent"
        })

    return {
        "status": "success",
        "count": len(phone_numbers),
        "results": results
    }