import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = ""
SCOPE = "user-modify-playback-state user-read-playback-state"

auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    open_browser=False,
)

sp = spotipy.Spotify(auth_manager=auth_manager)
try:
    user = sp.current_user()
    print(f"✅ Spotify 连接成功！已验证用户：{user['display_name']}")
except SpotifyException as e:
    print(f"❌ Spotify 连接失败或授权无效: {e}")
except Exception as e:
    print(f"❌ 发生了一个未知错误: {e}")
