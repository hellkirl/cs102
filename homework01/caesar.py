def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    uppercase = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]

    lowercase = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]

    digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    ciphertext = ""
    cipher_list = []
    cipher = []
    for i in plaintext:
        if i in uppercase:
            index = uppercase.index(i)
            encryption = (index + shift) % 26
            cipher_list.append(encryption)
            newletter = uppercase[encryption]
            cipher.append(newletter)
        if i in lowercase:
            index = lowercase.index(i)
            encryption = (index + shift) % 26
            cipher_list.append(encryption)
            newletter = lowercase[encryption]
            cipher.append(newletter)
        if i in digits:
            index = digits.index(i)
            encryption = index
            cipher_list.append(encryption)
            newletter = digits[encryption]
            cipher.append(newletter)
        if i not in uppercase and i not in lowercase and i not in digits:
            cipher.append(i)

    for i in cipher:
        ciphertext += i
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    uppercase = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]

    lowercase = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]

    digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    decipher_list = []
    decipher = []
    for i in ciphertext:
        if i in uppercase:
            index = uppercase.index(i)
            decryption = (index - shift) % 26
            decipher_list.append(decryption)
            newletter = uppercase[decryption]
            decipher.append(newletter)
        if i in lowercase:
            index = lowercase.index(i)
            decryption = (index - shift) % 26
            decipher_list.append(decryption)
            newletter = lowercase[decryption]
            decipher.append(newletter)
        if i in digits:
            index = digits.index(i)
            decryption = index
            decipher_list.append(decryption)
            newletter = digits[decryption]
            decipher.append(newletter)
        if i not in uppercase and i not in lowercase and i not in digits:
            decipher.append(i)

    for i in decipher:
        plaintext += i
    return plaintext
