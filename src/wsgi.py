import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.app import app as application  # noqa

if __name__ == "__main__":
    application.run(host="0.0.0.0")
