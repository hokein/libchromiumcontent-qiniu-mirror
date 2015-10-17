#!/usr/bin/env python

import os

# Maximum re-uploaded times to Qiniu.
MAX_TRIES = 10

access_key = os.getenv('QINIU_ACCESS_KEY')
secret_key = os.getenv('QINIU_SECRET_KEY')
bucket_name = os.getenv('QINIU_BUCKET')

QINIU_UPLOAD_URL = 'up.qiniug.com'
CONFIG_FILE_URL = 'https://raw.githubusercontent.com/atom/electron/master/script/lib/config.py'

# Time interval in seconds between each syns.
RUN_TIME_INTERVAL = 24*60*60

LIBCHROMIUMCONTENT_BINARIES = [
  'libchromiumcontent.zip',
  'libchromiumcontent-static.zip',
]

PLATFORMS = [
  'osx',
  'win',
  'linux',
]

TARGETS = [
  'x64',
  'ia32',
  'arm',
]
