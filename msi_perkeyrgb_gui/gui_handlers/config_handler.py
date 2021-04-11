import logging
import os
import sys

from gi.repository import Gdk

from .base import BaseHandler
from .open_file_dialog import OpenFileDialog
from ..config import load_config, ConfigError
from ..keyboard import Keyboard
from ..msikeyboard import MSIKeyboard
from ..parsing import parse_usb_id, UnknownIdError

log = logging.getLogger(__name__)
GDK_CONTROL_MASK = 4


def update_kb(model, usb_id, config):
    msi_presets = MSIKeyboard.get_model_presets(model)
    msi_keymap = MSIKeyboard.get_model_keymap(model)

    try:
        parsed_usb_id = parse_usb_id(usb_id)
    except UnknownIdError:
        log.error(f"Unknown vendor/product ID: %s", usb_id)
        sys.exit(1)

    kb = MSIKeyboard.get(parsed_usb_id, msi_keymap, msi_presets)
    if not kb:
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
        if not os.path.isfile(self.colors_filename):
            self.keyboard.save_colors(self.colors_filename)

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
        if not key:
            return
        log.info("Choose key %r: #%s", key.name, key.color.upper())
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

    def key_press(self, obj, button):
        keycode = button.hardware_keycode
        flag = button.state
        shift = bool(int(flag) & GDK_CONTROL_MASK)
        if shift:
            key = self.keyboard.get_keycode(keycode)
            if keycode == 39 or key.name == "s":
                log.info(f"Save colors to: {self.colors_filename}")
                self.keyboard.save_colors(self.colors_filename)
                update_kb(self.model, self.usb_id, self.colors_filename)
            elif keycode == 52 or key.name == "x":
                log.info(f"Load colors from: {self.colors_filename}")
                self.keyboard.load_colors(self.colors_filename)
                self.image.queue_draw()
            elif keycode == 32 or key.name == "o":
                file_path = OpenFileDialog.open(self.color_selector.get_parent())
                if file_path:
                    self.colors_filename = file_path

                    self.keyboard.load_colors(self.colors_filename)
                    self.image.queue_draw()
                    log.info(f"Config file opened: {self.colors_filename}")
            else:
                key = self.keyboard.get_keycode(keycode)
                if key:
                    log.info(f"Unknown combination: shift+{keycode}")
        # else:
        #     key = self.keyboard.get_keycode(keycode)
        #     log.info("Press: %s", key.name if key else keycode)

    def color_changed(self, color_selection):
        color = color_selection.get_current_rgba()
        rgb = [
            int(color.red * 255),
            int(color.green * 255),
            int(color.blue * 255),
        ]
        text = "".join("%0.2X" % i for i in rgb).lower()

        if self.current_key and self.current_key.color != text:
            log.info(f"New color for %r: #%s", self.current_key.name, text.upper())
            self.current_key.color = text
            self.image.queue_draw()
