from nonebot import get_plugin_config, get_driver
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from nonebot import logger
from io import StringIO
from twikit import Client
from twikit.media import AnimatedGif, Video
from pathlib import Path
import asyncio
import html
import random

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="x-forward",
    description="Automatically forward X tweets to subscribed groups.",
    usage="",
    config=Config,
)

plugin_config = get_plugin_config(Config)
last_noticed_tweet: dict[str, str] = {}
username_to_id: dict[str, str] = {}
client = Client('ja-JP')
driver = get_driver()

@driver.on_bot_connect
async def on_startup(bot: Bot):
    global ctx
    ctx = bot
    login()
    await start_polling()

@driver.on_bot_disconnect
@driver.on_shutdown
def on_shutdown():
    if isinstance(task, asyncio.Task):
        task.cancel()

def login():
    client.load_cookies('cookies.json')

async def polling_thread(method):
    try:
        while True:
            await method()

            """Add a random delay(100% to 150%)"""
            factor = (1.5 - 1) * random.random() + 1
            await asyncio.sleep(plugin_config.interval_seconds * factor)
    except asyncio.CancelledError:
        logger.info("Polling thread cancelled")
        pass

async def get_user_id(username: str):
    if username in username_to_id:
        return username_to_id[username]
    else:
        user = await client.get_user_by_screen_name(username)
        user_id = user.id
        username_to_id[username] = user_id
        return user_id

async def check_x_update():
    for username in plugin_config.subscribe_x_users:
        logger.info(f"Checking tweets from @{username}")
        try:
            userid = await get_user_id(username)

            """[INFO] count here does not work"""
            last_tweets = await client.get_user_tweets(user_id=userid, tweet_type='Tweets', count=5)
            if not userid in last_noticed_tweet:
                logger.success(f"Refresh last tweet from @{username}")
                last_noticed_tweet[userid] = last_tweets[0].id
                continue

            """Temporarily save last tweet id"""
            temp_last = last_noticed_tweet.get(userid)
            
            """Update last tweet id"""
            last_noticed_tweet[userid] = last_tweets[0].id

            for _, last_tweet in enumerate(last_tweets):
                if last_tweet.id == temp_last:
                    logger.success(f"No more new tweets from @{username}")
                    break

                message = StringIO()
                logger.success(f"New tweet from @{username}")

                """Create text message"""
                message.write(f"X: @{username}\n")
                if last_tweet.retweeted_tweet != None:
                    message.write(f"转发 @{last_tweet.retweeted_tweet.user.screen_name}：\n{last_tweet.retweeted_tweet.full_text}")
                elif last_tweet.is_quote_status and last_tweet.quote != None:
                    message.write(last_tweet.full_text)
                    message.write(f"\n引用： @{last_tweet.quote.user.screen_name}\n")
                    message.write(last_tweet.quote.full_text)
                else:
                    message.write(last_tweet.full_text)

                images: list[MessageSegment] = []
                videos: list[MessageSegment] = []

                """Download media"""
                base_path = Path.cwd()
                if last_tweet.media != None:
                    for media in last_tweet.media:
                        if media.type == 'photo':
                            #await media.download(f'media_{media.id}.jpg')
                            #images.append(create_image_segment(username, str(base_path / f'media_{media.id}.jpg')))
                            images.append(create_image_segment(username, media.media_url))
                        if media.type == 'animated_gif':
                            await media.streams[-1].download(f'media_{media.id}.mp4') if isinstance(media, AnimatedGif) else logger.error("Not AnimatedGif")
                            videos.append(create_video_segment(username, str(base_path / f'media_{media.id}.mp4')))
                        if media.type == 'video':
                            await media.streams[-1].download(f'media_{media.id}.mp4') if isinstance(media, Video) else logger.error("Not Video")
                            videos.append(create_video_segment(username, str(base_path / f'media_{media.id}.mp4')))

                """Create forward message format"""
                msg = [create_text_segment(username, html.unescape(message.getvalue()))]
                msg.extend(images)
                msg.extend(videos)

                logger.debug(msg)

                """Send to subscribed groups"""
                logger.info(message.getvalue())
                for g in plugin_config.subscribe_x_users[username]:
                    await ctx.send_group_forward_msg(group_id=g, messages=msg)
                    logger.success(f"Sending to group {g}")

        except Exception as e:
            logger.error(f"Error checking updates for @{username}: {e}")

async def start_polling():
    global task
    task = asyncio.create_task(polling_thread(check_x_update))

def create_text_segment(username: str, text: str):
    return MessageSegment.node_custom(user_id=0, nickname=username, content=Message(text))

def create_image_segment(username: str, url: str):
    return MessageSegment.node_custom(user_id=0, nickname=username, content=Message(MessageSegment.image(file=url)))

def create_video_segment(username: str, url: str):
    return MessageSegment.node_custom(user_id=0, nickname=username, content=Message(MessageSegment.video(file=url)))