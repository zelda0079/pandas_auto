

from typing import Iterable
from .UIModl import Content


class AbcArgs(object):
    """
    docstring
    """
    pass

    def __init__(self, title, default=None, required=True) -> None:
        self.title = title
        self.default = default
        self.required = required
        self.var_name: str = None

    def set_var_name(self, var_name) -> 'AbcArgs':
        self.var_name = var_name
        return self

    def to_content(self) -> Content:
        raise NotImplementedError


class ColumnSelect(AbcArgs):

    def __init__(self, title, default=None, required=True) -> None:
        super().__init__(title, default=default, required=required)

    def to_content(self) -> Content:
        ct = Content(self.title, 'select', self.var_name,
                     source='data_columns', defaultValue=self.default)
        return ct


class Input(AbcArgs):

    def __init__(self, title, placeholder=None, default=None, required=True) -> None:
        super().__init__(title, default=default, required=required)
        self.placeholder = placeholder

    def to_content(self) -> Content:
        ct = Content(self.title, 'input', self.var_name,
                     defaultValue=self.default)
        return ct


class Select(AbcArgs):

    def __init__(self, title, source, default=None, required=True) -> None:
        super().__init__(title, default=default, required=required)

        if isinstance(source, Iterable):
            source = [{'value': i, 'text': str(v)}
                      for i, v in enumerate(source)]
        self.source = source

    def to_content(self) -> Content:
        ct = Content(self.title, 'select', self.var_name,
                     source=self.source, defaultValue=self.default)
        return ct


class Switch(AbcArgs):

    def __init__(self, title, default=None, required=True) -> None:
        super().__init__(title, default=default, required=required)

    def to_content(self) -> Content:
        ct = Content(self.title, 'switch', self.var_name,
                     defaultValue=self.default)
        return ct
