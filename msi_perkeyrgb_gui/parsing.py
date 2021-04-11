import re
from typing import Tuple


class UnknownIdError(Exception):
    pass


class UnknownPresetError(Exception):
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
