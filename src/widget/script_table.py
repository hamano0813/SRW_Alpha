#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QAction, QCursor, QKeyEvent
from PySide6.QtWidgets import QMenu, QApplication

from structure.generic import SEQUENCE
from widget.array_table import ArrayModel, ArrayTable


def create_annotation(order: dict) -> str:
    code = order["指令码"]
    param1 = order["参数一"]
    param2 = order["参数二"]
    if code == 0x0002:
        return f'顕示背景[{param2:02X}]'
    elif code == 0x0008:
        if param1 == 13:
            return '特效 停止屏幕振動'
        elif param1 == 19:
            return f'特效 在{param2}ms時間内調整屏幕顔色RGB'
        elif param1 == 20:
            return f'特效 持續調整屏幕顔色RGB'
        elif param1 == 22:
            return f'特效 復位屏幕顔色RGB'
        elif param1 == 24:
            exp_str = order["扩展文本"].split(" ")[0]
            return f'特效 屏幕振動一次 幅度[{exp_str}]'
    elif code == 0x0009:
        if param1 == 24:
            exp_str = order["扩展文本"].split(" ")[0]
            return f'特效 屏幕持續振動 幅度[{exp_str}]'
    elif code == 0x0010:
        return '右側説話' if param1 == 0x0004 else '左側説話'
    elif code == 0x0020:
        if param1 == 1:
            return f'播放一次音效[{param2:04X}]'
        elif param1 == 3:
            return f'持續播放音效[{param2:04X}]'
        elif param1 == 4:
            return f'停止播放音效'
    elif code == 0x0021:
        if param1 == 1:
            return f'播放一次音效[{param2:04X}]並跟隨特效'
        if param1 == 3:
            return f'持續播放音效[{param2:04X}]並跟隨特效'
    elif code == 0x0210:
        return '提問'
    elif code == 0x0040:
        if param1 == 0x0004:
            exp = [int(i) for i in order["扩展文本"].split(" ")]
            return f'顕示地図[{param2}] 文字坐標({exp[0]},{exp[1]}) 文字裁取({exp[4]},{exp[5]},{exp[2]},{exp[3]}) 箭頭坐標({exp[6]},{exp[7]})'
    elif code == 0x0004:
        temp = param1 & 0x000F
        if temp == 0x0004:
            return f'右側顕示立繪[{param2}]表情[{(param1 & 0x00F0) >> 4}]'
        elif temp == 0x0008:
            return f'左側顕示立繪[{param2}]表情[{(param1 & 0x00F0) >> 4}]'
        elif temp == 0x0001:
            return f'右側立繪移除'
        elif temp == 0x0002:
            return f'左側立繪移除'
        elif temp == 0x0003:
            return f'兩側立繪移除'
        exp_str = ",".join([i for i in order["扩展文本"].split(" ") if i])
        return f'劇情使用的立繪編號({exp_str})'
    elif code == 0x0080:
        return f'選單，共[{param1 + 1}]個選擇項'
    elif code == 0x0100:
        if param1 == 0x0001:
            return f'跳轉第{int(order["扩展文本"].strip())}行'
        elif param1 == 0x0004:
            return '幕間劇情開始'
        elif param1 == 0x0005:
            return '幕間劇情結束'
        elif param1 == 0x0006:
            return '根據主人公跳轉不同行號'
        else:
            exp = [int(i) for i in order["扩展文本"].split(" ") if i]
            return ",".join([f'第{i + 1}項則跳轉第{exp[i]}行' for i in range(param1)])
    elif code == 0x0400:
        if param1 == 0x0001:
            return f'播放背景音樂[{param2}]'
        if param1 == 0x0002:
            return '停止背景音樂'
    elif code == 0x0401:
        return '停止全部音樂'
    elif code == 0x1000:
        return '触发事件'
    elif code == 0x2000:
        return '操作数值'
    elif code == 0x4000:
        if param1 == 0x0001:
            return "判斷超級係或真實係"
        if param2 == 0x0002:
            return "判斷主人公頭像"
    return ""


class ScriptModel(ArrayModel):
    def __init__(self, parent, columns):
        super(ScriptModel, self).__init__(parent, columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None
        elif orientation == Qt.Horizontal:
            return tuple(self.columns.keys())[section]
        return f"{section:>4d}"

    def data(self, index: QModelIndex, role: int = ...) -> any:
        if role == Qt.DisplayRole:
            if index.column() == 4:
                return create_annotation(self.data_sequence[index.row()])
        return super(ScriptModel, self).data(index, role)

    def flags(self, index: QModelIndex):
        if index.column() == 4:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return super(ScriptModel, self).flags(index)

    def insert_order(self, row: int):
        self.beginInsertRows(QModelIndex(), row, row)
        order = {"指令码": 0, "参数一": 0, "参数二": 0, "扩展字节": 0, "扩展文本": "", "释义": ""}
        self.data_sequence.insert(row, order)
        self.endInsertRows()

    def remove_order(self, row: int):
        self.beginRemoveRows(QModelIndex(), row, row)
        self.data_sequence.pop(row)
        self.endRemoveRows()


class ScriptTable(ArrayTable):
    def __init__(self, parent, data_name, columns, **kwargs):
        super(ScriptTable, self).__init__(parent, data_name, columns, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.right_menu)
        self.alignment = self.kwargs.get('alignment', Qt.AlignVCenter)
        self.horizontalHeader().setProperty('language', 'zh')
        self.setWordWrap(False)

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        array_model = ScriptModel(self, self.columns)
        array_model.install(data_set.get(self.data_name, list()))
        proxy = self.generate_proxy()
        proxy.setSourceModel(array_model)
        self.setModel(proxy)

        if self.kwargs.get('resizeRows', True):
            self.resizeRowsToContents()
            QApplication.processEvents()
        stretch_columns = self.kwargs.get('stretch', (0,))
        for column in stretch_columns:
            self.horizontalHeader().setSectionResizeMode(column, self.horizontalHeader().Stretch)
        self.data_set = data_set

        return True

    def keyPressEvent(self, event: QKeyEvent) -> bool:
        if self.kwargs.get('copy', True):
            if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                return self.copy_range()
            elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                return self.paste_range()
            elif event.key() == Qt.Key_I and event.modifiers() == Qt.ControlModifier:
                return self.insert_row()
            elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:
                return self.remove_row()
            elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
                self.model().sourceModel().undo()
                self.reset()
                return True
        super(ScriptTable, self).keyPressEvent(event)
        return True

    def right_menu(self) -> None:
        right_click_menu = QMenu()
        right_click_menu.setProperty('language', 'zh')
        copy_action = QAction('复制(C)', self)
        copy_action.triggered.connect(self.copy_range)
        paste_action = QAction('粘贴(V)', self)
        paste_action.triggered.connect(self.paste_range)
        insert_action = QAction('插入(I)', self)
        insert_action.triggered.connect(self.insert_row)
        remove_action = QAction('刪除(D)', self)
        remove_action.triggered.connect(self.remove_row)
        right_click_menu.addActions([copy_action, paste_action, insert_action, remove_action])
        right_click_menu.exec_(QCursor().pos())

    def insert_row(self) -> bool:
        if not self.selectedIndexes():
            return False
        row = self.selectedIndexes()[0].row() + 1
        self.model().sourceModel().insert_order(row)
        return True

    def remove_row(self) -> bool:
        if not self.selectedIndexes():
            return False
        row = self.selectedIndexes()[0].row()
        self.model().sourceModel().remove_order(row)
        return True
