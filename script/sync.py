#!/usr/bin/env python

import errno
import os
import re
import subprocess
import sys

SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
REMOTE_URL = 'http://gh-contractor-zcbenz.s3.amazonaws.com/libchromiumcontent'
CONFIG_FILE_URL = 'https://raw.githubusercontent.com/atom/electron/master/script/lib/config.py'
SAVE_PATH = os.path.join(SOURCE_ROOT, 'download_binaries')

LIBCHROMIUMCONTENT_BINARIES = [
  'libchromiumcontent.zip',
]

PLATFORMS = [
  'osx',
  'win',
  'linux',
]

TARGETS = [
  'x64',
  'ia32',
]


def execute(argv, env=os.environ):
  try:
    output = subprocess.check_output(argv, stderr=subprocess.STDOUT, env=env)
    return output
  except subprocess.CalledProcessError as e:
    print e.output
    raise e


def get_upstream_commit_id():
  args = ['curl', CONFIG_FILE_URL]
  content = execute(args)
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


def download(commit):
  for platform in PLATFORMS:
    for target in TARGETS:
      # Currently there are no ia32 binaries on OS X.
      if platform == 'osx' and target == 'ia32':
        continue
      for binary in LIBCHROMIUMCONTENT_BINARIES:
        download_url = '{0}/{1}/{2}/{3}/{4}'.format(
            REMOTE_URL, platform, target, commit, binary)
        save_dir = '{0}/{1}/{2}/{3}'.format(
            SAVE_PATH, platform, target, commit)
        create_dir_if_needed(save_dir)
        wget_args = ['wget', download_url, '-P', save_dir]
        execute(wget_args)

  commit_file = os.path.join(SAVE_PATH, '.commit')
  with open(commit_file, 'w') as f:
    f.write('{0}\n'.format(commit))


def main():
  create_dir_if_needed(SAVE_PATH)
  commit_id = get_upstream_commit_id()
  if need_download(commit_id):
    download(commit_id)


if __name__ == '__main__':
  sys.exit(main())
