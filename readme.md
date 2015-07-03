# libchromiumcontent-qiniu-mirror

A Qiniu mirror for the prebuilt [libchromiumcontent](https://github.com/atom/libchromiumcontent) binaries.

[Electron](https:://github.com/atom/electron) developement requires developers to download the libchromiumcontent
binaries hosting on Amazon Web Service, which is not friendly to Chinese due to
the Internet traffic.

libchromium-qiniu-mirror will download `libchromiumcontent` binaries from
[config.py](https://github.com/atom/electron/blob/master/script/lib/config.py), and upload to Qiniu platform.

##Prerequisties

* Python 2.7
* [Qiniu Python SDK](https://github.com/qiniu/python-sdk/)
* wget
* curl

##Usage

**1. Setup your Qiniu account's access key, secret key and bucket name in `ENVIRONMENT` variable. **

```
export QINIU_ACCESS_KEY="<your-access-key>"
export QINIU_SECRET_KEY="<your-secret-key>"
export QINIU_BUCKET="<your-qiniu-space-name>"
```

**2. Run the script to download and upload to Qiniu.**

```
python script/sync.py
```

##License

MIT
