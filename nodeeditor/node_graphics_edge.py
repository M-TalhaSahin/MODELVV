# -*- coding: utf-8 -*-
"""
A module containing the Graphics representation of an Edge
"""
import math

from qtpy.QtWidgets import QGraphicsPathItem, QWidget, QGraphicsItem
from qtpy.QtGui import QColor, QPen, QPainterPath, QFont, QBrush
from qtpy.QtCore import Qt, QRectF, QPointF
from PyQt5 import QtCore, QtGui

from nodeeditor.node_graphics_edge_path import GraphicsEdgePathBezier, GraphicsEdgePathDirect, GraphicsEdgePathSquare


class QDMGraphicsEdge(QGraphicsPathItem):
    """Base class for Graphics Edge"""
    def __init__(self, edge:'Edge', parent:QWidget=None):
        """
        :param edge: reference to :class:`~nodeeditor.node_edge.Edge`
        :type edge: :class:`~nodeeditor.node_edge.Edge`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance attributes:

            - **edge** - reference to :class:`~nodeeditor.node_edge.Edge`
            - **posSource** - ``[x, y]`` source position in the `Scene`
            - **posDestination** - ``[x, y]`` destination position in the `Scene`
        """
        super().__init__(parent)

        self.edge = edge
        self.nailList = []
        self.edge_labels = []
        # create instance of our path class
        self.pathCalculator = self.determineEdgePathClass()(self)

        # init our flags
        self._last_selected_state = False
        self.hovered = False

        # init our variables
        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self.arrowH = 15
        self.arrowW = 10
        self.arrowO = 28

        self.initAssets()
        self.initUI()

    def setText(self, labels):
        self.edge_labels = labels

    def setNails(self, nails):
        self.nailList = nails

    def initUI(self):
        """Set up this ``QGraphicsPathItem``"""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color = self._default_color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        self._color_hovered = QColor("#FF37A6FF")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(3.0)
        self._pen_selected.setWidthF(3.0)
        self._pen_dragging.setWidthF(3.0)
        self._pen_hovered.setWidthF(5.0)

    def createEdgePathCalculator(self):
        """Create instance of :class:`~nodeeditor.node_graphics_edge_path.GraphicsEdgePathBase`"""
        self.pathCalculator = self.determineEdgePathClass()(self)
        return self.pathCalculator

    def determineEdgePathClass(self):
        """Decide which GraphicsEdgePath class should be used to calculate path according to edge.edge_type value"""
        from nodeeditor.node_edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT, EDGE_TYPE_SQUARE
        if self.edge.edge_type == EDGE_TYPE_BEZIER:
            return GraphicsEdgePathBezier
        if self.edge.edge_type == EDGE_TYPE_DIRECT:
            return GraphicsEdgePathDirect
        if self.edge.edge_type == EDGE_TYPE_SQUARE:
            return GraphicsEdgePathSquare
        else:
            return GraphicsEdgePathBezier

    def makeUnselectable(self):
        """Used for drag edge to disable click detection over this graphics item"""
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setAcceptHoverEvents(False)

    def changeColor(self, color):
        """Change color of the edge from string hex value '#00ff00'"""
        # print("^Called change color to:", color.red(), color.green(), color.blue(), "on edge:", self.edge)
        self._color = QColor(color) if type(color) == str else color
        self._pen = QPen(self._color)
        self._pen.setWidthF(3.0)

    def setColorFromSockets(self) -> bool:
        """Change color according to connected sockets. Returns ``True`` if color can be determined"""
        socket_type_start = self.edge.start_socket.socket_type
        socket_type_end = self.edge.end_socket.socket_type
        if socket_type_start != socket_type_end: return False
        self.changeColor(self.edge.start_socket.grSocket.getSocketColor(socket_type_start))

    def onSelected(self):
        """Our event handling when the edge was selected"""
        self.edge.scene.grScene.itemSelected.emit()

    def doSelect(self, new_state:bool=True):
        """Safe version of selecting the `Graphics Node`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()

    def mouseReleaseEvent(self, event):
        """Overridden Qt's method to handle selecting and deselecting this `Graphics Edge`"""
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def setSource(self, x:float, y:float):
        """ Set source point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.posSource = [x, y]

    def setDestination(self, x:float, y:float):
        """ Set destination point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        """
        self.posDestination = [x, y]

    def boundingRect(self) -> QRectF:
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """Returns ``QPainterPath`` representation of this `Edge`

        :return: path representation
        :rtype: ``QPainterPath``
        """
        return self.calcPath(self.nailList)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Qt's overridden method to paint this Graphics Edge. Path calculated
            in :func:`~nodeeditor.node_graphics_edge.QDMGraphicsEdge.calcPath` method"""
        self.setPath(self.calcPath(self.nailList))
        painter.setBrush(Qt.NoBrush)

        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.drawPath(self.path())
            painter.drawPolyline(self.arrowCalc())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)

        painter.drawPath(self.path())
        painter.drawPolyline(self.arrowCalc())

        painter.setFont(QFont('f1',19,20))
        for lbl in self.edge_labels:
            kind = lbl['lblKind']
            if(kind == "assignment"):
                painter.setPen(QColor(81,81,175) if not self.isSelected() else self._pen_selected)
            elif(kind == "guard"):
                painter.setPen(QColor(122,194,126) if not self.isSelected() else self._pen_selected)
            elif(kind == "synchronisation"):
                painter.setPen(QColor(73,163,171) if not self.isSelected() else self._pen_selected)
            elif(kind == "select"):
                painter.setPen(QColor(165,170,70) if not self.isSelected() else self._pen_selected)
            painter.drawText(lbl['coordX'], lbl['coordY'] + 35, lbl['lblText'])

    def arrowCalc(self):
        pointsList = []
        pointsList.append(self.posSource)
        for nail in self.nailList:
            pointsList.append(nail)
        pointsList.append(self.posDestination)

        dx = pointsList[-2][0] - pointsList[-1][0]
        dy = pointsList[-2][1] - pointsList[-1][1]

        leng = math.sqrt(dx ** 2 + dy ** 2)
        normX, normY = dx / leng, dy / leng

        perpX = -normY
        perpY = normX

        endX = pointsList[-1][0] + self.arrowO * normX
        endY = pointsList[-1][1] + self.arrowO * normY

        leftX = endX + self.arrowH * normX + self.arrowW * perpX
        leftY = endY + self.arrowH * normY + self.arrowW * perpY

        rightX = endX + self.arrowH * normX - self.arrowW * perpX
        rightY = endY + self.arrowH * normY - self.arrowW * perpY

        p1 = QtCore.QPointF(leftX, leftY)
        end = QtCore.QPointF(endX, endY)
        p2 = QtCore.QPointF(rightX, rightY)

        return QtGui.QPolygonF([p1, end, p2])

    def intersectsWith(self, p1:QPointF, p2:QPointF) -> bool:
        """Does this Graphics Edge intersect with the line between point A and point B ?

        :param p1: point A
        :type p1: ``QPointF``
        :param p2: point B
        :type p2: ``QPointF``
        :return: ``True`` if this `Graphics Edge` intersects
        :rtype: ``bool``
        """
        cutpath = QPainterPath(p1)
        for pos in self.nailList:
            cutpath.lineTo(float(pos[0]), float(pos[1]))
        cutpath.lineTo(p2)
        path = self.calcPath(nails)
        return cutpath.intersects(path)

    def calcPath(self, nails) -> QPainterPath:
        """Will handle drawing QPainterPath from Point A to B. Internally there exist self.pathCalculator which
        is an instance of derived :class:`~nodeeditor.node_graphics_edge_path.GraphicsEdgePathBase` class
        containing the actual `calcPath()` function - computing how the edge should look like.

        :returns: ``QPainterPath`` of the edge connecting `source` and `destination`
        :rtype: ``QPainterPath``
        """
        return self.pathCalculator.calcPath(nails)

