import pyasge
import math
from game.gameobjects.gameobject import GameObject
from game.gamedata import GameData


class Player(GameObject):
    # current and destination
    max_health = 100
    health = max_health
    previous_health = health
    damage = 2
    Dead = 0
    speed = None
    x_destination = None
    y_destination = None

    has_bottle = False
    bottle_type = None
    attacking = False

    def __init__(self) -> None:
        # current and destination
        self.speed = 300
        self.alive = True

        self.initialiseSprite("data/images/Idle Sprite Sheet New.png", 1)

        # Makes the sprite not blurry when resized.
        self.sprite.setMagFilter(pyasge.MagFilter.NEAREST)

        # Sets the sprite rectangle to the top position of the sprite sheet.
        # Sets the length of each frame we will use to create the animation.
        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_Y] = 0
        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_Y] = 17

        # Set the sprite height to match length of each frame.
        # Set the scale of sprite.
        self.sprite.height = 17
        self.sprite.scale = 4

        # Sets the speed of the animation.
        # Sets the frames of animation.
        self.animation_timer = 0
        self.frame = 0

        # Variables to create players health
        self.health_bar = GameObject()
        self.health_bar.initialiseSprite("data/images/HealthBar.png", 100)
        self.health_bar.setPosition(195, 185)
        self.health_bar.sprite.setMagFilter(pyasge.MagFilter.NEAREST)
        self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 216
        self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        self.health_bar.sprite.scale = 2
        self.health_bar.sprite.width = 24

        self.setPosition(200, 200)

    def update(self, game_time: pyasge.GameTime, data: GameData) -> None:
        self.update_movement(game_time.fixed_timestep, data)
        self.health_range()

        # Updates the idles sprite of the character.
        self.animation_timer += game_time.fixed_timestep
        if self.animation_timer >= 0.2:
            self.animation_timer = 0
            frame_start = self.frame * self.sprite.height
            self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_Y] = frame_start
            self.frame += 1
            if self.frame > 4:
                self.frame = 0

    def health_range(self) -> None:
        # Changes state of health_bar when hit by enemies.
        if self.health == 100:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 216
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 80:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 192
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 70:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 168
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 60:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 144
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 50:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 120
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 40:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 96
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 30:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 72
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 20:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 48
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 10:
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 24
            self.health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24

    def set_destination(self, click_x, click_y, data: GameData):
        found = False
        for bound in data.off_limits:
            if bound[0] < (click_x / 2) < (bound[0] + bound[2]) and bound[1] < (click_y / 2) < (bound[1] + bound[3]):
                found = True
        if not found:
            self.x_destination = click_x
            self.y_destination = click_y

    def update_movement(self, dt, data: GameData) -> bool:
        if data.gamepad.connected:
            x_dir = data.inputs.getGamePad().AXIS_LEFT_X
            y_dir = data.inputs.getGamePad().AXIS_LEFT_Y
            if abs(x_dir) > 0.1 or abs(y_dir) > 0.1:
                self.move_sprite(data, dt, x_dir, y_dir)

        if self.x_destination is not None and self.y_destination is not None:
            # Stops jittering
            if abs(self.x_destination - self.sprite.x) > 4 and abs(self.y_destination - self.sprite.y) > 4:
                # Calculates player direction
                x_diff = self.x_destination - self.sprite.x
                y_diff = self.y_destination - self.sprite.y

                # Normalises player Movement
                x_dir = self.normalise(x_diff, y_diff)[0]
                y_dir = self.normalise(x_diff, y_diff)[1]

                self.move_sprite(data, dt, x_dir, y_dir)

                return True

    def move_sprite(self, data, dt, x_dir, y_dir):
        off_limits = False
        for bound in data.off_limits:
            if bound[0] < ((self.sprite.x + self.sprite.width * 2) + (x_dir * self.speed * dt)) / 2 < (
                    bound[0] + bound[2]) \
                    and bound[1] < ((self.sprite.y + self.sprite.height * 3 + 10) + (y_dir * self.speed * dt)) / 2 < (
                    bound[1] + bound[3]):
                off_limits = True
        if not off_limits:
            # Moves player if not into off limits
            if x_dir < 0:
                self.sprite.flip_flags = pyasge.Sprite.FlipFlags.FLIP_X
            if x_dir > 0:
                self.sprite.flip_flags = pyasge.Sprite.FlipFlags.NORMAL

            self.sprite.x += (x_dir * self.speed * dt)
            self.sprite.y += (y_dir * self.speed * dt)

            if data.ui_bottle is not None:
                data.ui_bottle.sprite.x += (x_dir * self.speed * dt)
                data.ui_bottle.sprite.y += (y_dir * self.speed * dt)

            if self.health_bar:
                self.health_bar.sprite.x += (x_dir * self.speed * dt)
                self.health_bar.sprite.y += (y_dir * self.speed * dt)

    def update_wasd_movement(self, dt, data: GameData, x_diff, y_diff):
        if abs(x_diff) > 0 or abs(y_diff) > 0:
            self.x_destination = None
            self.y_destination = None

        x_dir = self.normalise(x_diff, y_diff)[0]
        y_dir = self.normalise(x_diff, y_diff)[1]

        self.move_sprite(data, dt, x_dir, y_dir)

    def normalise(self, x, y) -> [float, float]:
        magnitude = math.sqrt((x * x) + (y * y))

        if magnitude != 0:
            return [(x/magnitude), (y/magnitude)]
        return [0, 0]

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
