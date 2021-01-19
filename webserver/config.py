import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'tmp')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024

