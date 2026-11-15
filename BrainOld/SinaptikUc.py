
from __future__ import annotations

import threading
import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from BrainOld.Dendrid import Dendrid


class SinaptikUc:
    def __init__(self, dendrit: Dendrid | None = None):
        self.dendrit = None
        self.strength = 0.5
        self.activation_delay = 0.02

        if dendrit is not None:
            self.connect(dendrit)

    def activate(
        self,
        trace=None,
        source_neuron=None,
        source_input=None,
        source_output=None
    ):
        if self.dendrit is None:
            source = getattr(self, "source_neuron", None)
            targets = getattr(self, "available_neurons", [])

            if source is None:
                return False

            possible_targets = [
                neuron for neuron in targets
                if neuron is not source
            ]

            random.shuffle(possible_targets)

            for target in possible_targets:
                available_dendrites = [
                    d for d in target.dendrits
                    if d.presinaps is None
                ]

                if not available_dendrites:
                    continue

                self.connect(random.choice(available_dendrites))
                self.strength = 0.5
                break

        if self.dendrit is None or self.strength == 0:
            return False

        if random.random() < self.strength:
            target = self.dendrit

            if trace is not None:
                accepted = trace.record(
                    source_neuron,
                    source_input,
                    source_output,
                    self,
                    target
                )

                if not accepted:
                    return False

            timer = threading.Timer(
                self.activation_delay,
                target.activate,
                args=(trace,)
            )
            timer.daemon = True
            timer.start()

            return True

        return False

    def connect(self, dendrit: Dendrid):
        if self.dendrit is dendrit:
            return

        self.disconnect()

        if dendrit.presinaps is not None:
            dendrit.presinaps.disconnect()

        self.dendrit = dendrit
        dendrit.presinaps = self

    def disconnect(self):
        if self.dendrit is not None:
            self.dendrit._remove_input(self)
            self.dendrit = None

    def strengthen(self, amount = 0.01):
        self.strength = round(min(1.0, self.strength + amount), 3)

    def weaken(self, amount = 0.01):
        self.strength = round(max(0.0, self.strength - amount), 3)

        if self.strength <= 0.0:
            self.disconnect()

    def is_have_sinaps(self):
        return self.dendrit is not None
