from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.core import AstrBotConfig
from astrbot.api import logger
from data.plugins.astrbot_plugin_bilibili_live.blivedm.models.message import (
    DanmakuMessage,
)
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "user-modify-playback-state user-read-playback-state"


@register("astrbot_plugin_blive_spotify", "Flartiny", "", "")
class BliveSpotify(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.context = context
        self.config = config
        client_id = self.config.get("client_id", "")
        client_secret = self.config.get("client_secret", "")
        redirect_uri = self.config.get("redirect_uri", "")

        star = self.context.get_registered_star("astrbot_plugin_bilibili_live")
        self.bilibili_live_plugin = star.star_cls
        self.spotify_client = self._get_spotify_client(
            client_id, client_secret, redirect_uri
        )

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        if self.bilibili_live_plugin:
            self.bilibili_live_plugin.register_message_subscriber(self.spotify_jukebox)

    def _get_spotify_client(self, client_id, client_secret, redirect_uri):
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SCOPE,
            open_browser=False,
        )

        sp = spotipy.Spotify(auth_manager=auth_manager)
        from spotipy.exceptions import SpotifyException
        try:
            user = sp.current_user()
            logger.info(f"✅ Spotify 连接成功！已验证用户：{user['display_name']}")
        except SpotifyException as e:
            logger.error(f"❌ Spotify 连接失败或授权无效: {e}")
        except Exception as e:
            logger.error(f"❌ 发生了一个未知错误: {e}")
        return sp

    async def spotify_jukebox(self, message):
        if isinstance(message, DanmakuMessage):
            content = message.content
            # 形如"点歌 name"
            if content.startswith("点歌"):
                search_query = content[2:]
                results = self.spotify_client.search(
                    q=search_query, type="track", limit=1
                )
                if results["tracks"]["items"]:
                    track_item = results["tracks"]["items"][0]
                    track_uri = track_item["uri"]

                    try:
                        self.spotify_client.add_to_queue(uri=track_uri)
                    except spotipy.exceptions.SpotifyException as e:
                        logger.error("请确认你的 Spotify 账户是 Premium (付费) 会员。")

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        if self.bilibili_live_plugin:
            self.bilibili_live_plugin.unregister_message_subscriber(
                self.spotify_jukebox
            )
