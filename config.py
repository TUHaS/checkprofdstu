import logging
from logging.config import dictConfig
from pathlib import Path

SECRET_KEY = ''
API_VERSION = 5.126
GROUP_ID = 'profdstu'

COLUMN_NAME_VK_ID = "Ссылка на VK"
COLUMN_NAME_BOOKNUMBER = "Номер зачетной книжки"
COLUMN_NAME_STATUS = "Статус проверки"
COLUMN_NAME_ERROR_MSG = "Ошибка"

STATUS_DUPLICATE = "Дубликат"
STATUS_ERROR = "Ошибка"
STATUS_GROUP_MEMBER = "Состоит в группе"
STATUS_NOT_MEMBER = "Не состоит в группе"


PROJECT_PATH = Path(__file__).resolve().parent
LOGFILE_PATH = PROJECT_PATH / 'logs'
if not LOGFILE_PATH.is_dir():
    LOGFILE_PATH.mkdir(parents=True, exist_ok=True)
LOGS_CONFIG = dict(
    version=1,
    formatters={
        "verbose": {
            "format": '%(asctime)s - %(levelname)s - %(funcName)s:'
                      '%(lineno)d - %(message)s',
        },
    },
    handlers={
        "info": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "backupCount": 1000,
            "formatter": "verbose",
            "filename": str(LOGFILE_PATH / "info.log")
        }
    },
    loggers={
        "": {
            "handlers": ["info"],
            "level": logging.INFO,
        }
    }
)

dictConfig(LOGS_CONFIG)
