import pyasge
import math
import random

from game.gameobjects.gameobject import GameObject
from enum import Enum

class BottleID(Enum):
    YELLOW = 1
    ORANGE = 2
    GREEN = 3
    RED = 4
    BLUE = 5
    PURPLE = 6


class Bottle(GameObject):
    type = None

    def __init__(self, x, y, type, ui) -> None:
        self.setType(type)
        self.heal = 20
        self.setPosition(x - self.sprite.width / 2 + 5, y - self.sprite.height - 20)
        if ui:
            self.sprite.scale = 0.5

    def setType(self, num):
        if num == 1 or num == BottleID.YELLOW:
            self.type = BottleID.YELLOW
            self.initialiseSprite("data/images/yellow_bottle.png", 120)
            self.heal = 10
        elif num == 2 or num == BottleID.ORANGE:
            self.type = BottleID.ORANGE
            self.initialiseSprite("data/images/orange_bottle.png", 120)
            self.heal = 20
        elif num == 3 or num == BottleID.ORANGE:
            self.type = BottleID.ORANGE
            self.initialiseSprite("data/images/green_bottle.png", 120)
            self.heal = -10
        elif num == 4 or num == BottleID.RED:
            self.type = BottleID.RED
            self.initialiseSprite("data/images/red_bottle.png", 120)
            self.heal = 50
        elif num == 5 or num == BottleID.BLUE:
            self.type = BottleID.BLUE
            self.initialiseSprite("data/images/blue_bottle.png", 120)
            self.heal = 20
        elif num == 6 or num == BottleID.PURPLE:
            self.type = BottleID.PURPLE
            self.initialiseSprite("data/images/purple_bottle.png", 120)
            self.heal = 90
        else:
            self.type = BottleID.YELLOW
            self.initialiseSprite("data/images/yellow_bottle.png", 120)
            self.heal = 10
