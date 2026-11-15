
import threading


class MotorOrgan:
    def __init__(self, motor_neuron_count=0):
        self.motor_neurons = []
        self.motor_neuron_count = motor_neuron_count

        self.outputs = {}
        self.tokens = {}

        self.processing_delay = 0.2
        self.is_processing = False
        self.lock = threading.Lock()
        self.last_output = None
        self.output_count = 0

    def add_neuron(self, neuron):
        if neuron not in self.motor_neurons:
            self.motor_neurons.append(neuron)
            self.motor_neuron_count = len(self.motor_neurons)

    def receive(self, neuron, signal):
        with self.lock:
            self.outputs[neuron] = signal

            if (
                len(self.outputs) == len(self.motor_neurons)
                and not self.is_processing
            ):
                self.is_processing = True

                timer = threading.Timer(
                    self.processing_delay,
                    self.process
                )
                timer.daemon = True
                timer.start()

    def process(self):
        with self.lock:
            binary = "".join(
                self.outputs[neuron]
                for neuron in self.motor_neurons
            )

            output = self.tokens.get(binary, binary)

            self.last_output = output
            self.output_count += 1

            self.outputs.clear()
            self.is_processing = False

        print("Motor organ çıktısı:", output)
