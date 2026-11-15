
class MotorOrgan:
    def __init__(self, noron_sayisi):
        self.ciktilar = [0] * noron_sayisi

    def noron_ateslendi(self, indeks):
        self.ciktilar[indeks] = 1

    def reset(self):
        self.ciktilar = [0] * len(self.ciktilar)
