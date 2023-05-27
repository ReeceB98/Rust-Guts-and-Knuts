import pyasge
import math
import random
from game.gameobjects.gameobject import GameObject
from game.gameobjects.projectile import BottleProjectile
from game.gameobjects.projectile import Orb
from game.gameobjects.projectile import Rocket
from game.gameobjects.projectile import TargetedRocket
from game.gameobjects.projectile import Shot
from game.gameobjects.projectile import RapidShot
from game.gameobjects.projectile import Drone
from game.gameobjects.BossBehaviourTree import BossBehaviourTree
from game.gamedata import GameData
from enum import Enum


class EnemyID(Enum):
    MELEE = 1
    RANGED = 2
    BARMAN = 3
    DRONE = 4
    HYBRID = 5


class Enemy(GameObject):
    health = 5
    previous_health = 5
    alive = None
    x_destination = None
    y_destination = None
    type = None
    stuck = False
    cooldown = 10
    speed = None

    def __init__(self, data: GameData, x, y) -> None:
        self.initialiseSprite("data/images/enemyIdleAnimation.png", 100)
        self.health = 5
        self.previous_health = 5
        self.speed = 50
        self.damage = 1
        self.alive = True

        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 0
        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 16

        self.sprite.width = 16
        self.sprite.scale = 3
        self.sprite.setMagFilter(pyasge.MagFilter.NEAREST)

        self.animation_timer = 0
        self.frame = 0

        self.setPosition(x - (self.sprite.width / 2) - 10, y - self.sprite.height)

        self.behaviour_tree()

    def behaviour_tree(self):
        num = random.randint(1, 5)
        if num == 1:
            self.type = EnemyID.RANGED
            self.cooldown = 5
        elif num >= 2:
            self.type = EnemyID.MELEE
            self.cooldown = 2.0

    def update(self, game_time: pyasge.GameTime, player_x, player_y, data: GameData) -> None:
        if self.type == EnemyID.MELEE:
            self.set_destination(player_x, player_y, data)
            self.update_movement(game_time.fixed_timestep, data)
        if (self.cooldown < 0 and self.type == EnemyID.RANGED) or (self.stuck and self.cooldown < 0):
            self.cooldown = 5
            data.enemy_projectile_array.append(
                BottleProjectile(self.sprite.midpoint.x, self.sprite.midpoint.y, player_x, player_y,
                                 random.randint(1, 6), False))

    def update_movement(self, dt, data: GameData) -> None:

        if self.x_destination is not None and self.y_destination is not None:
            # Stops jittering
            if abs(self.x_destination - self.sprite.x) > 4 and abs(self.y_destination - self.sprite.y) > 4:
                # Calculates player direction
                x_diff = self.x_destination - self.sprite.x
                y_diff = self.y_destination - self.sprite.y

                # Normalises player Movement
                x_dir = self.normalise(x_diff, y_diff)[0]
                y_dir = self.normalise(x_diff, y_diff)[1]

                off_limits = False

                for bound in data.off_limits:
                    if bound[0] < ((self.sprite.x + self.sprite.width) + (x_dir * self.speed * dt)) / 2 < (
                            bound[0] + bound[2]) \
                            and bound[1] < (
                            (self.sprite.y + self.sprite.height) + (y_dir * self.speed * dt)) / 2 < (
                            bound[1] + bound[3]):
                        off_limits = True
                        self.stuck = True

                if not off_limits:
                    if x_dir < 0:
                        self.sprite.flip_flags = pyasge.Sprite.FlipFlags.FLIP_X
                    if x_dir > 0:
                        self.sprite.flip_flags = pyasge.Sprite.FlipFlags.NORMAL
                    self.stuck = False
                    # Moves player if not into off limits
                    self.sprite.x += (x_dir * self.speed * dt)
                    self.sprite.y += (y_dir * self.speed * dt)

    def set_destination(self, click_x, click_y, data: GameData):
        self.x_destination = click_x
        self.y_destination = click_y

    def normalise(self, x, y) -> [float, float]:
        magnitude = math.sqrt((x * x) + (y * y))

        return [(x / magnitude), (y / magnitude)]

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """The fixed-update function moves the player at a constant speed"""

        self.animation_timer += game_time.fixed_timestep
        if self.animation_timer >= 0.2:
            self.animation_timer = 0
            frame_start = self.frame * self.sprite.width
            self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = frame_start
            self.frame += 1
            if self.frame > 2:
                self.frame = 0

    def render(self, renderer: pyasge.Renderer) -> None:
        if self.alive:
            renderer.render(self.sprite)
            # renderer.render(self.active_frame)

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def updateCooldown(self, dt) -> None:
        self.cooldown -= dt


