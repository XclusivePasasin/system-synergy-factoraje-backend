from datetime import datetime, timedelta

TOKEN_BLACKLIST = {}

def blacklist_token(token):
    """
    Agrega un token a la lista negra con su tiempo de expiración.
    """
    expiration = datetime.utcnow() + timedelta(hours=24)  
    TOKEN_BLACKLIST[token] = expiration

def is_token_blacklisted(token):
    """
    Verifica si un token está en la lista negra.
    """
    if token in TOKEN_BLACKLIST:
        if TOKEN_BLACKLIST[token] > datetime.utcnow():
            return True
        else:
            del TOKEN_BLACKLIST[token]
    return False
