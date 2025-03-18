# 文件概览

本项目分为微信小程序登录界面和 FastAPI 后端两部分。

在运行后端之前，需要进行一项重要的配置操作：在 `app/config` 目录中创建 `secret.py` 文件。该文件中应包含以下内容：

```python
WX_APP_ID = ""
WX_APP_SECRET = ""
JWT_SECRET_KEY = ""