class Barman(Enemy):
    def __init__(self, data: GameData, x, y) -> None:
        self.initialiseSprite("data/images/barman.png", 100)
        self.health = 1
        self.speed = 200

        self.alive = True

        self.position = pyasge.Point2D(0, 0)
        self.destination = [pyasge.Point2D(0, 0)]
        self.direction = pyasge.Point2D(0, 0)

        self.setPosition(x, y)

        self.type = EnemyID.BARMAN
        self.cooldown = 2.0
        self.burst_delay = 0.25
        self.bottles_thrown = 0

    def update(self, game_time: pyasge.GameTime, player_x, player_y, data: GameData) -> None:
        self.cooldown -= game_time.fixed_timestep
        if self.cooldown < 0:
            self.burst_delay -= game_time.fixed_timestep
            if self.bottles_thrown == 0 and self.burst_delay < 0:
                self.bottles_thrown += 1
                self.burst_delay = 0.25
                data.enemy_projectile_array.append(
                    BottleProjectile(self.sprite.midpoint.x, self.sprite.midpoint.y, player_x, player_y,
                                     random.randint(1, 6), False))
            elif self.bottles_thrown == 1 and self.burst_delay < 0:
                self.cooldown = 10
                self.bottles_thrown = 0
                self.burst_delay = 0.25
                data.enemy_projectile_array.append(
                    BottleProjectile(self.sprite.midpoint.x, self.sprite.midpoint.y, player_x, player_y,
                                     random.randint(1, 6), False))


