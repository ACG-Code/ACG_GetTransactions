from cryptography.fernet import Fernet


class PySecrets:
    """
    Module for encrypting/decrypting database entries
    """
    def __init__(self):
        # in "Python Console:
        # from cryptography.fernet import Fernet
        # key = Fernet.generate_key()
        self.key = b'1seB4qb6ENRQboaLMXqN_o3V6crVkTGboZWCaJKhiEw='
        self.fernet = Fernet(self.key)

    def make_secret(self, secret: str) -> bytes:
        """
        Encrypts and encodes secret
        :param secret: string to be encrypted
        :return: bytes representation of secret
        """
        return self.fernet.encrypt(secret.encode())

    def make_public(self, secret: bytes) -> str:
        """
        Decrypts and decodes bytes secret to strgin
        :param secret: Bytes representation of secret
        :return: string secret
        """
        return self.fernet.decrypt(secret).decode()
