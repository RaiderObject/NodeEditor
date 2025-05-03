from collections import OrderedDict
from nodeeditor.node_serializable import Serializable
from nodeeditor.node_graphics_socket import QDMGraphicsSocket

LEFT_TOP = 1
LEFT_BOTTOM = 2
LEFT_CENTER = 3
RIGHT_TOP = 4
RIGHT_BOTTOM = 5
RIGHT_CENTER = 6

DEBUG = False

class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1, multi_edges=True, count_on_this_node_side=1, is_input=False):
        super().__init__()

        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges
        self.count_on_this_node_side = count_on_this_node_side
        self.is_input = is_input
        self.is_output = not self.is_input

        self.grSocket = QDMGraphicsSocket(self, self.socket_type)

        self.setSocketPosition()

        self.edges = []

    def __str__(self):
        return "<Socket %s %s..%s>" % ("ME" if self.is_multi_edges else "SE", hex(id(self))[2:5], hex(id(self))[-3:])

    def setSocketPosition(self):
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side))

    def getSocketPosition(self):
        if DEBUG: print('GSP', self.index, self.position, "node: ", self.node.title)
        res = self.node.getSocketPosition(self.index, self.position, self.count_on_this_node_side)
        if DEBUG: print('RES', res)
        return res

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            print("!W:", "Socket::removeEdge", "wanna remove edge", edge, "from self.edges but it's not in the list!")

    # def hasEdge(self):
    #     return self.edges is not None

    def removeAllEdges(self):
        try:
            # Создаем копию списка, чтобы избежать проблем с модификацией во время итерации
            edges_to_remove = self.edges.copy()
            for edge in edges_to_remove:
                edge.remove()
            self.edges.clear()  # На всякий случай очищаем список полностью
        except Exception as e:
            print(f"Ошибка при удалении рёбер: {str(e)}")
        # self.edges.clear()

    def determineMultiEdges(self, data):
        if 'multi_edges' in data:
            return data['multi_edges']
        else:
            # probably older version of a file, make RIGHT socket multi-edged by default
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('multi_edges', self.is_multi_edges),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        self.is_multi_edges = self.determineMultiEdges(data)
        hashmap[data['id']] = self
        return True
