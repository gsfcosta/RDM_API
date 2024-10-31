class Config:
    TIMEOUT = 60
    CORS_HEADERS = "Content-Type"
    FLASK_CONFIG = 'development'
    SECRET_KEY = b'\xed\xf4\x83\xac\x92\x948\x10\xed\x04r\x94\x90\x058\xec\xf5\x84\x8bV\xfe\xceb\xea'
    database = "api_rdm"
    user = "api"
    password = "roundhead"
    host = "172.17.0.1"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://" + user + ":" + password + "@" + host + "/" + database

class Development(Config):
    DEBUG=True

class Testing(Config):
    pass

config = {
    "development": Development,
    "testing": Testing
}