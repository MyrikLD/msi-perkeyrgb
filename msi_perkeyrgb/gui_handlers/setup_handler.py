import json
import logging
from json import JSONDecodeError

from key import Key

log = logging.getLogger(__name__)


class SetupHandler:
    box = [(0, 0), (0, 0)]

    def __init__(self, model, image):
        self.model = model
        self.image = image

        try:
            with open(f"bindings/{self.model}.json") as f:
                keys = json.load(f)
        except FileNotFoundError:
            log.warning("Config not found")
            keys = []
        except JSONDecodeError:
            log.error("Config error")
            keys = []

        self.image.set_from_file(f"images/{model}.png")

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

        with open(f"bindings/{self.model}.json", "w") as f:
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
