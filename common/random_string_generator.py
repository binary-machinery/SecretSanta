import random
import string


class RandomStringGenerator:
    @staticmethod
    def generate(string_length):
        return "".join(random.choices(string.ascii_letters + string.digits, k=string_length))
