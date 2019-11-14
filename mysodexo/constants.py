import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://sodexows.mo2o.com"
DEFAULT_LANG = "en"
CERT_FILENAME = "sodexows.mo2o.com_client-android.crt.pem"
CERT_PATH = os.path.join(BASE_DIR, CERT_FILENAME)
KEY_FILENAME = "sodexows.mo2o.com_client-android.key.pem"
KEY_PATH = os.path.join(BASE_DIR, KEY_FILENAME)
JSON_RESPONSE_OK_CODE = 100
JSON_RESPONSE_OK_MSG = "OK"
REQUESTS_CERT = (CERT_PATH, KEY_PATH)
REQUESTS_HEADERS = {"Accept": "application/json"}
DEFAULT_DEVICE_UID = "device_uid"
DEFAULT_OS = 0
APPLICATION_NAME = "mysodexo"
SESSION_CACHE_FILENAME = "session.cache"
LOGIN_ENDPOINT = "v3/connect/login"
LOGIN_FROM_SESSION_ENDPOINT = "v3/connect/loginFromSession"
GET_CARDS_ENDPOINT = "v3/card/getCards"
GET_DETAIL_CARD_ENDPOINT = "v2/card/getDetailCard"
GET_CLEAR_PIN_ENDPOINT = "v1/card/getClearPin"
