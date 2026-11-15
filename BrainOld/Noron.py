
from __future__ import annotations

import threading
import random

from BrainOld.Dendrid import Dendrid
from SinaptikUc import SinaptikUc


class Noron:
    def __init__(self, dendrit_count, terminal_count):
        self.dendrits = [
            Dendrid(self) for _ in range(dendrit_count)
        ]

        self.synaptic_terminals = [
            SinaptikUc() for _ in range(terminal_count)
        ]

        self.memory = {}

        self.isactivated = False
        self.activation_delay = 0.5

        self.lock = threading.Lock()
        self.timer = None
        self.activation_trace = None

    def activate_dendrite(self, dendrit, trace=None):
        with self.lock:
            dendrit.isactive = 1

            if self.activation_trace is None and trace is not None:
                self.activation_trace = trace

            if self.isactivated:
                return

            self.isactivated = True

            self.timer = threading.Timer(
                self.activation_delay,
                self.process
            )

            self.timer.daemon = True
            self.timer.start()

    def process(self):
        with self.lock:
            binary = "".join(
                str(d.isactive) for d in self.dendrits
            )

            for d in self.dendrits:
                d.isactive = 0

            trace = self.activation_trace
            self.activation_trace = None

            self.isactivated = False
            self.timer = None

        output = self.get_memory(binary)
        self.decode(output, binary, trace)

    def get_memory(self, binary):
        if binary not in self.memory:
            self.memory[binary] = "".join(
                random.choice("01")
                for _ in self.synaptic_terminals
            )

        return self.memory[binary]

    def decode(self, output, source_input, trace):
        for index, bit in enumerate(output):
            if bit == "1":
                terminal = self.synaptic_terminals[index]
                terminal.strengthen()

                terminal.activate(
                    trace,
                    self,
                    source_input,
                    output
                )
