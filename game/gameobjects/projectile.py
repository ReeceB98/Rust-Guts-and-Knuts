from game.gameobjects.gameobject import GameObject
from game.gamedata import GameData
from game.gameobjects.bottle import BottleID

import pyasge
import math


class baseProjectile(GameObject):
    x_direction = 0
    y_direction = 0
    speed = 500
    damage = 1
    visible = True
    type = None

    def __init__(self) -> None:
        pass

    def render(self, renderer: pyasge.Renderer) -> None:
        if self.visible:
            renderer.render(self.sprite)
            # renderer.render(self.active_frame)

    def set_direction(self, sprite_x, sprite_y, click_x, click_y):
        # Calculates bottle direction
        x_dir = click_x - sprite_x
        y_dir = click_y - sprite_y

        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]

    def update_movement(self, dt, data: GameData):
        # Moves bottle
        self.sprite.x += (self.x_direction * self.speed * dt)
        self.sprite.y += (self.y_direction * self.speed * dt)

    def normalise(self, x, y) -> [float, float]:
        magnitude = math.sqrt((x * x) + (y * y))

        return [(x/magnitude), (y/magnitude)]

    def impact(self, data: GameData):
        self.visible = False


class BottleProjectile(baseProjectile, ):

    def __init__(self, sprite_x, sprite_y, click_x, click_y, colour, gamepad_connected) -> None:
        self.gamepad = gamepad_connected
        if colour == BottleID.YELLOW or colour == 1:
            self.type = BottleID.YELLOW
            self.damage = 5
            self.initialiseSprite("data/images/yellow_bottle.png", 120)
        elif colour == BottleID.ORANGE or colour == 2:
            self.type = BottleID.ORANGE
            self.damage = 5
            self.initialiseSprite("data/images/orange_bottle.png", 120)
        elif colour == BottleID.GREEN or colour == 3:
            self.type = BottleID.GREEN
            self.damage = 5
            self.initialiseSprite("data/images/green_bottle.png", 120)
        elif colour == BottleID.RED or colour == 4:
            self.type = BottleID.RED
            self.damage = 5
            self.initialiseSprite("data/images/red_bottle.png", 120)
        elif colour == BottleID.BLUE or colour == 5:
            self.type = BottleID.BLUE
            self.damage = 5
            self.initialiseSprite("data/images/blue_bottle.png", 120)
        elif colour == BottleID.PURPLE or colour == 6:
            self.type = BottleID.PURPLE
            self.initialiseSprite("data/images/purple_bottle.png", 120)
            self.damage = 5
        else:
            self.type = BottleID.YELLOW
            self.damage = 5
            self.initialiseSprite("data/images/yellow_bottle.png", 120)

        self.setPosition(sprite_x, sprite_y)
        self.set_direction(sprite_x, sprite_y, click_x, click_y)

    def set_direction(self, sprite_x, sprite_y, click_x, click_y):
        if not self.gamepad:
            # Calculates bottle direction
            x_dir = click_x - sprite_x
            y_dir = click_y - sprite_y

            # Normalises bottle Movement
            self.x_direction = self.normalise(x_dir, y_dir)[0]
            self.y_direction = self.normalise(x_dir, y_dir)[1]
        else:
            self.x_direction = self.normalise(click_x, click_y)[0]
            self.y_direction = self.normalise(click_x, click_y)[1]


class Orb(baseProjectile):
    def __init__(self, x_pos, y_pos, x_dir, y_dir) -> None:
        self.initialiseSprite("data/images/orb.png", 100)
        self.sprite.scale = 2
        self.damage = 10
        self.speed = 300
        self.setPosition(x_pos, y_pos)
        self.set_direction(x_pos, y_pos, x_dir, y_dir)

    def set_direction(self, sprite_x, sprite_y, x_dir, y_dir):
        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]


class Rocket(baseProjectile):
    def __init__(self, x_pos, y_pos, x_dir) -> None:
        self.initialiseSprite("data/images/rocket.png", 100)
        self.damage = 10
        self.speed = 400
        self.setPosition(x_pos, y_pos)
        self.set_direction(x_pos, y_pos, x_dir, 0)

    def set_direction(self, sprite_x, sprite_y, x_dir, y_dir):
        # Normalises bottle Movement
        self.x_direction = x_dir


class Shot(baseProjectile):
    def __init__(self, x_pos, y_pos, x_dir, y_dir) -> None:
        self.initialiseSprite("data/images/orb.png", 100)
        self.damage = 1
        self.speed = 500
        self.setPosition(x_pos, y_pos)
        self.set_direction(x_pos, y_pos, x_dir, y_dir)

    def set_direction(self, sprite_x, sprite_y, x_dir, y_dir):
        # Calculates bottle direction
        x_dir = x_dir - sprite_x
        y_dir = y_dir - sprite_y

        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]


class RapidShot(baseProjectile):
    def __init__(self, x_pos, y_pos, x_dir, y_dir) -> None:
        self.initialiseSprite("data/images/orb.png", 100)
        self.damage = 1
        self.speed = 500
        self.setPosition(x_pos, y_pos)
        self.set_direction(x_pos, y_pos, x_dir, y_dir)

    def set_direction(self, sprite_x, sprite_y, x_dir, y_dir):
        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]


class Drone(baseProjectile):
    def __init__(self, x_pos, y_pos, x_dir, y_dir) -> None:
        self.initialiseSprite("data/images/drone.png", 100)
        self.speed = 100
        self.damage = 5
        self.type = "Drone"
        self.setPosition(x_pos, y_pos)
        self.set_direction(x_pos, y_pos, x_dir, y_dir)

    def set_direction(self, sprite_x, sprite_y, x_dir, y_dir):
        # Calculates bottle direction
        x_dir = x_dir - sprite_x
        y_dir = y_dir - sprite_y

        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]

    def update_movement(self, dt, data: GameData):
        # Calculates bottle direction
        x_dir = data.player.sprite.x - self.sprite.x
        y_dir = data.player.sprite.y - self.sprite.y

        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]

        # Moves bottle
        self.sprite.x += (self.x_direction * self.speed * dt)
        self.sprite.y += (self.y_direction * self.speed * dt)


class TargetedRocket(baseProjectile):
    def __init__(self, x_pos, y_pos, x_dir, y_dir) -> None:
        self.initialiseSprite("data/images/Rocket.png", 100)
        self.fuse = 3
        self.damage = 25
        self.compass = [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]
        self.speed = 300
        self.setPosition(x_pos, y_pos)
        self.set_direction(x_pos, y_pos, x_dir, y_dir)

    def set_direction(self, sprite_x, sprite_y, x_dir, y_dir):
        # Calculates bottle direction
        x_dir = x_dir - sprite_x
        y_dir = y_dir - sprite_y

        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]

    def update_movement(self, dt, data: GameData):
        self.fuse -= dt

        # Calculates bottle direction
        x_dir = data.player.sprite.x - self.sprite.x
        y_dir = data.player.sprite.y - self.sprite.y

        # Normalises bottle Movement
        self.x_direction = self.normalise(x_dir, y_dir)[0]
        self.y_direction = self.normalise(x_dir, y_dir)[1]

        # Moves bottle
        self.sprite.x += (self.x_direction * self.speed * dt)
        self.sprite.y += (self.y_direction * self.speed * dt)

        if self.fuse < 0:
            self.explode(data)

    def impact(self, data: GameData):
        self.visible = False

    def explode(self, data: GameData):
        for direction in self.compass:
            data.enemy_projectile_array.append(
                Orb(self.sprite.midpoint.x, self.sprite.midpoint.y, direction[0], direction[1]))
        self.visible = False
