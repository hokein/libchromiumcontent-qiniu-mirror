#!/usr/bin/env python

import os
import re
import time
import sys

from config import access_key, secret_key, bucket_name, MAX_TRIES, \
                   QINIU_UPLOAD_URL
from qiniu import Auth, put_file, set_default, Zone, BucketManager

auth = Auth(access_key, secret_key)
last_progress = 0
last_record_time = time.time()

# The default qiniu upload host doesn't support uploading files outside China.
# Use up.qiniug.com provided from qiniu's custom service
set_default(default_zone=Zone(QINIU_UPLOAD_URL, QINIU_UPLOAD_URL))


def get_all_uploaded_files():
  sys.stdout.write('Retrieve uploaded file in qiniu...\n')
  sys.stdout.flush()
  bucket = BucketManager(auth)
  marker = None
  eof = False
  uploaded_files = []
  while not eof:
    ret, eof, info = bucket.list(bucket_name, marker=marker)
    marker = ret.get('marker', None)
    for item in ret['items']:
      uploaded_files.append(item['key'])
  return uploaded_files


def upload_progress_handler(progress, total):
  global last_progress, last_record_time
  time_stamp = int(time.time() - last_record_time)
  if time_stamp == 0: return
  upload_speed = (progress - last_progress) / time_stamp
  last_progress = progress
  last_record_time = time.time()
  sys.stdout.write('{0}/{1} MB, {2} KB/s\n'.format(progress/1024/1024,
    total/1024/1024,
    upload_speed/8/1024))
  sys.stdout.flush()


def upload_file(local_file_path, file_name):
  sys.stdout.write('Uploading {0}...\n'.format(local_file_path))
  sys.stdout.flush()

  global last_progress, last_record_time
  last_progress = 0
  last_record_time = time.time()
  token = auth.upload_token(bucket_name, file_name)
  ret, info = put_file(token, file_name, local_file_path,
      mime_type='application/zip', check_crc=True,
      progress_handler=upload_progress_handler)
  return info.status_code == 200


def qiniu_sync_dir(abs_dir_path):
  sys.stdout.write('Syncing to qiniu...\n')
  sys.stdout.flush()
  uploaded_files = get_all_uploaded_files()
  for dir_path, _, file_names in os.walk(abs_dir_path):
    for file_name in file_names:
      if file_name == 'libchromiumcontent.zip' or \
          file_name == 'libchromiumcontent-static.zip':
        # upload_name alias libchromiumcontent download url:
        # [osx|win|linux]/[x64|ia32]/<commit_id>/libchromiumcontent.zip
        upload_name = os.path.join(
            dir_path[([m.start() for m in re.finditer('osx|win|linux', dir_path)][-1]):], file_name)
        if upload_name not in uploaded_files:
          try_times = 0
          while try_times < MAX_TRIES:
            try:
              if upload_file(os.path.join(dir_path, file_name), upload_name):
                sys.stdout.write('Successfully upload {0}\n'.format(upload_name))
                sys.stdout.flush()
                break
              try_times += 1
            except ValueError as e:
              sys.stdout.write('Upload fails, retry again\n'.format(upload_name))
              sys.stdout.flush()
