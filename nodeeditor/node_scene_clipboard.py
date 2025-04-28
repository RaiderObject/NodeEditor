from collections import OrderedDict

from node_edge import Edge
from node_graphics_edge import QDMGraphicsEdge
from node_node import Node

DEBUG = False
class SceneClipboard():
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        if DEBUG: print("-- COPY TO CLIPBOARD --")

        sel_nodes, sel_edges, sel_sockets = [], [], {}

        # sort edges and nodes
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket.serialize()
            elif isinstance(item, QDMGraphicsEdge):
                sel_edges.append(item.edge)




        # debug
        if DEBUG: print(" NODES\n       ",sel_nodes)
        if DEBUG: print(" EDGES\n       ",sel_edges)
        if DEBUG: print(" SOCKETS\n       ",sel_sockets)

        # remove all edges that are not connected to a node in our list
        edges_to_remove = []
        for edge in sel_edges:
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                if DEBUG: print('   EDGE is OK, connected with both sides')
                pass
            else:
                if DEBUG: print('    EDGE', edge, "is NOT connected with both sides")
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            sel_edges.remove(edge)

        # make finel list of edges
        edge_final = []
        for edge in sel_edges:
            edge_final.append(edge.serialize())

        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edge_final),

        ])

        # if CUT: aka delete -- remove items
        if delete:
            self.scene.grScene.views()[0].deleteSelected()
            # store our history
            self.scene.history.storeHistory("Cut our elements from scene", setModified=True)

        return data

    def deserializeFromClipboard(self, data):
        hashmap = {}

        # calculate mouse pointer -- scene position
        view = self.scene.grScene.views()[0]
        mouse_scene_pos = view.last_scene_mouse_pos
        if DEBUG: print("view.last_scene_mouse_position", mouse_scene_pos)

        # calculate selected objects, bbox and center
        minx, maxx, miny, maxx = 0, 0, 0, 0
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxx: maxx = y

        bbox_center_x = (minx + maxx) / 2
        bbox_center_y = (miny + maxx) / 2
        if DEBUG: print("bbox_center_x, bbox_center_y", bbox_center_x, bbox_center_y)

        # center = view.mapToScene(view.rect().center())
        # if DEBUG: print("center", center)

        # calculate the offset of the newly creating nodes
        offset_x = mouse_scene_pos.x() - bbox_center_x
        offset_y = mouse_scene_pos.y() - bbox_center_y
        if DEBUG: print("offset_x, offset_y", offset_x, offset_y)

        # create each node
        for node_data in data['nodes']:
            new_node = Node(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)

            # readjust the new node's position
            pos = new_node.pos
            new_node.setPos(pos.x() + offset_x, pos.y() + offset_y)

        # create each edge
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)

        # store history
        self.scene.history.storeHistory("Pasted elements from clipboard", setModified=True)
