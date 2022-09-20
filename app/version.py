import os
from datetime import datetime

__git_commit__ = os.environ.get("GIT_SHA", "unspecified")
__time__ = os.environ.get("BUILD_TIME", datetime.now())
