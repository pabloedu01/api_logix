import IfxPy
import IfxPyDbi as dbapi2
from dotenv import load_dotenv
import os
load_dotenv()

def conexao ():
    connection_info = "SERVER={};DATABASE=logix;HOST={};SERVICE={};UID={};PWD={};".format(
        os.environ.get('DB_CONNECTION_NAME')
        ,os.environ.get('DB_HOST')
        ,os.environ.get('DB_PORT')
        ,os.environ.get('DB_USERNAME')
        ,os.environ.get('DB_PASSWORD'))
    conn = dbapi2.connect(connection_info, "", "")
    cur = conn.cursor()
    cur.execute('set isolation to dirty read;')
    return(conn, cur)