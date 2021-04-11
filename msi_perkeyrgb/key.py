from typing import Tuple

import gi
from pydantic import BaseModel

gi.require_version("Gtk", "3.0")


class Key(BaseModel):
    box: Tuple[
        Tuple[int, int],
        Tuple[int, int],
    ]
    keycode: int
    name: str
    color: str = "000000"

    def __str__(self):
        return self.json()

    __repr__ = __str__

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return other.keycode == self.keycode
        return False

    def __hash__(self):
        return self.keycode

    def clicked(self, x, y):
        if self.box[0][0] < x < self.box[1][0]:
            if self.box[0][1] < y < self.box[1][1]:
                return True
        return False
