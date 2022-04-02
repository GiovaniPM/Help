from typing import List
from unicodedata import normalize


def get_unicode_code_points(string: str) -> List[str]:
    string_normalized = normalize('NFD', string)
    code_points: List[str] = [
        'U+' + hex(ord(letter))[2:].zfill(4).upper()
        for letter in string_normalized
    ]
    return code_points


if __name__ == "__main__":
    text = 'Python 🐍™'
    code_points = get_unicode_code_points(text)
    print(code_points)