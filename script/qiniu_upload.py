#!/usr/bin/env python

from qiniu import Auth, put_file, set_default, Zone, BucketManager
import os
import re

access_key = os.getenv('QINIU_ACCESS_KEY')
secret_key = os.getenv('QINIU_SECRET_KEY')
bucket_name = os.getenv('QINIU_TEST_BUCKET')


auth = Auth(access_key, secret_key)

# The default qiniu upload host doesn't support uploading files outside China.
# Use up.qiniug.com provided from qiniu's custom service
set_default(default_zone=Zone('up.qiniug.com', 'up.qiniug.com'))


def get_all_uploaded_files():
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


def upload_file(local_file_path, file_name):
  print local_file_path
  print file_name
  token = auth.upload_token(bucket_name, file_name)
  ret, info = put_file(token, file_name, local_file_path,
      mime_type='application/zip', check_crc=True)
  return info.status_code == 200


def qiniu_sync_dir(abs_dir_path):
  uploaded_files = get_all_uploaded_files()
  for dir_path, _, file_names in os.walk(abs_dir_path):
    for file_name in file_names:
      # upload_name alias libchromiumcontent download url:
      # [osx|win|linux]/[x64|ia32]/<commit_id>/libchromiumcontent.zip
      upload_name = os.path.join(
          dir_path[re.search('osx|win|linux', dir_path).start():], file_name)
      if upload_name not in uploaded_files:
        upload_file(os.path.join(dir_path, file_name), upload_name)
