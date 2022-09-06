import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    DISCORDWEBHOOK = os.getenv('DISCORDWEBHOOK')
    SENDWEBHOOK = os.getenv('SENDWEBHOOK')
    INFLUX_ADDR = os.getenv('INFLUX_ADDR')
    INFLUX_TOKEN = os.getenv('INFLUX_TOKEN')
    INFLUX_ORG = os.getenv('INFLUX_ORG')
    INFLUX_BUCKET = os.getenv('INFLUX_BUCKET')
    LOG_FORMAT = os.getenv("LOG_FORMAT") or '%(asctime)s - %(levelname)s - %(message)s \t - %(name)s (%(filename)s).%(funcName)s(%(lineno)d) ' # https://docs.python.org/3/howto/logging.html#changing-the-format-of-displayed-messages
    LOG_LEVEL = os.getenv("LOG_LEVEL") or 'INFO'
    APPNAME = os.getenv("APPNAME") or 'NONE'
    ENV = os.getenv("ENV") or "DEV"
    EMOJIUP = os.getenv('EMOJIUP') or ":thumbsup:"
    EMOJIDOWN = os.getenv('EMOJIDOWN') or ":thumbsdown:"
    LOOPMODE = os.getenv('LOOPMODE') or 'false'
    PERSON = os.getenv('PERSON') or 'Dave'
    MEASUREMENT = os.getenv('MEASUREMENT') or 'crypto_portfolio'
    FIELD = os.getenv('FIELD') or 'holdings_gbp'
    CLOUDINARY_URL=os.getenv('CLOUDINARY_URL') or 'false'
    CLOUDINARY_API_KEY=os.getenv('CLOUDINARY_API_KEY') or 'false'
    CLOUDINARY_API_SECRET=os.getenv('CLOUDINARY_API_SECRET') or 'false'
    CLOUDINARY_CLOUD_NAME=os.getenv('CLOUDINARY_CLOUD_NAME') or 'false'
    UPLOAD_GRAPHS=os.getenv('UPLOAD_GRAPHS') or 'false'