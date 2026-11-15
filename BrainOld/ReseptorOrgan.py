class ReseptorOrgan:
    def __init__(self):
        self.receptor_neurons = []

    def add_neuron(self, neuron):
        if neuron not in self.receptor_neurons:
            self.receptor_neurons.append(neuron)

    def receive(self, binary):
        from BrainOld.ActivationTrace import ActivationTrace

        required_length = sum(
            len(neuron.dendrits)
            for neuron in self.receptor_neurons
        )

        if len(binary) != required_length:
            raise ValueError(
                f"Beklenen girdi uzunluğu: {required_length}"
            )

        trace = ActivationTrace()

        index = 0

        for neuron in self.receptor_neurons:
            count = len(neuron.dendrits)
            neuron.receive(binary[index:index + count], trace)
            index += count

        return trace