class Boss(GameObject):
    health = None
    alive = None
    type = None
    cooldown = 10
    reload = 1
    rapid_firing = False
    rapid_timer = 2
    stomp_timer = 5
    shot = 0
    swish = 1
    # North, East, South, West
    compass = [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]

    def __init__(self, data: GameData, x, y) -> None:
        self.initialiseSprite("data/images/bossIdleSheet.png", 100)
        self.health = 100
        self.speed = 200
        self.alive = True
        self.sprite.scale = 6
        self.alternate_fire = - 1

        self.x_destination = None
        self.y_destination = None
        self.landed = False

        self.sprite.setMagFilter(pyasge.MagFilter.NEAREST)
        self.sprite.flip_flags = pyasge.Sprite.FlipFlags.FLIP_X
        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 0
        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 53

        self.tree = BossBehaviourTree()

        self.sprite.width = 53

        self.animation_timer = 0
        self.frame = 0

        # Variables to create boss health
        self.boss_health_bar = GameObject()
        self.boss_health_bar.initialiseSprite("data/images/HealthBar.png", 100)
        self.boss_health_bar.setPosition(2050, 450)
        self.boss_health_bar.sprite.setMagFilter(pyasge.MagFilter.NEAREST)
        self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 216
        self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        self.boss_health_bar.sprite.scale = 8
        self.boss_health_bar.sprite.width = 24

        self.setPosition(x, y)

    def update(self, game_time: pyasge.GameTime, data: GameData) -> None:

        self.animation_timer += game_time.fixed_timestep
        if self.animation_timer >= 0.2:
            self.animation_timer = 0
            frame_start = self.frame * self.sprite.width
            self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = frame_start
            self.frame += 1
            if self.frame > 3:
                self.frame = 0

        if self.update_movement(game_time.fixed_timestep, data):
            if data.player.sprite.midpoint.x - 200 < self.sprite.midpoint.x < data.player.sprite.midpoint.x + 200 and \
            data.player.sprite.midpoint.y - 200 < self.sprite.midpoint.y < data.player.sprite.midpoint.y + 200 and not self.landed:
                data.player.hit(5)
                self.landed = True



        self.reload -= game_time.fixed_timestep
        self.cooldown -= game_time.fixed_timestep
        if self.landed:
            self.stomp_timer -= game_time.fixed_timestep

        if self.reload < 0:
            self.reload = 1
            self.shoot(data)

        if self.cooldown < 0:
            self.cooldown = 5
            self.tree.root.tick(self, data)
            # self.boss_behaviour_tree(data)

        if self.stomp_timer < 0 and self.landed:
            self.set_destination(2000, 500)

        if self.rapid_firing:
            self.rapid_fire(data, game_time.fixed_timestep)

    def boss_behaviour_tree(self, data):
        rand_num = random.randint(1, 6)
        # rand_num = 6
        if rand_num == 1:
            self.omni_orb(data)
        elif rand_num == 2:
            self.shoot_rocket(data)
        elif rand_num == 3:
            self.swish = - self.swish
            self.rapid_firing = True
        elif rand_num == 4:
            self.launch_drones(data)
        elif rand_num == 5:
            self.launch_rockets(data)
        elif rand_num == 6:
            self.big_stomp(data)

    def shoot(self, data: GameData):
        self.alternate_fire = - self.alternate_fire
        if self.alternate_fire > 0:
            data.enemy_projectile_array.append(
                Shot(self.sprite.midpoint.x - 16, self.sprite.midpoint.y + 12, data.player.sprite.x,
                     data.player.sprite.y))
        else:
            data.enemy_projectile_array.append(
                Shot(self.sprite.midpoint.x - 88, self.sprite.midpoint.y + 12, data.player.sprite.x,
                     data.player.sprite.y))

    def omni_orb(self, data: GameData):
        for direction in self.compass:
            data.enemy_projectile_array.append(
                Orb(self.sprite.midpoint.x - 155, self.sprite.midpoint.y + 15, direction[0], direction[1]))

    def shoot_rocket(self, data: GameData):
        temp = 1
        if (self.sprite.x + self.sprite.width - data.player.sprite.x) < 0:
            temp = -1
        for i in range(5):
            data.enemy_projectile_array.append(
                Rocket(self.sprite.midpoint.x, ((self.sprite.midpoint.y - 300) + 100 * i), (- 1 * temp)))

    def launch_rockets(self, data: GameData):
        for i in range(2):
            data.enemy_projectile_array.append(
                TargetedRocket(self.sprite.midpoint.x, ((self.sprite.midpoint.y - 100) + 200 * i), 100, 100))

    def rapid_fire(self, data: GameData, dt):
        self.rapid_timer -= dt
        self.shot += 1
        temp = 1
        if (self.sprite.x + self.sprite.width - data.player.sprite.x) < 0:
            temp = -1
        if self.rapid_timer > 0 and self.shot >= 8:
            data.enemy_projectile_array.append(
                RapidShot(self.sprite.midpoint.x + 45, self.sprite.midpoint.y + 40, - 1 * temp,
                          (self.rapid_timer - 1) * self.swish))
            self.shot = 0
        elif self.rapid_timer < 0:
            self.rapid_firing = False
            self.rapid_timer = 2

    def launch_drones(self, data: GameData):
        for i in range(2):
            data.drone_array.append(
                Drone(self.sprite.midpoint.x + 100, ((self.sprite.midpoint.y - 100) + 200 * i), 100, 100))

    def big_stomp(self, data: GameData):
        self.set_destination(data.player.sprite.x - 150, data.player.sprite.y - 200)
        self.stomp_timer = 6
        self.landed = False

    def set_destination(self, x, y):
        self.x_destination = x
        self.y_destination = y

    def boss_health(self) -> None:
        # States of boss health when attacked.

        if self.health <= 80:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 192
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 70:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 168
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 60:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 144
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 50:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 120
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 40:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 96
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 30:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 72
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 20:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 48
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health <= 10:
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = 24
            self.boss_health_bar.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = 24
        if self.health == 0:
            self.boss_health_bar.setPosition(-100, -100)

    def update_movement(self, dt, data: GameData) -> bool:
        if self.x_destination is not None and self.y_destination is not None:
            if abs(self.x_destination - self.sprite.x) > 4 and abs(self.y_destination - self.sprite.y) > 4:
                # Calculates player direction
                x_diff = self.x_destination - self.sprite.x
                y_diff = self.y_destination - self.sprite.y

                # Normalises player Movement
                x_dir = self.normalise(x_diff, y_diff)[0]
                y_dir = self.normalise(x_diff, y_diff)[1]

                off_limits = False

                for bound in data.off_limits:
                    if bound[0] < ((self.sprite.x + self.sprite.width) + (x_dir * self.speed * dt)) / 2 < (
                            bound[0] + bound[2]) \
                            and bound[1] < (
                            (self.sprite.y + self.sprite.height) + (y_dir * self.speed * dt)) / 2 < (
                            bound[1] + bound[3]):
                        off_limits = True
                        self.stuck = True

                if not off_limits:
                    self.stuck = False
                    # Moves player if not into off limits
                    self.sprite.x += (x_dir * self.speed * dt)
                    self.sprite.y += (y_dir * self.speed * dt)

                    if self.boss_health_bar:
                        self.boss_health_bar.sprite.x += (x_dir * self.speed * dt)
                        self.boss_health_bar.sprite.y += (y_dir * self.speed * dt)
                return False
            else:
                # Boss has Landed
                self.landed = True
                return True
        return False

    def normalise(self, x, y) -> [float, float]:
        magnitude = math.sqrt((x * x) + (y * y))

        return [(x / magnitude), (y / magnitude)]

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
