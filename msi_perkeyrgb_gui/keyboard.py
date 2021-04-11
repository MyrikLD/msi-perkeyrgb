import json
from collections import Counter
from itertools import groupby
from json import JSONDecodeError
from logging import getLogger
from typing import List, Optional

import webcolors

from .key import Key
from .parsing import parse_color

log = getLogger(__name__)

NUMPAD_KEYCODES = [104, 106, 63, 77, *range(79, 92)]
ARROWS_KEYCODES = [111, 113, 116, 114]
F_KEYCODES = [*range(67, 77), 95, 96]
NUM_ROW_KEYCODES = [*range(10, 22)]
CHARACTERS_KEYCODES = [*range(24, 36), *range(38, 49), *range(52, 62), 65]
BULK_KEYCODES = {
    "all": [
        *range(9, 92),
        *range(94, 97),
        *range(104, 109),
        *range(111, 115),
        *range(116, 120),
        127,
        133,
        666,
    ],
    "numpad": NUMPAD_KEYCODES,
    "arrows": ARROWS_KEYCODES,
    "f_row": F_KEYCODES,
    "num_row": NUM_ROW_KEYCODES,
    "characters": CHARACTERS_KEYCODES,
}


class Keyboard:
    keys: List[Key]

    def __init__(self, keys: List[Key]):
        self.keys = list(keys)

    @classmethod
    def load_keys(cls, filename: str):
        try:
            with open(filename) as f:
                keys = json.load(f)
        except FileNotFoundError:
            log.warning("Config not found")
            keys = []
        except JSONDecodeError:
            log.error("Config error")
            keys = []

        keys = sorted(
            {Key(**i) for i in keys},
            key=lambda x: x.keycode,
        )
        return cls(keys)

    def save_keys(self, filename: str):
        with open(filename, "w") as f:
            data = sorted(
                (i.dict() for i in set(self.keys)),
                key=lambda x: x["keycode"],
            )
            json.dump(data, f)

    def load_colors(self, filename: str):
        try:
            with open(filename) as f:
                lines = [i for i in f.read().splitlines() if i]
        except FileNotFoundError:
            log.error("Color config %s not found", filename)
            return

        for line in lines:
            keys, state, color = line.split(" ")

            keys = keys.split(",")
            parsed_keys = []
            for i in keys:
                if i == "all":
                    parsed_keys.extend(list(self.keys))
                elif i in BULK_KEYCODES:
                    parsed_keys.extend(self.get_keycode(j) for j in BULK_KEYCODES[i])
                else:
                    parsed_keys.append(self.get_keycode(int(i)))
            for key in parsed_keys:
                key.color = parse_color(color)

    def save_colors(self, filename: str):
        lines = []

        def color_name(c):
            try:
                c = webcolors.hex_to_name(f"#{c}")
            except ValueError:
                pass
            return c

        def eq(colors):
            return colors[0] if len(set(colors)) == 1 else None

        colors = Counter([i.color for i in self.keys])
        main_color = sorted(colors.items(), key=lambda x: x[1])[-1][0]
        lines.append(f"all steady {color_name(main_color)}")

        exclude = set()

        for k, v in BULK_KEYCODES.items():
            bulk = [key.color for key in (self.get_keycode(kc) for kc in v) if key]
            color = eq(bulk)
            if color and color != main_color:
                lines.append(f"{k} steady {color_name(color)}")
                exclude.update(v)

        last_keys = [
            i for i in self.keys if i.keycode not in exclude and i.color != main_color
        ]

        for color, keys in groupby(
            sorted(last_keys, key=lambda x: x.color), lambda x: x.color
        ):
            keycodes = sorted(i.keycode for i in keys)
            text = ",".join(str(i) for i in keycodes)

            lines.append(f"{text} steady {color_name(color)}")

        with open(filename, "w") as f:
            f.writelines([i + "\n" for i in lines])

    def get_xy(self, x: int, y: int) -> Optional[Key]:
        for key in self:
            if key.clicked(x, y):
                return key
        log.debug(f"Unknown key position: (%i,%i)", x, y)

    def get_keycode(self, keycode: int) -> Optional[Key]:
        for i in self:
            if i.keycode == keycode:
                return i
        log.warning(f"Unknown keycode: {keycode}")

    def __iter__(self):
        for i in self.keys:
            yield i
