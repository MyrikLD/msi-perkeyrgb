import logging
import sys

from gi.repository import Gdk

from keyboard import Keyboard
from msi_perkeyrgb.config import load_config, ConfigError
from msi_perkeyrgb.hidapi_wrapping import (
    HIDNotFoundError,
    HIDOpenError,
    HIDLibraryError,
)
from msi_perkeyrgb.msi_keyboard import MSI_Keyboard
from msi_perkeyrgb.parsing import parse_usb_id, UnknownIdError
from .base import BaseHandler

log = logging.getLogger(__name__)
GDK_CONTROL_MASK = 4


def update_kb(model, usb_id, config):
    msi_presets = MSI_Keyboard.get_model_presets(model)
    msi_keymap = MSI_Keyboard.get_model_keymap(model)

    try:
        parsed_usb_id = parse_usb_id(usb_id)
    except UnknownIdError:
        log.error(f"Unknown vendor/product ID: %s", usb_id)
        sys.exit(1)

    try:
        kb = MSI_Keyboard(parsed_usb_id, msi_keymap, msi_presets)
    except HIDLibraryError as e:
        log.error(
            "Cannot open HIDAPI library: %s. "
            'Make sure you have installed libhidapi on your system, then try running "sudo ldconfig" to regenerate library cache.',
            e,
        )
        sys.exit(1)
    except HIDNotFoundError:
        log.error(f"No USB device with ID {usb_id} found.")
        sys.exit(1)
    except HIDOpenError:
        log.error(
            "Cannot open keyboard. Possible causes:\n"
            "- You don't have permissions to open the HID device. Run this program as root, or give yourself read/write permissions to the corresponding /dev/hidraw*. If you have just installed this tool, reboot your computer for the udev rule to take effect.\n"
            "- The USB device is not a HID device."
        )
        sys.exit(1)

    try:
        colors_map, warnings = load_config(config, msi_keymap)
    except ConfigError as e:
        log.error("Error reading config file: %s", e)
        sys.exit(1)

    for w in warnings:
        log.error("Warning: %s", w)

    kb.set_colors(colors_map)
    kb.refresh()


class ConfigHandler(BaseHandler):
    current_key = None

    def __init__(self, model, image, color_selector, colors_filename, usb_id):
        super().__init__(model)
        self.image = image
        self.color_selector = color_selector
        self.colors_filename = colors_filename
        self.usb_id = usb_id

        self.image.connect("draw", self.expose)
        self.keyboard = Keyboard.load_keys(self.bindings_path)

        self.image.set_from_file(self.image_path)
        self.keyboard.load_colors(self.colors_filename)

    def expose(self, area, context):
        for key in self.keyboard:
            box = key.box
            color = key.color
            context.set_source_rgb(
                int(color[:2], 16) / 255.0,
                int(color[2:4], 16) / 255.0,
                int(color[4:], 16) / 255.0,
            )
            context.rectangle(*box[0], box[1][0] - box[0][0], box[1][1] - box[0][1])
            context.fill()

    def image_press(self, obj, button):
        key = self.keyboard.get_xy(button.x, button.y)
        log.info(key)
        self.current_key = key
        color = key.color

        self.color_selector.set_current_rgba(
            Gdk.RGBA(
                int(color[:2], 16) / 255.0,
                int(color[2:4], 16) / 255.0,
                int(color[4:], 16) / 255.0,
                1,
            )
        )

    def image_release(self, obj, button):
        pass

    def key_press(self, obj, button):
        keycode = button.hardware_keycode
        flag = button.state
        shift = bool(int(flag) & GDK_CONTROL_MASK)
        if shift:
            if keycode == 39:
                log.info(f"Save colors to: {self.colors_filename}")
                self.keyboard.save_colors(self.colors_filename)
                update_kb(self.model, self.usb_id, self.colors_filename)
            if keycode == 52:
                log.info(f"Load colors from: {self.colors_filename}")
                self.keyboard.load_colors(self.colors_filename)
                self.image.queue_draw()
            print(keycode)
        else:
            key = self.keyboard.get_keycode(keycode)
            log.info(key or keycode)

    def color_changed(self, color_selection):
        color = color_selection.get_current_rgba()
        rgb = [
            int(color.red * 255),
            int(color.green * 255),
            int(color.blue * 255),
        ]
        text = "".join("%0.2X" % i for i in rgb).lower()
        log.info(f"#{text}")
        if self.current_key:
            self.current_key.color = text
            self.image.queue_draw()

    @staticmethod
    def exit(event):
        sys.exit(1)
