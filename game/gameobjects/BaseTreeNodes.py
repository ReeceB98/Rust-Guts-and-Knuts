import pyasge
from enum import IntEnum
from abc import abstractmethod, ABC

from game.gamedata import GameData

# Original behaviour tree and help from Paul Erwich, helped us learn to customise it for our boss.

class NodeType(IntEnum):
    SELECTOR = 1
    SEQUENCE = 2
    DECORATOR = 3
    LEAF = 4


class ReturnType(IntEnum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3


class Blackboard:

    def __init__(self):
        pass


class RootNode:
    def __init__(self):
        self.enabled = True
        self.children = []

    def ready(self):
        if len(self.children) != 1:
            print("Behaviour Tree root should have 1 child")
            self.disable()
            return False
        for child in self.children:
            child.ready()
        return True

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def set_child(self, node):
        self.children.append(node)

    def get_child(self):
        return self.children[0]

    def tick(self, actor, data):
        print("tick")
        return self.children[0].tick(actor, data)


class Node(ABC):
    def __init__(self):
        self.children = []
        self.node_type = None

    @abstractmethod
    def tick(self, actor, data):
        pass

    def add_child(self, node):
        self.children.append(node)


class Composite(Node):
    def __init__(self):
        super().__init__()

    def ready(self):
        if len(self.children) < 1:
            print("Behaviour Tree Composite should have at least 1 child")
        for child in self.children:
            child.ready()

    def tick(self, actor, data):
        pass


class Selector(Composite):  # Returns FAILURE is all nodes are failure
    def __init__(self):
        super().__init__()
        self.node_type = NodeType.SELECTOR

    def tick(self, actor, data):
        for child in self.children:
            response = child.tick(actor, data)

            if response != ReturnType.FAILURE:
                return response

        return ReturnType.FAILURE


class Sequence(Composite):  # Returns success if all nodes are success
    def __init__(self):
        super().__init__()
        self.node_type = NodeType.SEQUENCE

    def tick(self, actor, data):
        for child in self.children:
            response = child.tick(actor, data)

            if response != ReturnType.SUCCESS:
                return response

        return ReturnType.SUCCESS


class Decorator(Node):
    def __init__(self):
        super().__init__()
        self.node_type = NodeType.DECORATOR

    def ready(self):
        if len(self.children) != 1:
            print("Behaviour Tree Decorator should only have 1 child")
        for child in self.children:
            child.ready()

    def tick(self, actor, data):
        pass


class Inverter(Decorator):
    def __init__(self):
        super().__init__()

    def tick(self, actor, data):
        response = self.children[0].tick(actor, data)

        if response == ReturnType.SUCCESS:
            return ReturnType.FAILURE
        if response == ReturnType.FAILURE:
            return ReturnType.SUCCESS
        if response == ReturnType.RUNNING:
            return ReturnType.RUNNING


class Leaf(Node):
    def __init__(self):
        super().__init__()
        self.node_type = NodeType.LEAF

    def ready(self):
        if len(self.children) != 0:
            print("Behaviour Tree Leaf should not have any children")

    def tick(self, actor, data):
        pass


class BehaviourTree:
    def __init__(self):
        self.root = RootNode()
        # self.build_tree()

    @abstractmethod
    def build_tree(self):
        # self.root.ready()
        pass
