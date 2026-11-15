
from Baglanti import Baglanti


class AksonUcu:
    def __init__(self, noron):
        self.noron = noron
        self.baglantilar = []

    def baglan(self, hedef, etki_mv=2.0, gecikme_ms=1):
        baglanti = Baglanti(
            self,
            hedef,
            etki_mv,
            gecikme_ms
        )

        self.baglantilar.append(baglanti)
        hedef.gelen_baglantilar.append(baglanti)

        return baglanti
