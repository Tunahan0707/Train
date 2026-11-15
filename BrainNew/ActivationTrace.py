
class ActivationTrace:
    def __init__(self):
        self.olaylar = []

    def aktarim_kaydet(self, zaman, kaynak, hedef, etki_mv):
        self.olaylar.append({
            "tur": "aktarim",
            "zaman": zaman,
            "kaynak": kaynak.noron,
            "hedef": hedef.noron,
            "etki_mv": etki_mv
        })

    def ateslenme_kaydet(self, zaman, noron):
        self.olaylar.append({
            "tur": "ateslenme",
            "zaman": zaman,
            "noron": noron
        })

    def temizle(self):
        self.olaylar.clear()
