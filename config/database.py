from bcpandas import SqlCreds

creds = None

def init_db(server, database, username=None, password=None):
    global creds
    creds = SqlCreds(server, database, username, password)
    return creds

def get_creds():
    global creds
    if creds is None:
        raise Exception("La base de datos no ha sido inicializada. Llama a init_db() primero.")
    return creds