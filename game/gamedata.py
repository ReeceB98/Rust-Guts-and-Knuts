#import pyasge
# import pyfmodex


class GameData:
    """
    GameData stores the data that needs to be shared

    When using multiple states in a game, you will find that
    some game data needs to be shared. GameData can be used to
    share access to data that the game and any running states may
    need.
    """

    def __init__(self) -> None:
        """MUSIC"""
        """
        self.brawl_audio = None
        self.peaceful_audio_channel = None
        self.bg_audio_channel = None
        self.peace_audio = None
        self.audio_system = pyfmodex.System()
        """
        self.ui_bottle = None
        self.played = None
        self.bottle_spawns = None
        self.robot_spawns = None
        self.drone_array = None
        self.damage_array = None
        self.stage = None
        self.enemy_projectile_array = None
        self.cursor_last_position_y = None
        self.cursor_last_position_x = None
        self.off_limits = None
        self.projectile_array = None
        self.bottle_array = None
        self.player = None
        self.background = None
        self.winbackground = None
        self.losebackground = None
        self.cursor = None
        self.fonts = {}
        self.game_map = None
        self.game_res = [1920, 1080]
        self.inputs = None
        self.gamepad = None
        self.prev_gamepad = None
        self.renderer = None
        self.shaders: dict[str, pyasge.Shader] = {}
        self.dt = None
