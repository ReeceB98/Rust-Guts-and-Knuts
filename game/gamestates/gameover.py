import pyasge

from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID
from game.gamedata import GameData

class GameOver(GameState):
    def __init__(self, gamedata: GameData) -> None:
        super().__init__(gamedata)
        self.id = GameStateID.GAME_OVER
        self.current_scene = GameStateID.GAME_OVER

        # Menu
        # Declare sprites
        self.data.background = pyasge.Sprite()
        self.menu_text = None
        self.restart_option = None
        self.exit_option = None
        self.menu_cursor = None
        self.menu_option = 0

        self.initLoseScreen()

    def initLoseScreen(self) -> None:

        if self.data.background.loadTexture("/data/images/YouLose.jpg"):
            # loaded, so make sure this gets rendered first
            self.data.background.z_order = -100

        self.data.fonts["MainFont"] = self.data.renderer.loadFont("/data/fonts/BebasNeue-Regular.ttf", 80)
        self.data.fonts["TitleFont"] = self.data.renderer.loadFont("/data/fonts/BebasNeue-Regular.ttf", 100)
        self.menu_text = pyasge.Text(self.data.fonts["TitleFont"])
        self.menu_text.string = "GAME OVER"
        self.menu_text.position = [(self.data.game_res[0] / 2) - (self.menu_text.width / 2), 120]
        self.menu_text.colour = pyasge.COLOURS.DARKBLUE

        self.restart_option = pyasge.Text(self.data.fonts["MainFont"])
        self.restart_option.string = "Restart"
        self.restart_option.position = [100, 300]
        self.restart_option.colour = pyasge.COLOURS.MAGENTA

        self.exit_option = pyasge.Text(self.data.fonts["MainFont"])
        self.exit_option.string = "EXIT"
        self.exit_option.position = [100, 450]
        self.exit_option.colour = pyasge.COLOURS.DEEPSKYBLUE

        self.menu_cursor = pyasge.Text(self.data.fonts["MainFont"])
        self.menu_cursor.string = ">"
        self.menu_cursor.position = [25, 300]
        self.menu_cursor.colour = pyasge.COLOURS.MAGENTA

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
        if self.restart_option.x < (self.data.cursor.x + self.data.cursor.width / 2) < (self.restart_option.x + self.restart_option.width)\
                and (self.restart_option.y - self.restart_option.height) < (self.data.cursor.y + self.data.cursor.height / 2) < self.restart_option.y:
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

    def update(self, game_time: pyasge.GameTime) -> None:
        if self.hover_detection() == 1:
            # If start is selected on menu
            self.restart_option.colour = pyasge.COLOURS.MAGENTA
            self.exit_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.menu_cursor.position = [self.restart_option.x - 75, 300]
        elif self.hover_detection() == 2:
            # If exit is selected on menu
            self.restart_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.exit_option.colour = pyasge.COLOURS.MAGENTA
            self.menu_cursor.position = [self.exit_option.x - 75, 450]
        else:
            self.restart_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.exit_option.colour = pyasge.COLOURS.DEEPSKYBLUE
            self.menu_cursor.position = [10000, 450]

        return self.current_scene

    def render(self, game_time: pyasge.GameTime) -> None:
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)

        self.data.renderer.render(self.data.background)
        self.data.renderer.render(self.menu_text)
        self.data.renderer.render(self.restart_option)
        self.data.renderer.render(self.exit_option)
        self.data.renderer.render(self.menu_cursor)


