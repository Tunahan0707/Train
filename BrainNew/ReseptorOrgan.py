
class ReseptorOrgan:
    def __init__(self, noronlar):
        self.noronlar = noronlar
        self.ciktilar = []

    def girdi_al(self, veri):
        veri = list(veri)

        if len(veri) != len(self.noronlar):
            raise ValueError("Girdi uzunluğu reseptör sayısıyla eşleşmiyor.")

        if any(bit not in (0, 1) for bit in veri):
            raise ValueError("Girdi yalnızca 0 ve 1 içerebilir.")

        self.ciktilar = veri

        for bit, noron in zip(veri, self.noronlar):
            if bit == 1:
                noron.dis_girdi_al(20.0)
