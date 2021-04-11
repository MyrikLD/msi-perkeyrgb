import json
import logging
import os
from json import JSONDecodeError

from msi_perkeyrgb.key import Key
from .base import BaseHandler

log = logging.getLogger(__name__)


class SetupHandler(BaseHandler):
    box = [(0, 0), (0, 0)]

    def __init__(self, model, image):
        super().__init__(model)
        self.image = image

        try:

            with open(
                os.path.join(
                    os.path.dirname(__file__), "..", "bindings", f"{model}.json"
                )
            ) as f:
                keys = json.load(f)
        except FileNotFoundError:
            log.warning("Config not found")
            keys = []
        except JSONDecodeError:
            log.error("Config error")
            keys = []

        self.image.set_from_file(self.image_path)

        self.keys = sorted(
            {Key(**i) for i in keys},
            key=lambda x: x.keycode,
        )

    def image_press(self, obj, button):
        if button.button == 1:
            self.box[0] = (button.x, button.y)
        elif button.button == 3:
            print(self.keys)

    def image_release(self, obj, button):
        if button.button == 1:
            self.box[1] = (button.x, button.y)
            print(self.box)

    def key_press(self, obj, button):
        keycode = button.hardware_keycode
        name = button.string
        key = Key(box=(self.box[0], self.box[1]), keycode=keycode, name=name)

        print(key)
        self.keys.append(key)

        with open(self.bindings_path, "w") as f:
            json.dump(
                sorted((i.dict() for i in set(self.keys)), key=lambda x: x["keycode"]),
                f,
                indent=2,
            )

    def color_changed(self, color_selection):
        pass

    @staticmethod
    def exit(event):
        exit(1)
