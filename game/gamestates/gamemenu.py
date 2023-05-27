import pyasge

from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID
from game.gamedata import GameData


class GameMenu(GameState):
    def __init__(self, gamedata: GameData) -> None:
        super().__init__(gamedata)
        self.id = GameStateID.START_MENU
        self.current_scene = GameStateID.START_MENU

        # Menu
        # Declare sprites
        self.data.background = pyasge.Sprite()
        self.menu_text = None
        self.play_option = None
        self.exit_option = None
        self.menu_cursor = None
        self.menu_option = 0

        self.initMenu()

        self.background_midpoint = pyasge.Point2D(self.data.background.x + 800, self.data.background.y + 400)

        map_mid = [
            self.data.game_map.width * self.data.game_map.tile_size[0] * 0.5,
            self.data.game_map.height * self.data.game_map.tile_size[1] * 0.5
        ]

        self.camera = pyasge.Camera(map_mid, self.data.game_res[0], self.data.game_res[1])
        self.camera.zoom = 0.8

    def initMenu(self) -> None:

        if self.data.background.loadTexture("/data/images/menu_background.jpg"):
            # loaded, so make sure this gets rendered first
            self.data.background.z_order = -100

        self.data.fonts["MainFont"] = self.data.renderer.loadFont("/data/fonts/Bungee-Regular.ttf", 80)
        self.data.fonts["MiniFont"] = self.data.renderer.loadFont("/data/fonts/Bungee-Regular.ttf", 20)
        self.data.fonts["InfoFont"] = self.data.renderer.loadFont("/data/fonts/Bungee-Regular.ttf", 40)
        self.data.fonts["TitleFont"] = self.data.renderer.loadFont("/data/fonts/Bungee-Regular.ttf", 100)
        self.menu_text = pyasge.Text(self.data.fonts["TitleFont"])
        self.menu_text.string = "Rust, Guts and Knuts"
        self.menu_text.position = [(self.data.game_res[0] / 2) - (self.menu_text.width / 2), 120]
        self.menu_text.colour = pyasge.COLOURS.ORANGERED

        self.play_option = pyasge.Text(self.data.fonts["MainFont"])
        self.play_option.string = "START"
        self.play_option.position = [100, 300]
        self.play_option.colour = pyasge.COLOURS.MAGENTA

        self.exit_option = pyasge.Text(self.data.fonts["MainFont"])
        self.exit_option.string = "EXIT"
        self.exit_option.position = [100, 450]
        self.exit_option.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.menu_cursor = pyasge.Text(self.data.fonts["MainFont"])
        self.menu_cursor.string = ">"
        self.menu_cursor.position = [25, 300]
        self.menu_cursor.colour = pyasge.COLOURS.MAGENTA

        self.info_1 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_1.string = "Use WASD to Move"
        self.info_1.position = [20, 900]
        self.info_1.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.info_2 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_2.string = "Use E to pickup and use Items"
        self.info_2.position = [20, 950]
        self.info_2.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.info_3 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_3.string = "Use F to throw items"
        self.info_3.position = [20, 1000]
        self.info_3.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.info_4 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_4.string = "Use Mouse 1 to punch"
        self.info_4.position = [20, 1050]
        self.info_4.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.info_5 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_5.string = "Use Left joystick to Move on console"
        self.info_5.position = [900, 900]
        self.info_5.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.info_6 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_6.string = "Use A to pickup and use Items on console"
        self.info_6.position = [900, 950]
        self.info_6.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.info_7 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_7.string = "Use RB and right joystick to throw items"
        self.info_7.position = [900, 1000]
        self.info_7.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.info_8 = pyasge.Text(self.data.fonts["InfoFont"])
        self.info_8.string = "Use B to punch on console"
        self.info_8.position = [900, 1050]
        self.info_8.colour = pyasge.COLOURS.DEEPSKYBLUE

    def click_handler(self, event: pyasge.ClickEvent) -> None:
        if event.button is pyasge.MOUSE.MOUSE_BTN2 and \
                event.action is pyasge.MOUSE.BUTTON_PRESSED:
            pass

        if event.button is pyasge.MOUSE.MOUSE_BTN1 and \
                event.action is pyasge.MOUSE.BUTTON_PRESSED:
            if self.hover_detection() == 1:
                self.current_scene = GameStateID.GAMEPLAY
            elif self.hover_detection() == 2:
                exit()

    def hover_detection(self) -> int:
        if self.play_option.x < (self.data.cursor.x + self.data.cursor.width / 2) < (self.play_option.x + self.play_option.width)\
                and (self.play_option.y - self.play_option.height) < (self.data.cursor.y + self.data.cursor.height / 2) < self.play_option.y:
            return 1
        elif self.exit_option.x < (self.data.cursor.x + self.data.cursor.width / 2) < (self.exit_option.x + self.exit_option.width)\
                and (self.exit_option.y - self.exit_option.height) < (self.data.cursor.y + self.data.cursor.height / 2) < self.exit_option.y:
            return 2
        else:
            return 0

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        pass

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        pass

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        pass

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        self.camera.lookAt(self.background_midpoint)

        if self.hover_detection() == 1:
            # If start is selected on menu
            self.play_option.colour = pyasge.COLOURS.MAGENTA
            self.exit_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.menu_cursor.position = [self.play_option.x - 75, 300]
        elif self.hover_detection() == 2:
            # If exit is selected on menu
            self.play_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.exit_option.colour = pyasge.COLOURS.MAGENTA
            self.menu_cursor.position = [self.exit_option.x - 75, 450]
        else:
            self.play_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.exit_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.menu_cursor.position = [10000, 450]

        return self.current_scene

    def render(self, game_time: pyasge.GameTime) -> None:
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)

        self.data.renderer.render(self.data.background)
        self.data.renderer.render(self.menu_text)
        self.data.renderer.render(self.play_option)
        self.data.renderer.render(self.exit_option)
        self.data.renderer.render(self.menu_cursor)
        self.data.renderer.render(self.info_1)
        self.data.renderer.render(self.info_2)
        self.data.renderer.render(self.info_3)
        self.data.renderer.render(self.info_4)
        self.data.renderer.render(self.info_5)
        self.data.renderer.render(self.info_6)
        self.data.renderer.render(self.info_7)
        self.data.renderer.render(self.info_8)