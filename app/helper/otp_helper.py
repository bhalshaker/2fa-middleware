import random

class OTPHelper:

    @staticmethod
    def create_four_digit_code():
        return random.randint(1000,9999)