#!/usr/bin/env python

import errno
import threading
import os
import re
import shutil
import subprocess
import sys
import tarfile

from config import CONFIG_FILE_URL, RUN_TIME_INTERVAL, \
                   LIBCHROMIUMCONTENT_BINARIES, PLATFORMS, TARGETS
from qiniu_upload import qiniu_sync_dir

SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SAVE_PATH = os.path.join(SOURCE_ROOT, 'download_binaries')
REMOTE_URL = '';

def execute(argv, env=os.environ):
  try:
    output = subprocess.check_output(argv, stderr=subprocess.STDOUT, env=env)
    return output
  except subprocess.CalledProcessError as e:
    print e.output
    raise e


def get_upstream_commit_id():
  sys.stdout.write('Get upstream lastest commit')
  sys.stdout.flush()
  args = ['curl', CONFIG_FILE_URL]
  content = execute(args)
  url_pattern= re.compile('\'http://([-\w\./]+)')
  global REMOTE_URL
  REMOTE_URL = 'http://{0}'.format(url_pattern.search(content).groups()[0])
  pattern = re.compile('LIBCHROMIUMCONTENT_COMMIT = \'(\w+)\'')
  return pattern.search(content).groups()[0]


def need_download(commit):
  commit_id_file = os.path.join(SAVE_PATH, '.commit')
  download_commit_id = ''
  try:
    with open(commit_id_file, 'r') as f:
      download_commit_id = f.readline().strip()
  except IOError as e:
    if e.errno != errno.ENOENT:
      raise

  return download_commit_id != commit


def create_dir_if_needed(dir_path):
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)


def rm_rf(path):
  try:
    shutil.rmtree(path)
  except OSError as e:
    if e.errno != errno.ENOENT:
      raise


def download(commit):
  sys.stdout.write('Downloading commit: {0} \n'.format(commit))
  sys.stdout.flush()
  for binary in LIBCHROMIUMCONTENT_BINARIES:
    for platform in PLATFORMS:
      for target in TARGETS:
        # Currently there are no ia32 binaries on OS X.
        if platform == 'osx' and target == 'ia32':
          continue
        # arm target is only under linux platform.
        if platform != 'linux' and target == 'arm':
          continue
        download_url = '{0}/{1}/{2}/{3}/{4}'.format(
            REMOTE_URL, platform, target, commit, binary)
        save_dir = '{0}/{1}/{2}/{3}'.format(
            SAVE_PATH, platform, target, commit)
        create_dir_if_needed(save_dir)
        sys.stdout.write('Downloading {0} \n'.format(download_url))
        sys.stdout.flush()
        wget_args = ['wget', '-nc', download_url, '-P', save_dir]
        execute(wget_args)

  commit_file = os.path.join(SAVE_PATH, '.commit')
  with open(commit_file, 'w') as f:
    f.write('{0}\n'.format(commit))


def main():
  create_dir_if_needed(SAVE_PATH)
  commit_id = get_upstream_commit_id()
  if need_download(commit_id):
    # Remove older versions library files for saving disk space.
    rm_rf(SAVE_PATH)
    download(commit_id)
  qiniu_sync_dir(SAVE_PATH)


def set_interval(func, sec):
  def func_wrapper():
    set_interval(func, sec)
    func()
  t = threading.Timer(sec, func_wrapper)
  t.start()
  return t


if __name__ == '__main__':
  main()
  # check update once a day, 24 hours.
  #sys.exit(set_interval(main, RUN_TIME_INTERVAL))
