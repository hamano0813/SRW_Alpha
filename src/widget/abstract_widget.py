#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QTableView, QSpinBox

from structure.generic import Value, Text, SEQUENCE


class AbstractWidget:
    def __init__(self, parent, data_name: str | tuple, **kwargs):
        self.data_set: dict[str, int | str | SEQUENCE] = dict()
        self.data_name = data_name
        self.kwargs = kwargs
        if isinstance(parent, ControlWidget):
            parent.append_child(self)

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        pass


class SingleWidget(AbstractWidget):
    def __init__(self, parent, data_name, structure: Value | Text, **kwargs):
        AbstractWidget.__init__(self, parent, data_name, **kwargs)
        self.structure = structure

    def install(self, data_set: dict[str, int | str], delegate: bool = False) -> bool:
        pass

    def overwrite(self) -> bool:
        self.data_set[self.data_name] = self.delegate()
        return True

    def display(self, data: int | str) -> str:
        pass

    def interpret(self, text: str) -> int | str:
        pass

    def delegate(self) -> int | str:
        pass

    def new(self, parent):
        return self.__class__(parent, self.data_name, self.structure, **self.kwargs)


class ControlWidget(AbstractWidget):
    def __init__(self, parent, data_name, **kwargs):
        super(ControlWidget, self).__init__(parent, data_name, **kwargs)
        self.childs: list[AbstractWidget] = list()

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        self.data_set = data_set
        self.control_child(0)
        return True

    def append_child(self, widget: AbstractWidget) -> bool:
        self.childs.append(widget)
        return True

    def control_child(self, idx: int) -> bool:
        child_data: SEQUENCE = self.data_set.get(self.data_name)
        if child_data:
            for child_widget in self.childs:
                child_widget.install(child_data[idx])
            return True
        return False


class BackgroundWidget:
    def __init__(self, **kwargs):
        self.widgets: dict[str, AbstractWidget] = dict()
        self.kwargs = kwargs

    def __getitem__(self, widget_name: str) -> AbstractWidget | ControlWidget | QWidget | QTableView | QSpinBox:
        return self.widgets.get(widget_name)

    def __setitem__(self, widget_name: str, child_widget: AbstractWidget) -> bool:
        self.widgets[widget_name] = child_widget
        return True
