# coding:utf-8
'''
QGraphicsScene的子类

'''
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtCore import QLine
import math
import PySide6
from base.XF_Config import Config

from widgets.XF_DeviceWidget import Device
from widgets.XF_LineWidget import LineWidget

from devices.XF_MCU import MCU
from devices.XF_LED import LED
from devices.XF_Button import Button

import logging

"""
中央场景控件
"""


class VisualGraphScene(QGraphicsScene):

    def __init__(self, parent=None):

        super().__init__(parent)
        config = Config()

        self.setBackgroundBrush(QBrush(QColor('#212121')))

        self._width = config.EditorConfig["editor_scene_width"]
        self._height = config.EditorConfig["editor_scene_height"]
        self._grid_size = config.EditorConfig["editor_scene_grid_size"]
        self._chunk_size = config.EditorConfig["editor_scene_grid_chunk"]
        # 设置背景大小
        self.setSceneRect(-self._width/2, -self._height /
                          2, self._width, self._height)

        # 画网格
        self._normal_line_pen = QPen(
            QColor(config.EditorConfig["editor_scene_grid_normal_line_color"]))
        self._normal_line_pen.setWidthF(
            config.EditorConfig["editor_scene_grid_normal_line_width"])

        self._dark_line_pen = QPen(
            QColor(config.EditorConfig["editor_scene_grid_dark_line_color"]))
        self._dark_line_pen.setWidthF(
            config.EditorConfig["editor_scene_grid_dark_line_width"])

        self.setItemIndexMethod(QGraphicsScene.NoIndex)

    def drawBackground(self, painter: PySide6.QtGui.QPainter, rect) -> None:

        super().drawBackground(painter, rect)

        lines, drak_lines = self.calGridLines(rect)
        # 画普通的线
        painter.setPen(self._normal_line_pen)
        painter.drawLines(lines)

        # 画粗线
        painter.setPen(self._dark_line_pen)
        painter.drawLines(drak_lines)

    def calGridLines(self, rect):
        left, right, top, bottom = math.floor(rect.left()), math.floor(
            rect.right()), math.floor(rect.top()), math.floor(rect.bottom())

        first_left = left - (left % self._grid_size)
        first_top = top - (top % self._grid_size)

        lines = []
        drak_lines = []
        # 画横线
        for v in range(first_top, bottom, self._grid_size):

            line = QLine(left, v, right, v)

            if v % (self._grid_size * self._chunk_size) == 0:
                drak_lines.append(line)
            else:
                lines.append(line)

        # 画竖线
        for h in range(first_left, right, self._grid_size):

            line = QLine(h, top, h, bottom)

            if h % (self._grid_size * self._chunk_size) == 0:
                drak_lines.append(line)
            else:
                lines.append(line)

        return lines, drak_lines

    def dump(self):
        data = {}
        items = self.items()
        for item in items:
            if isinstance(item, Device) or isinstance(item, LineWidget):
                key = type(item).__name__
                if key not in data:
                    data[type(item).__name__] = []
                data[type(item).__name__].append(item.dump())
        logging.info(f"dump data:{data}")
        return data

    def load(self, data, is_same_id=True):
        for key, values in data.items():
            if key == "MCU":
                for value in values:
                    dev = MCU.load(self, value, is_same_id)
                    dev.setSelected(True)
            elif key == "LED":
                for value in values:
                    dev = LED.load(self, value, is_same_id)
                    dev.setSelected(True)
            elif key == "Button":
                for value in values:
                    dev = Button.load(self, value, is_same_id)
                    dev.setSelected(True)

        for key, values in data.items():
            if key != "LineWidget":
                continue
            for view in self.views():
                for value in values:
                    view.connectWithInfo(value)
