# -*- coding: utf-8 -*-
import os
from lms.envs.production import *

####### Settings common to LMS and CMS
import json
import os

from xmodule.modulestore.modulestore_settings import update_module_store_settings

# Mongodb connection parameters: simply modify `mongodb_parameters` to affect all connections to MongoDb.
mongodb_parameters = {
    "host": "mongodb",
    "port": 27017,
    
    "user": None,
    "password": None,
    
    "db": "openedx",
}
DOC_STORE_CONFIG = mongodb_parameters
CONTENTSTORE = {
    "ENGINE": "xmodule.contentstore.mongo.MongoContentStore",
    "ADDITIONAL_OPTIONS": {},
    "DOC_STORE_CONFIG": DOC_STORE_CONFIG
}
# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)
DATA_DIR = "/openedx/data/"
for store in MODULESTORE["default"]["OPTIONS"]["stores"]:
   store["OPTIONS"]["fs_root"] = DATA_DIR

# Behave like memcache when it comes to connection errors
DJANGO_REDIS_IGNORE_EXCEPTIONS = True

DEFAULT_FROM_EMAIL = ENV_TOKENS.get("DEFAULT_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS.get("DEFAULT_FEEDBACK_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
SERVER_EMAIL = ENV_TOKENS.get("SERVER_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
TECH_SUPPORT_EMAIL = ENV_TOKENS.get("TECH_SUPPORT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
CONTACT_EMAIL = ENV_TOKENS.get("CONTACT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
BUGS_EMAIL = ENV_TOKENS.get("BUGS_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
UNIVERSITY_EMAIL = ENV_TOKENS.get("UNIVERSITY_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
PRESS_EMAIL = ENV_TOKENS.get("PRESS_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
PAYMENT_SUPPORT_EMAIL = ENV_TOKENS.get("PAYMENT_SUPPORT_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
BULK_EMAIL_DEFAULT_FROM_EMAIL = ENV_TOKENS.get("BULK_EMAIL_DEFAULT_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
API_ACCESS_MANAGER_EMAIL = ENV_TOKENS.get("API_ACCESS_MANAGER_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])
API_ACCESS_FROM_EMAIL = ENV_TOKENS.get("API_ACCESS_FROM_EMAIL", ENV_TOKENS["CONTACT_EMAIL"])

# Get rid completely of coursewarehistoryextended, as we do not use the CSMH database
INSTALLED_APPS.remove("lms.djangoapps.coursewarehistoryextended")
DATABASE_ROUTERS.remove(
    "openedx.core.lib.django_courseware_routers.StudentModuleHistoryExtendedRouter"
)

# Set uploaded media file path
MEDIA_ROOT = "/openedx/media/"

# Add your MFE and third-party app domains here
CORS_ORIGIN_WHITELIST = []

# Video settings
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT

GRADES_DOWNLOAD = {
    "STORAGE_TYPE": "",
    "STORAGE_KWARGS": {
        "base_url": "/media/grades/",
        "location": "/openedx/media/grades",
    },
}

ORA2_FILEUPLOAD_BACKEND = "filesystem"
ORA2_FILEUPLOAD_ROOT = "/openedx/data/ora2"
ORA2_FILEUPLOAD_CACHE_NAME = "ora2-storage"

# Change syslog-based loggers which don't work inside docker containers
LOGGING["handlers"]["local"] = {
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "all.log"),
    "formatter": "standard",
}
LOGGING["handlers"]["tracking"] = {
    "level": "DEBUG",
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "tracking.log"),
    "formatter": "standard",
}
LOGGING["loggers"]["tracking"]["handlers"] = ["console", "local", "tracking"]

# Email
EMAIL_USE_SSL = False
# Forward all emails from edX's Automated Communication Engine (ACE) to django.
ACE_ENABLED_CHANNELS = ["django_email"]
ACE_CHANNEL_DEFAULT_EMAIL = "django_email"
ACE_CHANNEL_TRANSACTIONAL_EMAIL = "django_email"
EMAIL_FILE_PATH = "/tmp/openedx/emails"

LOCALE_PATHS.append("/openedx/locale/contrib/locale")
LOCALE_PATHS.append("/openedx/locale/user/locale")

# Allow the platform to include itself in an iframe
X_FRAME_OPTIONS = "SAMEORIGIN"


JWT_AUTH["JWT_ISSUER"] = "https://unicapenlinea.mp.gob.gt/oauth2"
JWT_AUTH["JWT_AUDIENCE"] = "openedx"
JWT_AUTH["JWT_SECRET_KEY"] = "F5I08q3gkeviBd0ttHnQBDgp"
JWT_AUTH["JWT_PRIVATE_SIGNING_JWK"] = json.dumps(
    {
        "kid": "openedx",
        "kty": "RSA",
        "e": "AQAB",
        "d": "BOQLp2otAR8DGVAcRXNF405-2iOY-EGGtMSxJAAdiQDB1-WDDpkgvhqGThtgmlXBXZwEix_ne8oAL1MsYSSJuMUrQk68PDZouvQzYejE0Y_6IZkHthx6Yl7tRIAzZ-4hW58vqUoUTg4D162PHpzXafLJzWpm7rzrLZCT5AmOt80Rq8AE-sRrRFdQw9nuo2uArXysO1GdbCjTP_uWJX19CcpSVJP4rwacijU_Dv5oSsww6OLAVQ7h46ZqlwSQoEOI76_MIgNd--N59yGKXEUyFJag-ZWW-guEkQLJugzInSUQRrosazkP1CSDo_JgI-4fqhxmznEBODe-J3-DXfB5qw",
        "n": "jFOFLdaw45cyQ93h4IfDBV3YD14QAquyLXkDWLMLk2TVF5gs17q86UKGhkTINcMI1r41vNeNf7CluNWogRCXOZN5-Smo37NyHYFt5xlHrBtjC84C7gh2Et0Vzy_6CYyYGLe5Xur6R81BZjPBoV3BI6TkSLkJ-MXqpc6815J5dKvtTzR10Kdi1Q8x9gdELdrKR0zZJ4Yw85i64kIkZe89B5skYhc_eyTZY8Hz3XA_2zeaqFnIF6zLoAJg5FWla2dSIvZAr2bNd-FqjUaayTHGYto0yfl4oU8V_ZuaW7gxYRVz0yRYUFU-CXHzNW49Dy1tYUSh20shI-zbQ_Tb2ytC_Q",
        "p": "uABw6w_q35Ma7f49FDEuhgbqwqAAhjGHOfKbXkG_M-dBQr1CCzeRaKKitG6g0Bscoxh6nt_aRS1_AHS3tRbD_0FzFQ5qZDbBNyC98VeNkYpr277ps5LiMXjUlI2lkD1_aHeniI9amHzqtLHuv3YT8YfEnAgbOoikwRcl8pheuAc",
        "q": "wzwU9UR-Mde7_dO8PDN_5G2CrXWNF9CEX3c09xKTnKSdyS9rDsGXQyjkFEaBED0gvAD0-QJpryCR9P_9neY5prBXRoxdMGJ0QWcY9eafqlgGUMzohIXci4u-ETx3YtBssnxn9706CdpFQXzwlYeC6vvhnN1jdNMZgv657kW2Q9s",
    }
)
JWT_AUTH["JWT_PUBLIC_SIGNING_JWK_SET"] = json.dumps(
    {
        "keys": [
            {
                "kid": "openedx",
                "kty": "RSA",
                "e": "AQAB",
                "n": "jFOFLdaw45cyQ93h4IfDBV3YD14QAquyLXkDWLMLk2TVF5gs17q86UKGhkTINcMI1r41vNeNf7CluNWogRCXOZN5-Smo37NyHYFt5xlHrBtjC84C7gh2Et0Vzy_6CYyYGLe5Xur6R81BZjPBoV3BI6TkSLkJ-MXqpc6815J5dKvtTzR10Kdi1Q8x9gdELdrKR0zZJ4Yw85i64kIkZe89B5skYhc_eyTZY8Hz3XA_2zeaqFnIF6zLoAJg5FWla2dSIvZAr2bNd-FqjUaayTHGYto0yfl4oU8V_ZuaW7gxYRVz0yRYUFU-CXHzNW49Dy1tYUSh20shI-zbQ_Tb2ytC_Q",
            }
        ]
    }
)
JWT_AUTH["JWT_ISSUERS"] = [
    {
        "ISSUER": "https://unicapenlinea.mp.gob.gt/oauth2",
        "AUDIENCE": "openedx",
        "SECRET_KEY": "F5I08q3gkeviBd0ttHnQBDgp"
    }
]


######## End of settings common to LMS and CMS

######## Common LMS settings
LOGIN_REDIRECT_WHITELIST = ["admin-unicapenlinea.mp.gob.gt"]

# Better layout of honor code/tos links during registration
REGISTRATION_EXTRA_FIELDS["terms_of_service"] = "required"
REGISTRATION_EXTRA_FIELDS["honor_code"] = "hidden"

# This url must not be None and should not be used anywhere
LEARNING_MICROFRONTEND_URL = "http://learn.openedx.org"

# Fix media files paths
PROFILE_IMAGE_BACKEND["options"]["location"] = os.path.join(
    MEDIA_ROOT, "profile-images/"
)

COURSE_CATALOG_VISIBILITY_PERMISSION = "see_in_catalog"
COURSE_ABOUT_VISIBILITY_PERMISSION = "see_about_page"

# Allow insecure oauth2 for local interaction with local containers
OAUTH_ENFORCE_SECURE = False

# Create folders if necessary
for folder in [DATA_DIR, LOG_DIR, MEDIA_ROOT, STATIC_ROOT_BASE, ORA2_FILEUPLOAD_ROOT]:
    if not os.path.exists(folder):
        os.makedirs(folder)



######## End of common LMS settings

ALLOWED_HOSTS = [
    ENV_TOKENS.get("LMS_BASE"),
    FEATURES["PREVIEW_LMS_BASE"],
    "lms",
]


# Properly set the "secure" attribute on session/csrf cookies. This is required in
# Chrome to support samesite=none cookies.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
DCS_SESSION_COOKIE_SAMESITE = "None"


# Required to display all courses on start page
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True

