def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.
    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    len_alph = 26
    beginning_lower = ord("a")
    beginning_upper = ord("A")

    ciphertext = ""

    shift = [keyword[i % len(keyword)] for i in range(len(plaintext))]

    for i, character in enumerate(plaintext):
        if character.isupper():
            ciphertext += chr(
                (ord(character) + (ord(shift[i]) % beginning_upper) - beginning_upper) % len_alph + beginning_upper
            )
        elif character.islower():
            ciphertext += chr(
                (ord(character) + (ord(shift[i]) % beginning_lower) - beginning_lower) % len_alph + beginning_lower
            )
        else:
            ciphertext += character
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.
    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    >>> decrypt_vigenere("tfvzzvwkeaqv lq aqvpzf", "lsci")
    'introduction to python'
    """
    len_alph = 26
    beginning_lower = ord("a")
    beginning_upper = ord("A")
    plaintext = ""

    shift = [keyword[i % len(keyword)] for i in range(len(ciphertext))]

    for i, character in enumerate(ciphertext):
        if character.isupper():
            plaintext += chr(
                (ord(character) - (ord(shift[i]) % beginning_upper) - beginning_upper) % len_alph + beginning_upper
            )
        elif character.islower():
            plaintext += chr(
                (ord(character) - (ord(shift[i]) % beginning_lower) - beginning_lower) % len_alph + beginning_lower
            )
        else:
            plaintext += character
    return plaintext