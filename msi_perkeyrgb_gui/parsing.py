import re
from typing import Tuple

import webcolors


class UnknownIdError(Exception):
    pass


class UnknownPresetError(Exception):
    pass


class ColorParseError(Exception):
    pass


def parse_usb_id(id_arg) -> Tuple[int, int]:
    if isinstance(id_arg, (tuple, list)) and len(id_arg) == 2:
        return tuple(id_arg)
    if re.search("^[0-9a-f]{4}:[0-9a-f]{4}$", id_arg):
        vid, pid = [int(s, 16) for s in id_arg.split(":")]
        return vid, pid
    else:
        raise UnknownIdError(id_arg)


def parse_preset(preset_arg, msi_presets):
    if preset_arg in msi_presets.keys():
        return preset_arg
    else:
        raise UnknownPresetError(preset_arg)


def parse_color(color: str) -> str:
    _color = color.lower()
    try:
        _color = webcolors.name_to_hex(_color)[1:]
    except ValueError:
        pass

    if re.fullmatch("^[0-9a-f]{6}$", _color):  # Color in HTML notation
        return _color
    else:
        raise ColorParseError(f"{color} is not a valid color")
