
from __future__ import annotations

import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SinaptikUc import SinaptikUc


class Dendrid:
    def __init__(self, neuron):
        self.neuron = neuron
        self.isactive = 0
        self.presinaps: SinaptikUc | None = None
        self.activation_delay = 0.02

    def activate(self, trace=None):
        timer = threading.Timer(
            self.activation_delay,
            self.neuron.activate_dendrite,
            args=(self, trace)
        )
        timer.daemon = True
        timer.start()

    def deactive(self):
        with self.neuron.lock:
            self.isactive = 0

    def sinaps(self, other: SinaptikUc):
        other.connect(self)

    def desinaps(self):
        if self.presinaps is not None:
            self.presinaps.disconnect()

    def is_have_sinaps(self):
        return self.presinaps is not None

    def get_neuron(self):
        return self.neuron

    def _remove_input(self, terminal: SinaptikUc):
        if self.presinaps is terminal:
            self.presinaps = None
