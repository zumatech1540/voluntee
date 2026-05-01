import africastalking
from django.conf import settings

# Initialize API
africastalking.initialize(
    settings.AFRICASTALKING_USERNAME,
    settings.AFRICASTALKING_API_KEY
)

sms = africastalking.SMS


def send_sms(phone_numbers, message):

    try:
        response = sms.send(
            message,
            phone_numbers
        )

        return response

    except Exception as e:
        print("SMS Error:", e)
        return None