import hashlib
import string
import random
# Esta funão irá gerar um chave temporaria para ser usada
# como acesso para alteração de password por email.
def random_key(size=5):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))
# Esta funão irá criptografar a chave temporaria a ser usada
# como acesso para alteração de password por email.
def generate_hash_key(salt, random_str_size=5):
    random_str = random_key(random_str_size)
    text = random_str + salt
    return hashlib.sha224(text.encode('utf-8')).hexdigest()