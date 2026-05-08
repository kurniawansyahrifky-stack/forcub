from decouple import config

ADMIN_GROUP = config("ADMIN_GROUP")
POST_CHANNEL = config("POST_CHANNEL")
LOG_GROUP = config("LOG_GROUP", default=None)
ANON_CHANNEL = config("ANON_CHANNEL")
