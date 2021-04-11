import os
import sys


class BaseHandler:
    def __init__(self, model):
        self.model = model
        self.image_path = os.path.join(
            os.path.dirname(__file__), "..", "images", f"{model}.png"
        )
        self.bindings_path = os.path.join(
            os.path.dirname(__file__), "..", "bindings", f"{model}.json"
        )

    def color_changed(self, color_selection):
        pass

    def image_press(self, obj, button):
        pass

    def image_release(self, obj, button):
        pass

    def key_press(self, obj, button):
        pass

    @staticmethod
    def exit(event):
        sys.exit(1)
