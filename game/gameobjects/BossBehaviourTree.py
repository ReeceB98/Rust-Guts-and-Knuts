from game.gamedata import GameData
import pyasge

from game.gameobjects.BaseTreeNodes import BehaviourTree, Selector, Sequence, Inverter, Leaf, ReturnType


class BossBehaviourTree(BehaviourTree):

    def __init__(self):
        super().__init__()

        self.build_tree()

    def build_tree(self):
        self.root.set_child(Selector())

        self.root.children[0].add_child(Sequence())
        self.root.children[0].children[0].add_child(PlayerLowHealth())
        self.root.children[0].children[0].add_child(Drones())
        self.root.children[0].children[0].add_child(Sequence())
        self.root.children[0].children[0].children[2].add_child(StompRange())
        self.root.children[0].children[0].children[2].add_child(BigStomp())

        self.root.children[0].add_child(Sequence())
        self.root.children[0].children[1].add_child(PlayerHighHealth())

        self.root.children[0].children[1].add_child(Inverter())
        self.root.children[0].children[1].children[1].add_child(Sequence())
        self.root.children[0].children[1].children[1].children[0].add_child(StompRange())
        self.root.children[0].children[1].children[1].children[0].add_child(BigStomp())

        self.root.children[0].children[1].add_child(Sequence())
        self.root.children[0].children[1].children[2].add_child(PlayerFar())
        self.root.children[0].children[1].children[2].add_child(LaunchRocket())

        self.root.children[0].add_child(Selector())
        self.root.children[0].children[2].add_child(Sequence())
        self.root.children[0].children[2].children[0].add_child(StompRange())
        self.root.children[0].children[2].children[0].add_child(BigStomp())
        self.root.children[0].children[2].add_child(Sequence())
        self.root.children[0].children[2].children[1].add_child(PlayerClose())
        self.root.children[0].children[2].children[1].add_child(RapidFire())
        self.root.children[0].children[2].add_child(Sequence())
        self.root.children[0].children[2].children[2].add_child(PlayerMidRange())
        self.root.children[0].children[2].children[2].add_child(OmniOrb())
        self.root.children[0].children[2].add_child(Sequence())
        self.root.children[0].children[2].children[3].add_child(PlayerFar())
        self.root.children[0].children[2].children[3].add_child(ShootRocket())

        self.root.ready()


class Drones(Leaf):

    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        actor.launch_drones(data)
        return ReturnType.RUNNING


class OmniOrb(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        print("omni orb")
        actor.omni_orb(data)
        return ReturnType.RUNNING


class ShootRocket(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        print("shoot rocket")
        actor.shoot_rocket(data)
        return ReturnType.RUNNING


class LaunchRocket(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        print("launch rocket")
        actor.launch_rockets(data)
        return ReturnType.RUNNING


class RapidFire(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        print("rapid fire")
        actor.rapid_firing = True
        return ReturnType.RUNNING


class BigStomp(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        print("big stomp")
        actor.big_stomp(data)
        return ReturnType.RUNNING


class PlayerLowHealth(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        if data.player.health < 30:
            print("low hp")
            return ReturnType.SUCCESS
        return ReturnType.FAILURE


class PlayerHighHealth(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        if data.player.health > 80:
            print("high hp")
            return ReturnType.SUCCESS
        return ReturnType.FAILURE


def in_range(plr_pos, boss_pos, xrange, yrange):
    if boss_pos[0] - xrange < plr_pos[0] < boss_pos[0] + xrange:
        if boss_pos[1] - yrange < plr_pos[1] < boss_pos[1] + yrange:
            return True
    return False


class PlayerClose(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        player_tile = data.game_map.tile(pyasge.Point2D(data.player.sprite.x, data.player.sprite.y))
        boss_pos = data.game_map.tile(pyasge.Point2D(actor.sprite.x, actor.sprite.y))
        if in_range(player_tile, boss_pos, 7, 5):
            print("close range")
            return ReturnType.SUCCESS
        return ReturnType.FAILURE


class PlayerFar(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        player_tile = data.game_map.tile(pyasge.Point2D(data.player.sprite.x, data.player.sprite.y))
        boss_pos = data.game_map.tile(pyasge.Point2D(actor.sprite.x, actor.sprite.y))
        if in_range(player_tile, boss_pos, 17, 10):
            print("far range")
            return ReturnType.SUCCESS
        return ReturnType.FAILURE


class PlayerMidRange(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        player_tile = data.game_map.tile(pyasge.Point2D(data.player.sprite.x, data.player.sprite.y))
        boss_pos = data.game_map.tile(pyasge.Point2D(actor.sprite.x, actor.sprite.y))
        if in_range(player_tile, boss_pos, 12, 10):
            print("mid range")
            return ReturnType.SUCCESS
        return ReturnType.FAILURE


class StompRange(Leaf):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        player_pos = data.game_map.tile(pyasge.Point2D(data.player.sprite.x, data.player.sprite.y))
        boss_pos = data.game_map.tile(pyasge.Point2D(actor.sprite.x, actor.sprite.y))
        if in_range(player_pos, boss_pos, 3, 10):
            print("stomp range")
            return ReturnType.SUCCESS
        return ReturnType.FAILURE
