from datetime import timedelta

# API
API_PREFIX = "/api/v0.2"

# Time and date formatting
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"

# Sessions
SESSION_LIFETIME = timedelta(days=30)

# Pay period
PAY_PERIOD_START_DAY = 8
PAY_PERIOD_LENGTH = 21

# Bonuses
BONUS_BLOCK_MINUTES = 30

MORNING_BONUS_START = "05:00"
MORNING_BONUS_END = "07:00"

EVENING_BONUS_START = "18:00"
EVENING_BONUS_END = "22:00"

MORNING_BONUS_POINTS = 9
EVENING_BONUS_POINTS = 4


# -----------------------------
# Administration
# -----------------------------

ENFORCE_MIN_ADMIN_COUNT = True
MIN_NUM_ADMINS = 1

ALLOW_ADMIN_ROLE_CHANGES = True

DELETE_USER_REQUIRES_CONFIRMATION = True
DELETE_USER_CASCADE_SHIFTS = True

ARCHIVE_USER_BEFORE_DELETE = True

# -----------------------------
# Deleted user archive
# -----------------------------

DELETED_USERS_ARCHIVE_DIR = "deleted_users"

DELETED_USERS_RETENTION_DAYS = 365 * 3
DELETED_USERS_MAX_ARCHIVE_SIZE_MB = 1024
