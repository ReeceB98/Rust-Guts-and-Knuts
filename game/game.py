import random
import pyasge

from game.gamedata import GameData
from game.gamestates.gamestate import GameStateID
from game.gameobjects.gamemap import GameMap
from game.gamestates.gameplay import GamePlay
from game.gamestates.menu import Menu
from game.gamestates.gamemenu import GameMenu
from game.gamestates.gameover import GameOver
from game.gamestates.gamewon import GameWon
# from pyfmodex.flags import MODE


class MyASGEGame(pyasge.ASGEGame):
    """The ASGE Game in Python."""

    def __init__(self, settings: pyasge.GameSettings):
        """
        The constructor for the game.

        The constructor is responsible for initialising all the needed
        subsystems,during the game's running duration. It directly
        inherits from pyasge.ASGEGame which provides the window
        management and standard game loop.

        :param settings: The game settings
        """
        pyasge.ASGEGame.__init__(self, settings)
        self.data = GameData()
        self.renderer.setBaseResolution(self.data.game_res[0], self.data.game_res[1], pyasge.ResolutionPolicy.MAINTAIN)
        random.seed(a=None, version=2)

        self.data.game_map = GameMap(self.renderer, "./data/map/RobotBar.tmx", self.data)
        self.data.inputs = self.inputs
        self.data.renderer = self.renderer
        self.data.shaders["partytime"] = self.data.renderer.loadPixelShader("/data/shaders/rave.frag")
        self.data.prev_gamepad = self.data.gamepad = self.inputs.getGamePad()

        # setup the background and load the fonts for the game
        # self.init_audio()
        self.init_cursor()
        self.init_fonts()

        # register the key and mouse click handlers for this class
        self.key_id = self.data.inputs.addCallback(pyasge.EventType.E_KEY, self.key_handler)
        self.mouse_id = self.data.inputs.addCallback(pyasge.EventType.E_MOUSE_CLICK, self.click_handler)
        self.mousemove_id = self.data.inputs.addCallback(pyasge.EventType.E_MOUSE_MOVE, self.move_handler)

        # start the game in the menu
        self.menu = GameMenu(self.data)
        self.current_state = self.menu

    def init_cursor(self):
        """Initialises the mouse cursor and hides the OS cursor."""
        self.data.cursor = pyasge.Sprite()
        self.data.cursor.loadTexture("/data/textures/cursors.png")
        self.data.cursor.width = 11
        self.data.cursor.height = 11
        self.data.cursor.src_rect = [0, 0, 11, 11]
        self.data.cursor.scale = 4
        self.data.cursor.setMagFilter(pyasge.MagFilter.NEAREST)
        self.data.cursor.z_order = 100
        self.data.inputs.setCursorMode(pyasge.CursorMode.HIDDEN)

    def init_audio(self) -> None:
        """Plays the background audio."""
        #self.data.audio_system.init()
        self.data.bg_audio = self.data.audio_system.create_sound("./data/audio/menu.ogg", mode=MODE.LOOP_NORMAL)
        self.data.peace_audio = self.data.audio_system.create_sound("./data/audio/peace.ogg", mode=MODE.LOOP_NORMAL)
        self.data.brawl_audio = self.data.audio_system.create_sound("./data/audio/brawl.ogg", mode=MODE.LOOP_NORMAL)
        self.data.bg_audio_channel = self.data.audio_system.play_sound(self.data.bg_audio)
        self.data.bg_audio_channel.volume = 0.25

    def init_fonts(self) -> None:
        """Loads the game fonts."""
        pass

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        """Handles the mouse movement and delegates to the active state."""
        self.data.cursor.x = event.x
        self.data.cursor.y = event.y
        self.data.cursor_last_position_x = event.x
        self.data.cursor_last_position_y = event.y
        self.current_state.move_handler(event)

    def click_handler(self, event: pyasge.ClickEvent) -> None:
        """Forwards click events on to the active state."""
        self.current_state.click_handler(event)

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        """Forwards Key events on to the active state."""
        self.current_state.key_handler(event)
        if event.key == pyasge.KEYS.KEY_ESCAPE:
            self.signalExit()

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """Processes fixed updates."""
        self.current_state.fixed_update(game_time)
        # self.data.audio_system.update()

        if self.data.gamepad.connected and self.data.gamepad.START:
            self.signalExit()

    def update(self, game_time: pyasge.GameTime) -> None:
        self.data.prev_gamepad = self.data.gamepad
        self.data.gamepad = self.inputs.getGamePad()

        # self.data.cursor.x = self.data.cursor_last_position_x
        # self.data.cursor.y = self.data.cursor_last_position_y

        new_state = self.current_state.update(game_time)

        if new_state == self.current_state.id:
            pass
        elif new_state == GameStateID.START_MENU:
            self.gameplay.current_scene = GameStateID.GAMEPLAY
            self.menu.current_scene = GameStateID.START_MENU
            self.current_state = self.menu
        elif new_state == GameStateID.GAMEPLAY:
            self.menu.current_scene = GameStateID.START_MENU
            self.gameplay = GamePlay(self.data)
            self.gameplay.current_scene = GameStateID.GAMEPLAY
            self.current_state = self.gameplay
        elif new_state == GameStateID.WINNER_WINNER:
            self.gameplay.current_scene = GameStateID.GAMEPLAY
            self.won = GameWon(self.data)
            self.won.current_scene = GameStateID.WINNER_WINNER
            self.current_state = self.won
        elif new_state == GameStateID.GAME_OVER:
            self.gameplay.current_scene = GameStateID.GAMEPLAY
            self.lost = GameOver(self.data)
            self.lost.current_scene = GameStateID.GAME_OVER
            self.current_state = self.lost

        self.data.prev_gamepad = self.data.gamepad

    def render(self, game_time: pyasge.GameTime) -> None:
        """Renders the game state and mouse cursor"""
        self.current_state.render(game_time)
        self.data.renderer.shader = None
        self.renderer.render(self.data.cursor)
