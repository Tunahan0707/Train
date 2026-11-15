import threading


class ActivationTrace:
    def __init__(self):
        self.records = []
        self.lock = threading.Lock()
        self.feedback_applied = False
        self.completed = False

    def record(
        self,
        source_neuron,
        source_input,
        source_output,
        terminal,
        target_dendrite
    ):
        with self.lock:
            if self.completed:
                return False

            target_neuron = target_dendrite.neuron

            self.records.append({
                "source_neuron": source_neuron,
                "source_input": source_input,
                "source_output": source_output,
                "terminal": terminal,
                "target_neuron": target_neuron,
                "target_dendrite": target_dendrite
            })

            if getattr(target_neuron, "is_motor_neuron", False):
                self.completed = True

            return True

    def feedback(self, amount=0.01, positive=True):
        with self.lock:
            if self.feedback_applied:
                return False
            self.feedback_applied = True
            records = list(reversed(self.records))

        for record in records:
            terminal = record["terminal"]

            if positive:
                terminal.strengthen(amount)
            else:
                terminal.weaken(amount)

        return True