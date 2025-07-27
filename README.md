# x-forward-bot


## ⚙️ 配置

1. 登录你的X，使用Cookie Editor复制自己的cookie，在项目根目录运行`py ./get_cookies.py`，按照提示操作，会自动生成`cookies.json`用于登录X

2. 在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| INTERVAL_SECONDS | 否 | 300 | 轮询间隔（会随机100%-150%） |
| SUBSCRIBE_X_USERS | 是 | 无 | 订阅的X用户与对应群聊，字典表示，例如`{"x_at_username": [123456, random_group_id]}` |


## How to start

1. generate project using `nb create` .
2. create your plugin using `nb plugin create` .
3. writing your plugins under `src/plugins` folder.
4. run your bot using `nb run --reload` .

## Documentation

See [Docs](https://nonebot.dev/)
