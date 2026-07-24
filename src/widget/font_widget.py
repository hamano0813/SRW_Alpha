#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PySide6.QtWidgets import QLabel, QGroupBox


class FontLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(FontLabel, self).__init__(*args, **kwargs)
        self.setProperty('language', 'zh')


class FontGroup(QGroupBox):
    def __init__(self, *args, **kwargs):
        super(FontGroup, self).__init__(*args, **kwargs)
        self.setProperty('language', 'zhb')
