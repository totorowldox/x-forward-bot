import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter


nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OneBotAdapter)

nonebot.load_plugins("./src/plugins")

nonebot.run()