
import threading
import random

from BrainOld.Dendrid import Dendrid
from SinaptikUc import SinaptikUc


class ReseptorNoron:
    def __init__(self, organ, dendrit_count=2, terminal_count=2):
        self.organ = organ

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

    def receive(self, binary, trace):
        if len(binary) != len(self.dendrits):
            raise ValueError("Girdi uzunluğu dendrit sayısıyla eşleşmiyor.")

        with self.lock:
            if self.activation_trace is None:
                self.activation_trace = trace

            if not self.isactivated:
                self.isactivated = True

                self.timer = threading.Timer(
                    self.activation_delay,
                    self.process
                )

                self.timer.daemon = True
                self.timer.start()

        for index, bit in enumerate(binary):
            if bit == "1":
                self.dendrits[index].activate(trace)

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

        if binary not in self.memory:
            self.memory[binary] = "".join(
                random.choice("01")
                for _ in self.synaptic_terminals
            )

        self.decode(self.memory[binary], binary, trace)

    def decode(self, output, source_input, trace):
        for index, bit in enumerate(output):
            if bit == "1":
                self.synaptic_terminals[index].activate(
                    trace,
                    self,
                    source_input,
                    output
                )


