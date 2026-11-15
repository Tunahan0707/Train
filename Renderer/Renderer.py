
from .Window import Window


class Renderer:

    def __init__(
        self,
        title="Renderer",
        width=800,
        height=600,
        x=100,
        y=100,
        resizable=True
    ):
        self.window = Window(
            title=title,
            width=width,
            height=height,
            x=x,
            y=y,
            resizable=resizable
        )

        self.is_running = False

    def open(self):
        self.window.open()

    def run(self):
        self.is_running = True
        self.window.run()
        self.is_running = False

    def close(self):
        pass
