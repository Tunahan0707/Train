import math


class Dendrid:
    """İşaretli girdiyi toplar ve yerel sinapslara dağıtır."""

    def __init__(self, kimlik, konum=(0.0, 0.0), sinyal_olcegi=10.0):
        if sinyal_olcegi <= 0:
            raise ValueError("Sinyal ölçeği pozitif olmalı.")
        self.kimlik = kimlik
        self.konum = tuple(konum)
        self.sinyal_olcegi = float(sinyal_olcegi)
        self.sinaps_katkilari = {}
        self.girdiler = []
        self.reseptor_duyarliliklari = {}
        self.son_islenen_sinapslar = set()

    def sinaps_bagla(self, sinaps, katki):
        self.sinaps_katkilari[sinaps] = float(katki)

    def transmitter_duyarliligi_ayarla(self, tur, duyarlilik):
        self.reseptor_duyarliliklari[tur] = float(duyarlilik)

    def kimyasal_yanit(self, kimyasal_alan, zaman):
        toplam = 0.0
        for tur, duyarlilik in self.reseptor_duyarliliklari.items():
            yogunluk = kimyasal_alan.yogunluk(tur, self.konum, zaman)
            toplam += duyarlilik * (yogunluk / (1.0 + yogunluk))
        return toplam

    def girdi_al(self, etki):
        self.girdiler.append(float(etki))

    def sinyali_isle(self, zaman, kimyasal_alan=None):
        self.son_islenen_sinapslar.clear()
        if not self.girdiler:
            return 0.0

        elektriksel_toplam = sum(self.girdiler)
        self.girdiler.clear()

        kimyasal_modulasyon = 0.0
        if kimyasal_alan is not None and self.reseptor_duyarliliklari:
            kimyasal_modulasyon = self.kimyasal_yanit(kimyasal_alan, zaman)

        u = math.tanh(
            elektriksel_toplam / self.sinyal_olcegi + kimyasal_modulasyon
        )
        adet = len(self.sinaps_katkilari)
        if adet and u != 0.0:
            normalizasyon = math.sqrt(max(1, adet))
            for sinaps, katki in self.sinaps_katkilari.items():
                sinaps.etki_uygula((katki * u) / normalizasyon, zaman)
                self.son_islenen_sinapslar.add(sinaps)
        return elektriksel_toplam

    def firsat_sonucu_ogren(self, aktif_sinapslar, zaman, adim=0.01):
        """Yalnızca bu olayda gerçekten katkı yüklenen çiftleri günceller."""
        for sinaps in self.son_islenen_sinapslar:
            if sinaps in aktif_sinapslar:
                self.sinaps_katkilari[sinaps] += adim
            elif sinaps.degerlendirme_sayisi > 0:
                self.sinaps_katkilari[sinaps] -= adim
        self.son_islenen_sinapslar.clear()
