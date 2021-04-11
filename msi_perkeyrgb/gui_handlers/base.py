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

    @staticmethod
    def exit(event):
        sys.exit(1)
