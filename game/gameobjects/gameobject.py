import pyasge

from game.gamedata import GameData


class GameObject:
    sprite = None
    z_order = 0
    scale = 1

    def __init__(self) -> None:
        pass

    def initialiseSprite(self, file_path, z_input):
        self.sprite = pyasge.Sprite()

        if self.sprite.loadTexture(file_path):
            self.z_order = z_input

    def setZOrder(self, z_input):
        self.z_order = z_input

    def setScale(self, scale_input):
        self.scale = scale_input

    def setPosition(self, x_pos, y_pos):
        self.sprite.x = x_pos
        self.sprite.y = y_pos

    def setXPosition(self, x_pos):
        self.sprite.x = x_pos

    def setYPosition(self, y_pos):
        self.sprite.y = y_pos

    def move(self, dt, x_movement, y_movement):
        self.sprite.x += (x_movement * dt)
        self.sprite.y += (y_movement * dt)

    def moveX(self, dt, x_movement):
        self.sprite.x += (x_movement * dt)

    def moveY(self, dt, y_movement):
        self.sprite.y += (y_movement * dt)

    def width(self) -> float:
        return self.sprite.width

    def height(self) -> float:
        return self.sprite.height

    def getSpriteCentre(self) -> [float, float]:
        return [self.sprite.x - (self.sprite.width / 2), self.sprite.y - (self.sprite.height / 2)]


class GameText:
    sprite = None
    z_order = 0
    scale = 1
    timer = 1
    visible = True

    def __init__(self, text_string, x, y, data: GameData) -> None:
        self.sprite = pyasge.Text(data.fonts["MiniFont"])
        self.sprite.colour = pyasge.COLOURS.ORANGERED
        self.sprite.string = text_string
        self.setPosition(x, y)
        self.sprite.z_order = 200

    def setPosition(self, x_pos, y_pos):
        self.sprite.position = [x_pos, y_pos]

    def update_timer(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.visible = False