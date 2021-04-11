import json
import os
import random

from .hidapi_wrapping import (
    HID_Keyboard,
    HIDLibraryError,
    HIDNotFoundError,
    HIDOpenError,
)
from .msiprotocol import make_key_colors_packet, make_refresh_packet
from .protocol_data.keycodes import REGION_KEYCODES
from .protocol_data.msi_keymaps import AVAILABLE_MSI_KEYMAPS
from .protocol_data.presets_index import PRESETS_FILES


class UnknownModelError(Exception):
    pass


class MSIKeyboard:
    presets_files = PRESETS_FILES
    available_msi_keymaps = AVAILABLE_MSI_KEYMAPS
    region_keycodes = REGION_KEYCODES

    def __init__(self, usb_id, msi_keymap, msi_presets):
        self._hid_keyboard = HID_Keyboard(usb_id)
        self._msi_keymap = msi_keymap
        self._msi_presets = msi_presets

    @classmethod
    def get_model_keymap(cls, msi_model):
        for msi_models, msi_keymap in cls.available_msi_keymaps:
            if msi_model in msi_models:
                return msi_keymap

    @classmethod
    def get_model_presets(cls, msi_model):
        for msi_models, filename in cls.presets_files:
            if msi_model in msi_models:
                presets_path = os.path.join(
                    os.path.dirname(__file__), "protocol_data", "presets", filename
                )
                with open(presets_path) as f:
                    msi_presets = json.load(f)

                return msi_presets

    def set_color_all(self, color):
        for region in self.region_keycodes.keys():
            keycodes = self.region_keycodes[region]
            n = len(keycodes)
            colors_values = [color] * n
            colors_map = dict(zip(keycodes, colors_values))

            key_colors_packet = make_key_colors_packet(region, colors_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_random_color_all(self):
        for region in self.region_keycodes.keys():
            keycodes = self.region_keycodes[region]
            n = len(keycodes)
            colors_values = []
            for _ in range(n):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                colors_values.append([r, g, b])
            colors_map = dict(zip(keycodes, colors_values))

            key_colors_packet = make_key_colors_packet(region, colors_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_colors(self, linux_colors_map):
        # Translating from Linux keycodes to MSI's own encoding
        linux_keycodes = linux_colors_map.keys()
        colors = linux_colors_map.values()
        msi_keycodes = [self._msi_keymap[k] for k in linux_keycodes]
        msi_colors_map = dict(zip(msi_keycodes, colors))

        # Sorting requested keycodes by keyboard region
        maps_sorted_by_region = {}
        for keycode in msi_colors_map.keys():
            for region in self.region_keycodes.keys():
                if keycode in self.region_keycodes[region]:
                    if region not in maps_sorted_by_region.keys():
                        maps_sorted_by_region[region] = {}
                    maps_sorted_by_region[region][keycode] = msi_colors_map[keycode]

        # Sending color commands by region
        for region, region_colors_map in maps_sorted_by_region.items():
            key_colors_packet = make_key_colors_packet(region, region_colors_map)
            self._hid_keyboard.send_feature_report(key_colors_packet)

    def set_preset(self, preset):
        feature_reports_list = self._msi_presets[preset]
        for data in feature_reports_list:
            self._hid_keyboard.send_feature_report(bytearray.fromhex(data))

    def refresh(self):
        refresh_packet = make_refresh_packet()
        self._hid_keyboard.send_output_report(refresh_packet)

    @classmethod
    def get(cls, usb_id, msi_keymap, msi_presets):
        try:
            return MSIKeyboard(usb_id, msi_keymap, msi_presets)
        except HIDLibraryError as e:
            print(
                "Cannot open HIDAPI library : %s. "
                "Make sure you have installed libhidapi on your system, "
                'then try running "sudo ldconfig" to regenerate library cache.' % str(e)
            )
        except HIDNotFoundError:
            if not usb_id:
                print(
                    "No MSI keyboards with a known product/vendor IDs were found. "
                    "However, if you think your keyboard should work with this program, "
                    'you can try overriding the ID by adding the option "--id VENDOR_ID:PRODUCT_ID". '
                    "In that case you will also need to give yourself proper read/write permissions "
                    "to the corresponding /dev/hidraw* device."
                )
            else:
                print("No USB device with ID %s found." % usb_id)
        except HIDOpenError:
            print(
                "Cannot open keyboard. Possible causes :\n"
                "- You don't have permissions to open the HID device. "
                "Run this program as root, or give yourself read/write permissions "
                "to the corresponding /dev/hidraw*. "
                "If you have just installed this tool, reboot your computer for the udev rule to take effect.\n"
                "- The USB device is not a HID device."
            )

    @classmethod
    def parse_model(cls, model_arg):
        model_arg_nocase = model_arg.upper()
        for msi_models, _ in cls.available_msi_keymaps:
            for model in msi_models:
                if model == model_arg_nocase:
                    return model

        raise UnknownModelError(model_arg)
