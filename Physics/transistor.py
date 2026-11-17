class Transistor:
    def __init__(self):
        self.is_active = False
        self.is_get_energy = False

    def open(self):
        self.is_active = True

    def close(self):
        self.is_active = False

    def open_electricity(self):
        self.is_get_energy = True

    def close_electircity(self):
        self.is_get_energy = False

    def get_out(self):
        return self.is_get_energy and self.is_active