import numpy as np
import pyasge
import random
from game.gamedata import GameData
from game.gameobjects.gameobject import GameObject
from game.gameobjects.gameobject import GameText
from game.gameobjects.bottle import Bottle
from game.gameobjects.projectile import BottleProjectile
from game.gameobjects.projectile import Drone
from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID
from game.gameobjects.player import Player
from game.gameobjects.enemy import Enemy
from game.gameobjects.enemy import Barman
from game.gameobjects.enemy import Boss
from game.gameobjects.enemy import EnemyID
from enum import Enum
from game.gameobjects.gameobject import GameObject

# from pyfmodex.flags import MODE


class stage(Enum):

    PEACEFUL = 1
    BRAWL = 2
    BOSS = 3
    VICTORY = 4


class GamePlay(GameState):
    cooldown = -1
    red = 1.0
    green = 1.0
    blue = 1.0
    """ The game play state is the core of the game itself.

    The role of this class is to process the game logic, update
    the players positioning and render the resultant game-world.
    The logic for deciding on victory or loss should be handled by
    this class and its update function should return GAME_OVER or
    GAME_WON when the end game state is reached.
    """

    def __init__(self, data: GameData) -> None:
        """ Creates the game world

        Use the constructor to initialise the game world in a "clean"
        state ready for the player. This includes resetting of player's
        health and the enemy positions.

        Args:
            data (GameData): The game's shared data
        """
        super().__init__(data)

        self.red_shader = self.data.renderer.loadPixelShader("/data/shaders/red.frag")
        self.alpha_shader = self.data.renderer.loadPixelShader("/data/shaders/alpha.frag")
        self.green_shader = self.data.renderer.loadPixelShader("/data/shaders/green.frag")
        self.yellow_shader = self.data.renderer.loadPixelShader("/data/shaders/yellow.frag")
        self.test = False

        self.id = GameStateID.GAMEPLAY
        self.data.renderer.setClearColour(pyasge.COLOURS.CORAL)
        self.init_ui()
        # self.init_audio()

        # sets up the camera and points it at the player
        map_mid = [
            self.data.game_map.width * self.data.game_map.tile_size[0] * 0.5,
            self.data.game_map.height * self.data.game_map.tile_size[1] * 0.5
        ]

        self.camera = pyasge.Camera(map_mid, self.data.game_res[0], self.data.game_res[1])

        self.camera.zoom = 1.2
        self.data.ui_bottle = None

        # Game Objects
        self.data.player = Player()
        self.data.bottle_array = []
        self.data.projectile_array = []
        self.data.enemy_projectile_array = []
        self.spawn_bottles()
        self.i = 0
        self.x_dir = 0
        self.y_dir = 0
        self.data.played = False
        self.rave = False

        self.music_screen = GameObject()
        self.music_screen.initialiseSprite("data/images/music_display.png", 20)
        self.music_screen.setPosition(1020, 200)

        self.dj_1 = GameObject()
        self.dj_1.initialiseSprite("data/images/dj_1.png", 0)
        self.dj_1.setPosition(1020, 130)

        self.dj_2 = GameObject()
        self.dj_2.initialiseSprite("data/images/dj_2.png", 0)
        self.dj_2.setPosition(1120, 130)

        # Used for animations
        self.animation_timer = 0
        self.frame = 0

        self.data.stage = stage.PEACEFUL
        self.enemy_array = []
        self.data.drone_array = []
        self.data.damage_array = []
        self.boss = None
        self.spawn_enemies(data)
        self.camera.lookAt(pyasge.Point2D(0, 0))

        self.id = GameStateID.GAMEPLAY
        self.current_scene = GameStateID.GAMEPLAY

        self.animation_timer = 0
        self.frame = 0

    def init_ui(self):
        """Initialises the UI elements"""
        pass

    def init_audio(self):
        self.data.bg_audio_channel.volume = 0
        if not self.data.played:
            self.data.peaceful_audio_channel = self.data.audio_system.play_sound(self.data.peace_audio)
        self.data.peaceful_audio_channel.volume = 1

    def remix_audio(self):
        self.data.peaceful_audio_channel.volume = 0
        if not self.data.played:
            self.data.brawl_audio_channel = self.data.audio_system.play_sound(self.data.brawl_audio)
            self.data.played = True
        self.data.brawl_audio_channel.volume = 0.5

    def let_battle_commence(self):
        self.data.stage = stage.BRAWL
        # self.remix_audio()
        self.data.played = True

    def spawn_enemies(self, data) -> None:
        temp_list = self.data.robot_spawns
        for i in range(20):
            rand_num = random.randint(0, len(temp_list) - 1)
            self.enemy_array.append(Enemy(data, (temp_list[rand_num][0] * 2),  (temp_list[rand_num][1] * 2) - 40))
        self.enemy_array.append(Barman(data, 100, 600))

    def spawn_bottles(self) -> None:
        temp_list = self.data.bottle_spawns
        for i in range(13):
            self.data.bottle_array.append(Bottle(temp_list[i][0] * 2, temp_list[i][1] * 2, random.randint(1, 6), False))

    def click_handler(self, event: pyasge.ClickEvent) -> None:
        if event.button is pyasge.MOUSE.MOUSE_BTN1 and \
                event.action is pyasge.MOUSE.BUTTON_PRESSED:
            self.punch()

        if event.button is pyasge.MOUSE.MOUSE_BTN2 and \
                event.action is pyasge.MOUSE.BUTTON_PRESSED:

            self.data.player.set_destination(event.x, event.y, self.data)

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        """ Listens for mouse movement events from the game engine """
        pass

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        """ Listens for key events from the game engine """

        if event.key is pyasge.KEYS.KEY_E and event.action is pyasge.KEYS.KEY_PRESSED:
            self.pickup()
            self.button()

        if event.key is pyasge.KEYS.KEY_F and event.action is pyasge.KEYS.KEY_PRESSED:
            self.throw(False)

        if event.key is pyasge.KEYS.KEY_W and event.action is pyasge.KEYS.KEY_PRESSED:
            self.y_dir = -1

        if event.key is pyasge.KEYS.KEY_S and event.action is pyasge.KEYS.KEY_PRESSED:
            self.y_dir = 1

        if event.key is pyasge.KEYS.KEY_D and event.action is pyasge.KEYS.KEY_PRESSED:
            self.x_dir = 1
            self.data.player.sprite.flip_flags = pyasge.Sprite.FlipFlags.NORMAL

        if event.key is pyasge.KEYS.KEY_A and event.action is pyasge.KEYS.KEY_PRESSED:
            self.x_dir = -1
            self.data.player.sprite.flip_flags = pyasge.Sprite.FlipFlags.FLIP_X

        if event.key is pyasge.KEYS.KEY_W and event.action is pyasge.KEYS.KEY_RELEASED:
            self.y_dir = 0

        if event.key is pyasge.KEYS.KEY_S and event.action is pyasge.KEYS.KEY_RELEASED:
            self.y_dir = 0

        if event.key is pyasge.KEYS.KEY_D and event.action is pyasge.KEYS.KEY_RELEASED:
            self.x_dir = 0

        if event.key is pyasge.KEYS.KEY_A and event.action is pyasge.KEYS.KEY_RELEASED:
            self.x_dir = 0

    def punch(self):
        for enemy in self.enemy_array:
            if (self.data.player.sprite.midpoint.x + 100) > enemy.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 100) \
                    and (self.data.player.sprite.midpoint.y + 100) > enemy.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 100):
                if self.click_check(enemy.sprite):
                    enemy.hit(self.data.player.damage)
                    self.data.damage_array.append(GameText(str(self.data.player.damage), enemy.sprite.x + random.randint(-20, 20), enemy.sprite.y + random.randint(-20, 20), self.data))
                    if self.data.stage == stage.PEACEFUL and not self.data.played:
                        self.let_battle_commence()
                    if enemy.health <= 0:
                        self.enemy_array.remove(enemy)
        for drone in self.data.drone_array:
            if (self.data.player.sprite.midpoint.x + 100) > drone.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 100) \
                    and (self.data.player.sprite.midpoint.y + 100) > drone.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 100):
                if self.click_check(drone.sprite):
                    drone.impact(self.data)
                    self.data.drone_array.remove(drone)
        if self.data.stage == stage.BOSS:
            if (self.data.player.sprite.midpoint.x + 200) > self.boss.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 200) \
                    and (self.data.player.sprite.midpoint.y + 200) > self.boss.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 200):
                if self.click_check(self.boss.sprite):
                    self.boss.hit(self.data.player.damage)
                    if self.boss.health == 0:
                        self.data.stage = stage.VICTORY

    def console_punch(self):
        for enemy in self.enemy_array:
            if (self.data.player.sprite.midpoint.x + 100) > enemy.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 100) \
                    and (self.data.player.sprite.midpoint.y + 100) > enemy.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 100):
                enemy.hit(self.data.player.damage)
                if self.data.stage == stage.PEACEFUL and not self.data.played:
                    self.let_battle_commence()
                if enemy.health <= 0:
                    self.enemy_array.remove(enemy)
        for drone in self.data.drone_array:
            if (self.data.player.sprite.midpoint.x + 100) > drone.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 100) \
                    and (self.data.player.sprite.midpoint.y + 100) > drone.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 100):
                drone.impact(self.data)
                self.data.drone_array.remove(drone)
        if self.data.stage == stage.BOSS:
            if (self.data.player.sprite.midpoint.x + 200) > self.boss.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 200) \
                    and (self.data.player.sprite.midpoint.y + 200) > self.boss.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 200):
                self.boss.hit(self.data.player.damage)
                if self.boss.health == 0:
                    self.data.stage = stage.VICTORY

    def pickup(self):
        if self.data.player.has_bottle:
            # Player has Bottle
            if self.data.player.health < self.data.player.max_health:
                # Player has taken damage
                self.data.player.previous_health = self.data.player.health
                if self.data.player.bottle_type is not None:
                    self.data.player.health += self.data.player.bottle_type.heal
                if self.data.player.health >= self.data.player.max_health:
                    self.data.player.health = self.data.player.max_health
                self.data.player.has_bottle = False
                self.data.ui_bottle = None
                print("Drank Bottle")
                return
            else:
                # Player is at full health.
                print("Health is full")
        elif not self.data.player.has_bottle:
            # Player does not have Bottle
            for bottle in self.data.bottle_array:
                if (self.data.player.getSpriteCentre()[0] + 100) > bottle.getSpriteCentre()[0] > (
                        self.data.player.getSpriteCentre()[0] - 100) \
                        and (self.data.player.getSpriteCentre()[1] + 100) > bottle.getSpriteCentre()[1] > (
                        self.data.player.getSpriteCentre()[1] - 100):
                    # Bottle close
                    self.data.player.has_bottle = True
                    self.data.player.bottle_type = Bottle(0, 0, bottle.type, True)
                    self.data.bottle_array.remove(bottle)
                    self.data.ui_bottle = Bottle(self.data.player.sprite.x + 8, self.data.player.sprite.y + 110,
                                            self.data.player.bottle_type.type, True)
                    print("Picked up Bottle")
                    return
        else:
            # No bottle  Close
            print("No Bottle to pickup or drink")
            return

    def button(self):
        if (self.data.player.getSpriteCentre()[0] + 200) > self.music_screen.getSpriteCentre()[0] > (self.data.player.getSpriteCentre()[0] - 200) and (self.data.player.getSpriteCentre()[1] + 200) > self.music_screen.getSpriteCentre()[1] > (self.data.player.getSpriteCentre()[1] - 200):
            self.rave = True

    def throw(self, gamepad):
        if not gamepad:
            if self.data.player.has_bottle:
                self.data.projectile_array.append(
                    BottleProjectile(self.data.player.sprite.midpoint.x, self.data.player.sprite.midpoint.y,
                                     self.data.cursor.x, self.data.cursor.y, self.data.player.bottle_type.type, gamepad))
                self.data.ui_bottle = None
                self.data.player.has_bottle = False
        else:
            if self.data.player.has_bottle:
                self.data.projectile_array.append(
                    BottleProjectile(self.data.player.sprite.midpoint.x, self.data.player.sprite.midpoint.y, self.data.inputs.getGamePad().AXIS_RIGHT_X, self.data.inputs.getGamePad().AXIS_RIGHT_Y, self.data.player.bottle_type.type, gamepad))
                self.data.ui_bottle = None
                self.data.player.has_bottle = False

    def collision_check(self, sprite, projectile) -> bool:
        sprite_bounds = sprite.getWorldBounds()
        projectile_bounds = projectile.getWorldBounds()

        if (sprite_bounds.v1.x < projectile_bounds.v3.x) and (sprite_bounds.v3.x > projectile_bounds.v1.x) and (
                sprite_bounds.v1.y < projectile_bounds.v3.y) and (sprite_bounds.v3.y > projectile_bounds.v1.y):
            return True
        return False

    def click_check(self, sprite) -> bool:
        sprite_bounds = sprite.getWorldBounds()

        if sprite_bounds.v1.x < self.data.cursor.x < sprite_bounds.v3.x and sprite_bounds.v1.y < self.data.cursor.y < sprite_bounds.v3.y:
            return True
        return False

    def projectile_handler(self, projectile, enemy):
        if self.collision_check(enemy.sprite, projectile.sprite):
            if projectile.visible:
                if self.data.stage == stage.PEACEFUL and not self.data.played:
                    self.let_battle_commence()
                enemy.hit(projectile.damage)
                self.data.damage_array.append(GameText(str(projectile.damage), enemy.sprite.x + random.randint(-20, 20), enemy.sprite.y + random.randint(-20, 20), self.data))
                if not enemy.alive:
                    self.enemy_array.remove(enemy)
                projectile.impact(enemy.sprite)

    def drone_projectile_handler(self, projectile, drone):
        if self.collision_check(drone.sprite, projectile.sprite):
            drone.impact(self.data)
            if not drone.visible:
                self.data.drone_array.remove(drone)
            projectile.impact(self.data)
            self.data.projectile_array.remove(projectile)

    def player_projectile_handler(self, projectile):
        if self.collision_check(self.data.player.sprite, projectile.sprite) or not projectile.visible:
            projectile.impact(self.data)
            if projectile.type == "Drone":
                self.data.drone_array.remove(projectile)
            else:
                self.data.enemy_projectile_array.remove(projectile)
            self.data.player.health -= projectile.damage

    def boss_projectile_handler(self):
        for projectile in self.data.projectile_array:
            if self.collision_check(self.boss.sprite, projectile.sprite):
                self.boss.hit(projectile.damage)
                if self.boss.health <= 0:
                    self.data.stage = stage.VICTORY
                projectile.impact(self.data)
                self.data.projectile_array.remove(projectile)

    def robot_punch_handler(self, enemy):
        if enemy.type == EnemyID.MELEE:
            if self.collision_check(self.data.player.sprite, enemy.sprite) and enemy.cooldown < 0:
                enemy.cooldown = 5
                self.data.player.hit(enemy.damage)

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """ Simulates deterministic time steps for the game objects"""
        pass

    def colour_cooldown(self, dt) -> None:
        self.cooldown -= dt

        if self.cooldown <= 10:
            self.red = 0.5
            self.blue = 0.5
            self.green = 1
        if self.cooldown <= 9:
            self.red = 0.8
            self.blue = 0.2
            self.green = 0.1
        if self.cooldown <= 8:
            self.red = 0.4
            self.blue = 0.6
            self.green = 0.7
        if self.cooldown <= 7:
            self.red = 0.2
            self.blue = 0.9
            self.green = 0.6
        if self.cooldown <= 6:
            self.red = 0.2
            self.blue = 0.6
            self.green = 0.8
        if self.cooldown <= 5:
            self.red = 0.4
            self.blue = 1
            self.green = 0.6
        if self.cooldown <= 4:
            self.red = 0.8
            self.blue = 0.8
            self.green = 0.8
        if self.cooldown <= 3:
            self.red = 1
            self.blue = 0.4
            self.green = 0.7
        if self.cooldown <= 2:
            self.red = 0.5
            self.blue = 0.5
            self.green = 0.8
        if self.cooldown <= 1:
            self.red = 0.4
            self.blue = 1
            self.green = 0.7

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        """ Updates the game world

        Processes the game world logic. You should handle collisions,
        actions and AI actions here. At present cannonballs are
        updated and so are player collisions with the islands, but
        consider how the ships will react to each other

        Args:
            game_time (pyasge.GameTime): The time between ticks.
        """
        self.data.dt = game_time.fixed_timestep

        if self.data.player.health <= 0:
            self.data.player.setPosition(0, 0)
            self.current_scene = GameStateID.GAME_OVER

        if self.data.ui_bottle is not None:
            if self.data.player.animation_timer == 0:
                if self.data.player.frame == 0:
                    self.data.ui_bottle.sprite.y += 6
                elif self.data.player.frame == 1 or self.data.player.frame == 2:
                    self.data.ui_bottle.sprite.y -= 2
                if self.data.player.frame == 3:
                    self.data.ui_bottle.sprite.y -= 2

        for text in self.data.damage_array:
            text.update_timer(game_time.fixed_timestep)
            if not text.visible:
                self.data.damage_array.remove(text)

        for projectile in self.data.projectile_array:
            projectile.update_movement(game_time.fixed_timestep, self.data)
            for enemy in self.enemy_array:
                self.projectile_handler(projectile, enemy)
            for drone in self.data.drone_array:
                self.drone_projectile_handler(projectile, drone)

        for projectile in self.data.enemy_projectile_array:
            # Clears projectiles far away
            distance_x = projectile.sprite.x - self.data.player.sprite.x
            distance_y = projectile.sprite.y - self.data.player.sprite.y
            if abs(distance_x) > 2000 or abs(distance_y) > 2000:
                self.data.enemy_projectile_array.remove(projectile)

            projectile.update_movement(game_time.fixed_timestep, self.data)
            self.player_projectile_handler(projectile)

        if self.data.stage is stage.BRAWL:
            for enemy in self.enemy_array:
                enemy.update(game_time, self.data.player.sprite.midpoint.x, self.data.player.sprite.midpoint.y, self.data)
                enemy.updateCooldown(game_time.fixed_timestep)
                self.robot_punch_handler(enemy)
            if len(self.enemy_array) == 0:
                self.data.stage = stage.BOSS
                self.boss = Boss(self.data, 2000, 500)

        if self.data.stage is stage.BOSS:
            self.boss.update(game_time, self.data)
            self.boss_projectile_handler()

        if self.data.stage is stage.VICTORY:
            if 2500 < self.data.player.sprite.x < 2600 and 500 < self.data.player.sprite.y < 650:
                self.current_scene = GameStateID.WINNER_WINNER

        for drone in self.data.drone_array:
            drone.update_movement(game_time.fixed_timestep, self.data)
            self.player_projectile_handler(drone)

        self.data.player.update(game_time, self.data)
        self.data.player.update_wasd_movement(game_time.fixed_timestep, self.data, self.x_dir, self.y_dir)

        self.data.player.health_range()
        if self.boss is not None:
            self.boss.boss_health()

        self.update_camera()
        self.update_inputs()

        return self.current_scene

    def update_camera(self):
        """ Updates the camera based on gamepad input"""
        self.camera.lookAt(pyasge.Point2D(self.data.player.sprite.x, self.data.player.sprite.y))
        if self.data.gamepad.connected:
            self.camera.translate(
                self.data.inputs.getGamePad().AXIS_LEFT_X * 10,
                self.data.inputs.getGamePad().AXIS_LEFT_Y * 10, 0.0)

        view = [
            self.data.game_res[0] * 0.5 / self.camera.zoom,
            self.data.game_map.width * 64 - self.data.game_res[0] * 0.5 / self.camera.zoom,
            self.data.game_res[1] * 0.5 / self.camera.zoom,
            self.data.game_map.height * 64 - self.data.game_res[1] * 0.5 / self.camera.zoom
        ]
        self.camera.clamp(view)

    def update_inputs(self):
        """ This is purely example code to show how gamepad events
        can be tracked """
        if self.data.gamepad.connected:
            if self.data.gamepad.A and not self.data.prev_gamepad.A:
                # A button is pressed
                self.pickup()

            if self.data.gamepad.RIGHT_BUMPER and not self.data.prev_gamepad.RIGHT_BUMPER:
                # A button is pressed
                self.throw(True)

            if self.data.gamepad.B and not self.data.prev_gamepad.B:
                # A button is pressed
                self.console_punch()

            elif self.data.gamepad.A and self.data.prev_gamepad.A:
                # A button is being held
                pass
            elif not self.data.gamepad.A and self.data.prev_gamepad.A:
                # A button has been released
                pass

    def render(self, game_time: pyasge.GameTime) -> None:
        """ Renders the game world and the UI """

        self.data.renderer.setViewport(pyasge.Viewport(0, 0, self.data.game_res[0], self.data.game_res[1]))
        self.data.renderer.setProjectionMatrix(self.camera.view)
        self.data.game_map.render(self.data.renderer, game_time)
        self.render_ui()

        if self.data.ui_bottle is not None:
            self.data.renderer.render(self.data.ui_bottle.sprite)

        self.data.renderer.render(self.data.player.sprite)
        self.data.renderer.render(self.dj_1.sprite)
        self.data.renderer.render(self.dj_2.sprite)
        self.data.renderer.render(self.music_screen.sprite)
        self.data.renderer.render(self.data.player.health_bar.sprite)

        if self.boss is not None:
            self.data.renderer.render(self.boss.boss_health_bar.sprite)

        for text in self.data.damage_array:
            self.data.renderer.render(text.sprite)

        for bottle in self.data.bottle_array:
            self.data.renderer.render(bottle.sprite)

        for projectile in self.data.projectile_array:
            projectile.render(self.data.renderer)

        for projectile in self.data.enemy_projectile_array:
            projectile.render(self.data.renderer)

        for drone in self.data.drone_array:
            drone.render(self.data.renderer)

        for enemy in self.enemy_array:
            # self.data.renderer.render(enemy.sprite)
            enemy.render(self.data.renderer)

        if self.data.stage is stage.BOSS:
            self.data.renderer.render(self.boss.sprite)

        for bottle in self.data.bottle_array:
            if (self.data.player.getSpriteCentre()[0] + 50) > bottle.getSpriteCentre()[0] > (
                    self.data.player.getSpriteCentre()[0] - 50) \
                    and (self.data.player.getSpriteCentre()[1] + 50) > bottle.getSpriteCentre()[1] > (
                    self.data.player.getSpriteCentre()[1] - 50):
                self.data.renderer.shader = self.yellow_shader
                self.data.renderer.render(bottle.sprite)

        for enemy in self.enemy_array:
            if (self.data.player.sprite.midpoint.x + 100) > enemy.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 100) \
                    and (self.data.player.sprite.midpoint.y + 100) > enemy.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 100):
                if self.click_check(enemy.sprite):
                    self.data.renderer.shader = self.green_shader
                    enemy.render(self.data.renderer)

        for enemy in self.enemy_array:
            if enemy.previous_health > enemy.health:
                self.data.renderer.shader = self.red_shader
                enemy.render(self.data.renderer)
                enemy.previous_health = enemy.health

        for drone in self.data.drone_array:
            if (self.data.player.sprite.midpoint.x + 100) > drone.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 100) \
                    and (self.data.player.sprite.midpoint.y + 100) > drone.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 100):
                if self.click_check(drone.sprite):
                    self.data.renderer.shader = self.green_shader
                    drone.render(self.data.renderer)

        if self.data.stage == stage.BOSS:
            if (self.data.player.sprite.midpoint.x + 200) > self.boss.sprite.midpoint.x > (
                    self.data.player.sprite.midpoint.x - 200) \
                    and (self.data.player.sprite.midpoint.y + 200) > self.boss.sprite.midpoint.y > (
                    self.data.player.sprite.midpoint.y - 200):
                if self.boss.health <= 0:
                    self.data.stage = stage.VICTORY
                if self.click_check(self.boss.sprite):
                    self.data.renderer.shader = self.green_shader
                    self.data.renderer.render(self.boss.sprite)


        if self.data.player.previous_health > self.data.player.health:
            self.data.renderer.shader = self.red_shader
            self.data.renderer.render(self.data.player.sprite)
            self.data.player.previous_health = self.data.player.health

        self.colour_cooldown(game_time.fixed_timestep)

        if self.rave:
            if self.cooldown < -1:
                self.cooldown = 10
            if self.cooldown > 0:
                self.data.shaders["partytime"].uniform("rgb").set([self.red, self.green, self.blue])
                self.data.renderer.shader = self.data.shaders["partytime"]
                self.data.game_map.render(self.data.renderer, game_time)
            if self.cooldown < 0:
                self.rave = False

    def render_ui(self) -> None:
        """ Render the UI elements and map to the whole window """
        # set a new view that covers the width and height of game
        camera_view = pyasge.CameraView(self.data.renderer.resolution_info.view)
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)

        if Player.health is not Player.health <=0:
            self.data.renderer.render(Player.health - 1)

        # this restores the original camera view
        self.data.renderer.setProjectionMatrix(camera_view)

    def to_world(self, pos: pyasge.Point2D) -> pyasge.Point2D:
        """
        Converts from screen position to world position
        :param pos: The position on the current game window camera
        :return: Its actual/absolute position in the game world
        """
        view = self.camera.view
        x = (view.max_x - view.min_x) / self.data.game_res[0] * pos.x
        y = (view.max_y - view.min_y) / self.data.game_res[1] * pos.y
        x = view.min_x + x
        y = view.min_y + y

        return pyasge.Point2D(x, y)



