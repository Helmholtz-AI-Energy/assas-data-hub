
class Config(object):
    
    DEBUG = True
    DEVELOPMENT = True
    LSDF_ARCHIVE = r'/mnt/ASSAS/upload_test/'
    UPLOAD_DIRECTORY = r'/mnt/ASSAS/upload_test/uploads/'
    UPLOAD_FILE = r'/mnt/ASSAS/upload_test/uploads/uploads.txt'
    LOCAL_ARCHIVE = r'/root/upload/'
    PYTHON_VERSION = r'/opt/python/3.11.8/bin/python3.11'
    ASTEC_ROOT = r'/root/astecV3.1.1_linux64/astecV3.1.1'
    ASTEC_COMPUTER = r'linux_64'
    ASTEC_COMPILER = r'release'
    ASTEC_PARSER = r'/root/assas-data-hub/assas_database/assasdb/assas_astec_parser.py'
    CONNECTIONSTRING = r'mongodb://localhost:27017/'
    
    #SECRET_KEY = 'do-i-really-need-this'
    #FLASK_HTPASSWD_PATH = '/secret/.htpasswd'
    #FLASK_SECRET = SECRET_KEY
    #DB_HOST = 'database' # a docker link
   
