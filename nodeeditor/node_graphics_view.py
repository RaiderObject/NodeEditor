from PySide6.QtCore import QEvent, Signal
from PySide6.QtGui import QPainter, Qt, QMouseEvent
from PySide6.QtWidgets import QGraphicsView, QApplication

from nodeeditor.node_edge import EDGE_TYPE_BEZIER, Edge
from nodeeditor.node_graphics_cutline import QDMCutLine
from nodeeditor.node_graphics_edge import QDMGraphicsEdge
from nodeeditor.node_graphics_socket import QDMGraphicsSocket

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3
DEBUG = False

EDGE_DRAG_START_THRESHOLD = 10.0

class QDMGraphicsView(QGraphicsView):
    scenePosChanged = Signal(int, int)

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene
        self.initUI()
        self.setScene(grScene)

        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        # cutline
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)

        # listeners
        self._drag_enter_listeners = []
        self._drop_listeners = []

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform |
                            QPainter.LosslessImageRendering)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag) # Selection Rect Mode

        # enable dropping
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        for callback in self._drag_enter_listeners: callback(event)

    def dropEvent(self, event):
        for callback in self._drop_listeners: callback(event)

    def addDragEnterListener(self, callback):
        self._drag_enter_listeners.append(callback)

    def addDropListener(self, callback):
        self._drop_listeners.append(callback)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):

        item = self.getItemAtClick(event)


        # debug print out
        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print('RMB DEBUG:', item.edge, ' connecting sockets: ',
                                                        item.edge.start_socket, '<-->', item.edge.end_socket)
            if type(item) is QDMGraphicsSocket: print('RMB DEBUG:', item.socket, 'has edges: ', item.socket.edges)
            if item is None:
                print('SCENE:')
                print('     Nodes:')
                for node in self.grScene.scene.nodes: print('         ', node)
                print('     Edges:')
                for edge in self.grScene.scene.edges: print('         ', edge)

        # faking events for enable MMB dragging the scene

        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())

        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event):
        # get the item which we clicked on
        item = self.getItemAtClick(event)


        # we store the position of the last LMB click
        self.last_lmb_click_pos = self.mapToScene(event.pos())

        if DEBUG: print("LMB Click on", item, self.debug_modifires(event))

        # logic
        if hasattr(item, 'node') or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:

                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True


        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        # get the item which we released the mouse button on
        item = self.getItemAtClick(event)

        # logic
        if hasattr(item, 'node') or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                if DEBUG: print("LMB Release + Shift on", item)
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                try:
                    if res: return
                except Exception as e:
                    print("ERROR:", e)

        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.line_points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            return

        # if self.dragMode() == QGraphicsView.RubberBandDrag:
        if self.rubberBandDraggingRectangle:
            self.rubberBandDraggingRectangle = False
            current_selected_items = self.grScene.selectedItems()

            if current_selected_items != self.grScene.scene._last_selected_items:
                if current_selected_items == []:
                    self.grScene.itemsDeselected.emit()
                else:
                    self.grScene.itemSelected.emit()
                self.grScene.scene._last_selected_items = current_selected_items

            return

            # otherwise deselect everything
        if item is None:
            self.grScene.itemsDeselected.emit()

        super().mouseReleaseEvent(event)


    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)



    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def debug_modifires(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "

        return out
    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.grEdge.setDestination(pos.x(), pos.y())
            self.drag_edge.grEdge.update()

        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()

        self.last_scene_mouse_pos = self.mapToScene(event.pos())

        self.scenePosChanged.emit(
            int(self.last_scene_mouse_pos.x()),
            int(self.last_scene_mouse_pos.y())
        )

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            if not self.editingFlag:
                self.deleteSelected()
            else:
                super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.saveToFile("graph.json")
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.loadFromFile("graph.json")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.redo()
        # if event.key() == Qt.Key_H:
        #     print("HISTORY:     len(%d)" % len(self.grScene.scene.history.history_stack),
        #           " -- current_step", self.grScene.scene.history.history_current_step)
        #     ix = 0
        #     for item in self.grScene.scene.history.history_stack:
        #         print("#", ix, "--", item['desc'])
        #         ix += 1
        # else:
        super().keyPressEvent(event)


    def cutIntersectingEdges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.grScene.scene.history.storeHistory("Delete cutted edges", setModified=True)


    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()

            elif hasattr(item, 'node'):
                item.node.remove()

        self.grScene.scene.history.storeHistory("Delete selected", setModified=True)


    def getItemAtClick(self, event):
        """ return the object on which we clicked/released the mouse button """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edgeDragStart(self, item):
        try:
            if DEBUG: print('View::edgeDragStart - Start dragging edge... ')
            if DEBUG: print('View::edgeDragStart -     assign Start Socket to:', item.socket)
            # self.previousEdge = item.socket.edges
            self.drag_start_socket = item.socket
            self.drag_edge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
            if DEBUG: print('View::edgeDragStart -     dragEdge:', self.drag_edge)
        except Exception as e:
            print("%s2 ERROR:",e.__class__.__name__ , e)

    def edgeDragEnd(self, item):
        """ return True if skip the rest of the code"""
        self.mode = MODE_NOOP

        if DEBUG: print('View::edgeDragEnd - Stop dragging edge... ')
        self.drag_edge.remove()
        self.drag_edge = None

        try:
            if type(item) is QDMGraphicsSocket:
                if item.socket != self.drag_start_socket:
                    # if we released dragging on a socket (other than the beginning socket)

                    # we want to keep all the edges coming from a target socket
                    if not item.socket.is_multi_edges:
                        item.socket.removeAllEdges()

                    # we want to keep all the edges coming from a start socket
                    if not self.drag_start_socket.is_multi_edges:
                        self.drag_start_socket.removeAllEdges()

                    new_edge = Edge(self.grScene.scene, self.drag_start_socket, item.socket, edge_type=EDGE_TYPE_BEZIER)
                    if DEBUG: print("View::edgeDragEnd - created new edge:", new_edge, "connecting",
                                    new_edge.start_socket, "<-->", new_edge.end_socket)

                    for socket in [self.drag_start_socket, item.socket]:
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input: socket.node.onInputChanged(new_edge)

                    self.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                    return True
        except Exception as e:
            print("%s3 ERROR:",e.__class__.__name__ , e)


        if DEBUG: print('View::edgeDragEnd - Done')

        return False

    def distanceBetweenClickAndReleaseIsOff(self, event):
        """ mesures if we are too far from the last LMB click position """
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_pos
        edge_drag_treshold_sq = EDGE_DRAG_START_THRESHOLD * EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x() * dist_scene.x() + dist_scene.y() * dist_scene.y()) > edge_drag_treshold_sq

    def wheelEvent(self, event):
        # calculate zoom in/out factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False

        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        # set scene scale factor
        if not clamped or self.zoomClamp is False:

            self.scale(zoomFactor, zoomFactor)


