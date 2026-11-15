
class Dendrid:
    def __init__(self, noron):
        self.noron = noron
        self.gelen_baglantilar = []
        self.bekleyen_etki_mv = 0.0
        self.bekleyen_katkilar = []

    def uyari_al(self, etki_mv, baglanti=None):
        self.bekleyen_etki_mv += etki_mv

        if baglanti is not None:
            self.bekleyen_katkilar.append(
                (baglanti, etki_mv)
            )

    def etkileri_al(self):
        etki = self.bekleyen_etki_mv
        katkilar = self.bekleyen_katkilar

        self.bekleyen_etki_mv = 0.0
        self.bekleyen_katkilar = []

        return etki, katkilar

    def etkiyi_al(self):
        etki, _ = self.etkileri_al()
        return etki

    def temizle(self):
        self.bekleyen_etki_mv = 0.0
        self.bekleyen_katkilar.clear()
