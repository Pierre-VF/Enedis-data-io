"""
Ce module permet de décrypter les fichiers transmis par Enedis via e-mail ou FTP
"""

from Crypto.Cipher import AES


def decrypt_file(file_path: str, key: str, output_file: str) -> str:
    with open(file_path, "rb") as f:
        file_content = f.read()

    iv = file_content[:16]
    encoded_key = bytes.fromhex(key)
    cipher = AES.new(encoded_key, AES.MODE_CBC, iv=iv)

    data_bytes = file_content[16:]
    decrypted_data = cipher.decrypt(data_bytes)

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    return output_file